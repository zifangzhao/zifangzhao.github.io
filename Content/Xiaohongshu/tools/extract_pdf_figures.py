from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
from pypdf import PdfReader


BASE_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = BASE_DIR.parents[1]
MIN_AREA = 45_000
MIN_SIDE = 90
MAX_CANDIDATES = 16


@dataclass
class Candidate:
    page: int
    index: int
    width: int
    height: int
    area: int
    source_name: str
    path: Path


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf"),
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
    ]:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def parse_source_pdf(paper_dir: Path, readme: str) -> Path | None:
    match = re.search(r"Source PDF:\s*`([^`]+)`", readme)
    if not match:
        return None
    source = (paper_dir / match.group(1)).resolve()
    return source if source.exists() else None


def image_fingerprint(image: Image.Image) -> str:
    normalized = ImageOps.exif_transpose(image.convert("RGB")).resize((64, 64))
    return hashlib.sha256(normalized.tobytes()).hexdigest()


def safe_rgb(image: Image.Image) -> Image.Image:
    image = ImageOps.exif_transpose(image)
    if image.mode in {"RGBA", "LA", "P"}:
        background = Image.new("RGB", image.size, "white")
        if image.mode == "P":
            image = image.convert("RGBA")
        alpha = image.getchannel("A") if "A" in image.getbands() else None
        background.paste(image.convert("RGB"), mask=alpha)
        return background
    return image.convert("RGB")


def clean_old_outputs(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*"):
        if old.is_file() and old.suffix.lower() in {".jpg", ".png", ".txt"}:
            old.unlink()


def extract_candidates(paper_dir: Path, pdf_path: Path) -> list[Candidate]:
    out_dir = paper_dir / "extracted_figures"
    clean_old_outputs(out_dir)
    reader = PdfReader(str(pdf_path))
    raw: list[tuple[Candidate, str]] = []
    seen_per_hash: dict[str, int] = {}

    for page_index, page in enumerate(reader.pages, start=1):
        for image_index, image_file in enumerate(page.images, start=1):
            try:
                image = safe_rgb(image_file.image)
            except Exception:
                continue
            width, height = image.size
            area = width * height
            if area < MIN_AREA or min(width, height) < MIN_SIDE:
                continue
            fingerprint = image_fingerprint(image)
            seen_per_hash[fingerprint] = seen_per_hash.get(fingerprint, 0) + 1
            filename = f"p{page_index:02d}_i{image_index:03d}_{width}x{height}.jpg"
            path = out_dir / filename
            candidate = Candidate(
                page=page_index,
                index=image_index,
                width=width,
                height=height,
                area=area,
                source_name=image_file.name,
                path=path,
            )
            raw.append((candidate, fingerprint))

    unique: list[Candidate] = []
    used_hashes: set[str] = set()
    for candidate, fingerprint in sorted(raw, key=lambda item: item[0].area, reverse=True):
        if fingerprint in used_hashes:
            continue
        # Repeated large images across many pages are usually journal headers/footers.
        if seen_per_hash.get(fingerprint, 0) >= 3:
            continue
        used_hashes.add(fingerprint)
        unique.append(candidate)

    selected = sorted(unique[:MAX_CANDIDATES], key=lambda candidate: (candidate.page, candidate.index))
    for candidate in selected:
        page = reader.pages[candidate.page - 1]
        image_file = page.images[candidate.index - 1]
        safe_rgb(image_file.image).save(candidate.path, quality=94, optimize=True, subsampling=1)

    manifest = out_dir / "manifest.txt"
    manifest.write_text(
        "\n".join(
            [
                f"{item.path.name}\tpage={item.page}\timage={item.index}\tsize={item.width}x{item.height}\tarea={item.area}\tsource={item.source_name}"
                for item in selected
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return selected


def make_contact_sheet(paper_dir: Path, candidates: list[Candidate]) -> Path | None:
    if not candidates:
        return None
    out_dir = paper_dir / "extracted_figures"
    thumb_w, thumb_h = 360, 250
    label_h = 74
    gap = 24
    cols = 2
    rows = (len(candidates) + cols - 1) // cols
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * (thumb_h + label_h) + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), "#f8f6f2")
    draw = ImageDraw.Draw(sheet)
    label_font = font(24)
    small_font = font(19)

    for idx, candidate in enumerate(candidates):
        row = idx // cols
        col = idx % cols
        x = gap + col * (thumb_w + gap)
        y = gap + row * (thumb_h + label_h + gap)
        image = Image.open(candidate.path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        frame = Image.new("RGB", (thumb_w, thumb_h), "white")
        frame.paste(image, ((thumb_w - image.width) // 2, (thumb_h - image.height) // 2))
        sheet.paste(frame, (x, y))
        draw.rectangle((x, y, x + thumb_w, y + thumb_h), outline="#d7d0c8", width=2)
        draw.text((x, y + thumb_h + 10), f"{idx + 1}. page {candidate.page}, image {candidate.index}", font=label_font, fill="#8a1538")
        draw.text((x, y + thumb_h + 40), f"{candidate.width} x {candidate.height}", font=small_font, fill="#58606a")

    path = out_dir / "contact_sheet.jpg"
    sheet.save(path, quality=92, optimize=True, subsampling=1)
    return path


def write_readme(paper_dir: Path, pdf_path: Path, candidates: list[Candidate], contact_sheet: Path | None) -> None:
    out_dir = paper_dir / "extracted_figures"
    lines = [
        "# Extracted Figure Candidates",
        "",
        f"Source PDF: `{pdf_path.relative_to(REPO_DIR).as_posix()}`",
        "",
        "These are de-duplicated, large embedded image objects extracted from the PDF. They are figure candidates, not guaranteed final figure crops. Use `contact_sheet.jpg` to choose which panels belong in the Xiaohongshu carousel/video.",
        "",
    ]
    if contact_sheet:
        lines.extend(["## Contact Sheet", "", f"- `{contact_sheet.relative_to(paper_dir).as_posix()}`", ""])
    lines.extend(["## Candidates", ""])
    for idx, item in enumerate(candidates, start=1):
        lines.append(
            f"{idx}. `{item.path.relative_to(paper_dir).as_posix()}` - page {item.page}, image {item.index}, {item.width}x{item.height}"
        )
    lines.append("")
    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    for paper_dir in sorted(BASE_DIR.iterdir()):
        if not paper_dir.is_dir() or paper_dir.name == "tools":
            continue
        readme_path = paper_dir / "README.md"
        if not readme_path.exists():
            continue
        pdf_path = parse_source_pdf(paper_dir, readme_path.read_text(encoding="utf-8"))
        if not pdf_path:
            print(f"SKIP {paper_dir.name}: no source pdf")
            continue
        candidates = extract_candidates(paper_dir, pdf_path)
        contact_sheet = make_contact_sheet(paper_dir, candidates)
        write_readme(paper_dir, pdf_path, candidates, contact_sheet)
        print(f"DONE {paper_dir.name}: {len(candidates)} figure candidates")


if __name__ == "__main__":
    main()
