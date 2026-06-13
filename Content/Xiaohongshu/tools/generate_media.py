from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parents[1]
WIDTH = 1080
HEIGHT = 1440

FONT_CANDIDATES = {
    "regular": [
        Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf"),
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\Deng.ttf"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
    ],
    "bold": [
        Path(r"C:\Windows\Fonts\msyhbd.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
        Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf"),
    ],
}

PAPER_LABELS = {
    "2021-pnas-responsive-neuroelectronics": "闭环植入式神经接口",
    "2022-sciadv-ionic-communication": "植入式设备的离子通信",
    "2022-advanced-science-single-neuron-interface": "脑表面单神经元记录",
    "2023-nature-materials-vigt-bioelectronics": "全有机独立生物电子",
    "2024-advanced-science-aci-epidermal-emg": "高分辨率表皮肌电",
    "2026-nature-sensors-event-based-neurostimulation": "事件驱动闭环神经刺激",
    "2026-wild-datalogger-manuscript": "自由行为无线神经记录",
}

CURATED_FIGURE_ORDER = {
    "2021-pnas-responsive-neuroelectronics": [
        "p05_i001_885x577.jpg",
        "p04_i001_496x637.jpg",
        "p06_i053_440x122.jpg",
        "p07_i001_461x190.jpg",
        "p07_i002_368x190.jpg",
    ],
    "2022-sciadv-ionic-communication": [
        "p03_i001_1501x953.jpg",
        "p06_i006_508x465.jpg",
        "p07_i001_1396x726.jpg",
        "p03_i001_1501x953.jpg",
        "p07_i001_1396x726.jpg",
    ],
    "2022-advanced-science-single-neuron-interface": [
        "p04_i002_1986x752.jpg",
        "p03_i002_1500x453.jpg",
        "p05_i001_554x448.jpg",
        "p04_i002_1986x752.jpg",
    ],
    "2023-nature-materials-vigt-bioelectronics": [
        "p02_i001_685x227.jpg",
        "p02_i003_246x225.jpg",
        "p05_i001_812x577.jpg",
        "p07_i001_632x538.jpg",
        "p07_i002_780x372.jpg",
    ],
    "2024-advanced-science-aci-epidermal-emg": [
        "p03_i002_2050x1370.jpg",
        "p04_i002_1499x1405.jpg",
        "p05_i003_2050x841.jpg",
        "p06_i002_2050x1117.jpg",
        "p05_i002_2047x634.jpg",
    ],
    "2026-nature-sensors-event-based-neurostimulation": [
        "p05_i001_297x297.jpg",
        "p05_i004_427x413.jpg",
        "p06_i001_387x387.jpg",
        "p06_i002_387x194.jpg",
        "p19_i001_422x422.jpg",
    ],
    "2026-wild-datalogger-manuscript": [
        "p03_i001_1634x629.jpg",
        "p05_i001_1946x1090.jpg",
        "p07_i001_2581x1380.jpg",
        "p08_i001_2572x1450.jpg",
        "p13_i001_2048x1152.jpg",
    ],
}

VISUAL_TRANSLATIONS = {
    "Hero figure or device overview.": "论文主图或设备总览图",
    "Figure showing device architecture or channel/electronics layout.": "设备架构图，或通道与电子系统布局图",
    "Multiplex-then-amplify schematic.": "先复用、再放大的 MTA 架构示意图",
    "Recording, processing, stimulation, or onboard workflow figure.": "记录、处理、刺激或板载闭环流程图",
    "Main epilepsy/network intervention result.": "癫痫样活动或脑网络干预的核心结果图",
    "Implant/tissue/data transmission schematic.": "植入设备、组织介质与数据传输示意图",
    "Comparison or introduction figure.": "通信方式对比图或论文引入图",
    "Ionic communication mechanism figure.": "离子通信工作机制图",
    "Propagation radius/depth or parallel communication figure.": "传播半径、深度调控或并行通信结果图",
    "Implanted device and neural recording result.": "植入式设备与神经记录结果图",
    "Device on cortical surface or clinical interface overview.": "贴合脑表面的器件或临床接口总览图",
    "Organic/conformable neural interface device figure.": "有机柔性神经接口器件图",
    "Spike waveforms/clustering/single-unit figure.": "动作电位波形、聚类或单神经元结果图",
    "Phase modulation, population coupling, or microcircuit interaction figure.": "相位调制、群体耦合或微电路相互作用结果图",
    "Summary or clinical translation figure.": "总结图或临床转化意义图",
    "Stand-alone conformable device overview.": "独立贴合式有机设备总览图",
    "vIGT architecture figure.": "vIGT 器件结构图",
    "Circuit or array performance figure.": "集成电路或阵列性能结果图",
    "AC-powered conformable circuitry or wireless communication figure.": "交流供电贴合电路或无线通信结果图",
    "Implanted freely moving rodent result.": "自由活动啮齿动物植入实验结果图",
    "Dense epidermal electrode array on skin.": "皮肤表面的高密度表皮电极阵列图",
    "Paste/crosstalk schematic or comparison.": "导电膏横向串扰示意图或对比图",
    "Anisotropic conducting interlayer design.": "各向异性导电界面材料设计图",
    "High-density EMG spatial profile result.": "高密度肌电空间分布结果图",
    "Multi-species validation panels.": "小鼠、非人灵长类和人类验证图",
    "Event-based sensor concept.": "事件驱动传感器概念图",
    "Silicon versus organic interface comparison.": "硅基接口与有机接口对比图",
    "OECN device and pulse response figure.": "OECN 器件与脉冲响应结果图",
    "Energy/speed benchmark figure.": "能耗与速度性能对比图",
    "IED detection and in vivo stimulation result.": "癫痫样放电检测与体内刺激结果图",
    "Freely moving mouse with WILD device.": "佩戴 WILD 设备的自由活动小鼠图",
    "Constraint comparison: tethered, wireless, multimodal.": "有线、无线与多模态设备限制对比图",
    "Device architecture or module overview.": "设备架构或模块组成总览图",
    "Multimodal data panels.": "神经、运动、声音和视频多模态数据图",
    "Onboard processing and closed-loop trigger result.": "板载实时处理与闭环触发结果图",
}


@dataclass
class Slide:
    number: int
    title: str
    visual: str
    copy: str
    takeaway: str


@dataclass(frozen=True)
class FigureAsset:
    path: Path
    crop: tuple[float, float, float, float] | None = None


SLIDE_TITLE_OVERRIDES = {
    ("2026-wild-datalogger-manuscript", 3): "WILD：无线轻量多模态平台",
}


SLIDE_FIGURE_OVERRIDES = {
    "2021-pnas-responsive-neuroelectronics": [
        {"filename": "p05_i001_885x577.jpg"},
        {"filename": "p04_i001_496x637.jpg", "crop": (0.00, 0.00, 0.55, 0.46)},
        {"filename": "p05_i001_885x577.jpg", "crop": (0.15, 0.00, 0.52, 0.58)},
        {"filename": "p07_i001_461x190.jpg"},
        {"filename": "p07_i002_368x190.jpg"},
    ],
    "2026-wild-datalogger-manuscript": [
        {"filename": "p03_i001_1634x629.jpg"},
        {"filename": "p05_i001_1946x1090.jpg", "crop": (0.78, 0.04, 0.98, 0.48)},
        {"filename": "p05_i001_1946x1090.jpg", "crop": (0.00, 0.00, 0.50, 0.44)},
        {"filename": "p07_i001_2581x1380.jpg"},
        {"filename": "p13_i001_2048x1152.jpg"},
    ],
}


def choose_font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    for candidate in FONT_CANDIDATES[kind]:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> float:
    return draw.textlength(text, font=font)


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
    max_lines: int | None = None,
) -> list[str]:
    lines: list[str] = []
    for paragraph in re.split(r"\n+", text.strip()):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        line = ""
        for char in paragraph:
            candidate = line + char
            if text_width(draw, candidate, font) <= max_width or not line:
                line = candidate
            else:
                lines.append(line)
                line = char
                if max_lines and len(lines) >= max_lines:
                    break
        if line and (not max_lines or len(lines) < max_lines):
            lines.append(line)
        if max_lines and len(lines) >= max_lines:
            break
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    font: ImageFont.ImageFont,
    fill: str,
    max_width: int,
    line_gap: int,
    max_lines: int | None = None,
) -> int:
    x, y = xy
    lines = wrap_text(draw, text, font, max_width=max_width, max_lines=max_lines)
    bbox = draw.textbbox((0, 0), "国", font=font)
    line_height = bbox[3] - bbox[1]
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height + line_gap
    return y


def text_line_height(draw: ImageDraw.ImageDraw, font: ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), "Ag", font=font)
    return bbox[3] - bbox[1]


def fit_wrapped_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    kind: str,
    start_size: int,
    min_size: int,
    max_width: int,
    max_lines: int,
) -> tuple[ImageFont.ImageFont, list[str]]:
    for size in range(start_size, min_size - 1, -2):
        font = choose_font(kind, size)
        lines = wrap_text(draw, text, font, max_width=max_width)
        if len(lines) <= max_lines:
            return font, lines
    font = choose_font(kind, min_size)
    return font, wrap_text(draw, text, font, max_width=max_width, max_lines=max_lines)


def draw_lines(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    xy: tuple[int, int],
    font: ImageFont.ImageFont,
    fill: str,
    line_gap: int,
) -> int:
    x, y = xy
    line_height = text_line_height(draw, font)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height + line_gap
    return y


def parse_section(markdown: str, start: str, end: str | None = None) -> str:
    start_match = re.search(re.escape(start), markdown)
    if not start_match:
        return ""
    start_index = start_match.end()
    if end:
        end_match = re.search(re.escape(end), markdown[start_index:])
        if end_match:
            return markdown[start_index : start_index + end_match.start()]
    return markdown[start_index:]


def parse_slides(markdown: str) -> list[Slide]:
    section = parse_section(
        markdown,
        "## 4-5 Page Xiaohongshu Carousel",
        "## 60-90 Second Dubbed Video Script",
    )
    chunks = re.split(r"\n### Page\s+(\d+)[^\n]*\n", section)
    slides: list[Slide] = []
    for i in range(1, len(chunks), 2):
        number = int(chunks[i])
        body = chunks[i + 1]
        title = parse_field(body, "Title")
        visual = parse_field(body, "Visual")
        copy = parse_field(body, "Copy")
        takeaway = parse_field(body, "Takeaway")
        if title and copy and takeaway:
            slides.append(
                Slide(
                    number=number,
                    title=title,
                    visual=visual,
                    copy=copy,
                    takeaway=takeaway,
                )
            )
    return slides


def parse_field(text: str, field: str) -> str:
    match = re.search(rf"^{re.escape(field)}:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def parse_named_section(markdown: str, heading: str, next_heading: str | None = None) -> str:
    return parse_section(markdown, f"## {heading}", f"## {next_heading}" if next_heading else None).strip()


def slide_seconds_for_count(count: int) -> int:
    if count <= 0:
        return 7
    return max(6, min(9, round(40 / count)))


def clean_for_upload_text(text: str) -> str:
    replacements = {
        "Visual:": "图位：",
        "Copy:": "正文：",
        "Takeaway:": "重点：",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def translate_visual(text: str) -> str:
    return VISUAL_TRANSLATIONS.get(text, text)


def make_gradient() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), "#fffaf4")
    pixels = img.load()
    top = (255, 250, 244)
    bottom = (244, 248, 249)
    for y in range(HEIGHT):
        ratio = y / (HEIGHT - 1)
        color = tuple(int(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        for x in range(WIDTH):
            pixels[x, y] = color
    return img


def crop_to_content(image: Image.Image, threshold: int = 245, padding: int = 18) -> Image.Image:
    rgb = image.convert("RGB")
    gray = rgb.convert("L")
    mask = gray.point(lambda value: 255 if value < threshold else 0)
    bbox = mask.getbbox()
    if not bbox:
        return rgb
    left, top, right, bottom = bbox
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(rgb.width, right + padding)
    bottom = min(rgb.height, bottom + padding)
    cropped = rgb.crop((left, top, right, bottom))
    # Avoid over-cropping line plots with pale backgrounds.
    if cropped.width < rgb.width * 0.25 or cropped.height < rgb.height * 0.25:
        return rgb
    return cropped


def resize_to_fit(image: Image.Image, max_width: int, max_height: int, max_upscale: float = 3.0) -> Image.Image:
    scale = min(max_width / image.width, max_height / image.height, max_upscale)
    new_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def resize_to_cover(image: Image.Image, width: int, height: int, max_upscale: float = 6.0) -> Image.Image:
    scale = max(width / image.width, height / image.height)
    scale = min(scale, max_upscale)
    resized = image.resize((max(1, int(image.width * scale)), max(1, int(image.height * scale))), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - width) // 2)
    top = max(0, (resized.height - height) // 2)
    return resized.crop((left, top, left + width, top + height))


def crop_relative(image: Image.Image, crop: tuple[float, float, float, float]) -> Image.Image:
    left, top, right, bottom = crop
    width, height = image.size
    box = (
        max(0, min(width - 1, int(width * left))),
        max(0, min(height - 1, int(height * top))),
        max(1, min(width, int(width * right))),
        max(1, min(height, int(height * bottom))),
    )
    if box[2] <= box[0] or box[3] <= box[1]:
        return image
    return image.crop(box)


def load_figure_candidates(paper_dir: Path, count: int = 5) -> list[Path]:
    manifest = paper_dir / "extracted_figures" / "manifest.txt"
    if not manifest.exists():
        return []
    curated = CURATED_FIGURE_ORDER.get(paper_dir.name)
    if curated:
        curated_paths = [paper_dir / "extracted_figures" / name for name in curated]
        curated_paths = [path for path in curated_paths if path.exists()]
        if curated_paths:
            return curated_paths[:count]
    candidates: list[tuple[int, int, int, Path]] = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        filename = parts[0]
        page = 999
        index = 999
        area = 0
        for part in parts[1:]:
            if part.startswith("page="):
                page = int(part.split("=", 1)[1])
            elif part.startswith("image="):
                index = int(part.split("=", 1)[1])
            elif part.startswith("area="):
                area = int(part.split("=", 1)[1])
        path = paper_dir / "extracted_figures" / filename
        if path.exists():
            candidates.append((area, page, index, path))
    largest = sorted(candidates, key=lambda item: item[0], reverse=True)[: max(count, 1)]
    return [item[3] for item in largest]


def load_figure_assets(paper_dir: Path, count: int = 5) -> list[FigureAsset]:
    overrides = SLIDE_FIGURE_OVERRIDES.get(paper_dir.name)
    if overrides:
        assets: list[FigureAsset] = []
        for spec in overrides[:count]:
            path = paper_dir / "extracted_figures" / spec["filename"]
            if path.exists():
                assets.append(FigureAsset(path=path, crop=spec.get("crop")))
        if assets:
            return assets
    return [FigureAsset(path=path) for path in load_figure_candidates(paper_dir, count=count)]


def draw_slide(paper_dir: Path, label: str, slide: Slide, total: int, figure_asset: FigureAsset | None) -> Path:
    out_dir = paper_dir / "jpg"
    out_dir.mkdir(exist_ok=True)
    img = make_gradient()
    draw = ImageDraw.Draw(img)

    font_brand = choose_font("bold", 30)
    font_kicker = choose_font("regular", 28)
    font_body = choose_font("regular", 30)
    font_takeaway = choose_font("bold", 32)
    font_slot = choose_font("regular", 30)
    font_footer = choose_font("regular", 24)

    ink = "#1d1f22"
    muted = "#58606a"
    accent = "#8a1538"
    accent_soft = "#f4e8dd"
    line = "#ded7cf"

    margin = 52
    draw.rounded_rectangle((margin, 34, WIDTH - margin, 88), radius=18, fill="#ffffff", outline=line)
    draw.text((margin + 24, 47), "神经接口科普", font=font_brand, fill=accent)
    page_text = f"第 {slide.number} / {total} 页"
    draw.text((WIDTH - margin - text_width(draw, page_text, font_kicker) - 24, 50), page_text, font=font_kicker, fill=muted)

    y = 116
    y = draw_wrapped(draw, label, (margin, y), font_kicker, accent, WIDTH - 2 * margin, 6, max_lines=1)
    y += 10
    title_text = SLIDE_TITLE_OVERRIDES.get((paper_dir.name, slide.number), slide.title)
    font_title, title_lines = fit_wrapped_font(draw, title_text, "bold", 42, 32, WIDTH - 2 * margin, 2)
    y = draw_lines(draw, title_lines, (margin, y), font_title, ink, 8)

    slot_top = max(238, y + 18)
    prepared_figure = None
    cover_mode = False
    if figure_asset and figure_asset.path.exists():
        raw_figure = crop_to_content(Image.open(figure_asset.path).convert("RGB"))
        if figure_asset.crop:
            raw_figure = crop_to_content(crop_relative(raw_figure, figure_asset.crop), padding=10)
        raw_aspect = raw_figure.width / max(raw_figure.height, 1)
        if raw_aspect > 2.2:
            cover_mode = True
            prepared_figure = resize_to_cover(raw_figure, WIDTH - 2 * margin - 66, 500)
        else:
            prepared_figure = resize_to_fit(raw_figure, WIDTH - 2 * margin - 66, 778)
    slot_height = 760
    if prepared_figure is not None:
        if cover_mode:
            slot_height = 580
        else:
            slot_height = max(700, min(822, prepared_figure.height + 78))
    slot_bottom = slot_top + slot_height
    draw.rounded_rectangle((margin, slot_top, WIDTH - margin, slot_bottom), radius=20, fill="#ffffff", outline=line, width=2)
    inner_box = (margin + 18, slot_top + 18, WIDTH - margin - 18, slot_bottom - 18)
    draw.rounded_rectangle(inner_box, radius=18, fill="#ffffff")
    if prepared_figure is not None and figure_asset:
        figure = prepared_figure
        fig_x = inner_box[0] + (inner_box[2] - inner_box[0] - figure.width) // 2
        fig_y = inner_box[1] + (inner_box[3] - inner_box[1] - figure.height) // 2 - 10
        fig_y = max(inner_box[1] + 10, fig_y)
        draw.rounded_rectangle((fig_x - 8, fig_y - 8, fig_x + figure.width + 8, fig_y + figure.height + 8), radius=14, fill="#ffffff")
        img.paste(figure, (fig_x, fig_y))
        draw.text((margin + 30, slot_bottom - 38), "图源：原论文图版裁切", font=font_footer, fill=muted)
    else:
        draw.text((margin + 48, slot_top + 58), "主图位置", font=font_takeaway, fill=accent)
        draw_wrapped(
            draw,
            f"建议放入：{translate_visual(slide.visual)}",
            (margin + 48, slot_top + 128),
            font_slot,
            ink,
            WIDTH - 2 * margin - 96,
            8,
            max_lines=4,
        )
        draw_wrapped(
            draw,
            "导出论文中的对应图版后，替换这个区域。",
            (margin + 48, slot_bottom - 82),
            font_footer,
            muted,
            WIDTH - 2 * margin - 96,
            4,
            max_lines=2,
        )

    body_top = slot_bottom + 30
    draw.text((margin, body_top), "证据解读", font=font_footer, fill=accent)
    body_lines = 3 if slot_bottom > 980 else 5
    body_end = draw_wrapped(draw, slide.copy, (margin, body_top + 34), font_body, ink, WIDTH - 2 * margin, 6, max_lines=body_lines)

    takeaway_top = max(body_end + 22, HEIGHT - 214)
    draw.rounded_rectangle((margin, takeaway_top, WIDTH - margin, HEIGHT - 58), radius=20, fill="#8a1538")
    draw.text((margin + 28, takeaway_top + 22), "核心结论", font=font_footer, fill="#ffe8d4")
    draw_wrapped(
        draw,
        slide.takeaway,
        (margin + 28, takeaway_top + 62),
        font_takeaway,
        "#ffffff",
        WIDTH - 2 * margin - 56,
        6,
        max_lines=2,
    )

    out_path = out_dir / f"{slide.number:02d}.jpg"
    img.save(out_path, quality=94, optimize=True, subsampling=1)
    return out_path


def clear_generated_jpgs(paper_dir: Path) -> None:
    out_dir = paper_dir / "jpg"
    out_dir.mkdir(exist_ok=True)
    for old in out_dir.glob("*.jpg"):
        try:
            old.unlink()
        except PermissionError:
            continue


def format_time(seconds: float) -> str:
    whole = int(seconds)
    millis = int(round((seconds - whole) * 1000))
    h = whole // 3600
    m = (whole % 3600) // 60
    s = whole % 60
    return f"{h:02d}:{m:02d}:{s:02d},{millis:03d}"


def write_subtitles(paper_dir: Path, slides: list[Slide], slide_seconds: int) -> Path:
    video_dir = paper_dir / "video"
    video_dir.mkdir(exist_ok=True)
    lines: list[str] = []
    for idx, slide in enumerate(slides, start=1):
        start = (idx - 1) * slide_seconds
        end = idx * slide_seconds - 0.2
        lines.extend(
            [
                str(idx),
                f"{format_time(start)} --> {format_time(end)}",
                f"{slide.title}",
                f"{slide.takeaway}",
                "",
            ]
        )
    srt = video_dir / "subtitles.srt"
    srt.write_text("\n".join(lines), encoding="utf-8")
    return srt


def write_video_notes(paper_dir: Path, slides: list[Slide], slide_seconds: int) -> Path:
    video_dir = paper_dir / "video"
    video_dir.mkdir(exist_ok=True)
    notes = [
        "# 竖屏短视频说明",
        "",
        f"- 时长：约 {len(slides) * slide_seconds} 秒",
        "- 画幅：1080 x 1440 JPG 轮播图合成",
        "- 当前版本：无配音，可直接用作节奏预览；配音可使用父目录 README 的脚本录制。",
        "- 字幕：`subtitles.srt`",
        "- 视频：`short_video.mp4`",
        "",
        "## 每页节奏",
        "",
    ]
    for slide in slides:
        notes.append(f"{slide.number}. {slide.title} - {slide.takeaway}")
    path = video_dir / "README.md"
    path.write_text("\n".join(notes) + "\n", encoding="utf-8")
    return path


def make_video(paper_dir: Path, jpg_paths: list[Path], slide_seconds: int) -> Path | None:
    video_dir = paper_dir / "video"
    video_dir.mkdir(exist_ok=True)
    concat = video_dir / "concat.txt"
    entries: list[str] = []
    for path in jpg_paths:
        safe = path.resolve().as_posix().replace("'", r"'\''")
        entries.append(f"file '{safe}'")
        entries.append(f"duration {slide_seconds}")
    safe_last = jpg_paths[-1].resolve().as_posix().replace("'", r"'\''")
    entries.append(f"file '{safe_last}'")
    concat.write_text("\n".join(entries) + "\n", encoding="utf-8")

    out = video_dir / "short_video.mp4"
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat),
        "-vf",
        "fps=30,format=yuv420p",
        "-pix_fmt",
        "yuv420p",
        str(out),
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        failure = video_dir / "ffmpeg_failed.txt"
        failure.write_text(str(exc), encoding="utf-8")
        return None
    return out


def write_upload_readme(paper_dir: Path, jpg_paths: list[Path], video_path: Path | None) -> None:
    rel_jpgs = [path.relative_to(paper_dir).as_posix() for path in jpg_paths]
    lines = [
        "# 上传文件",
        "",
        "## JPG 轮播图",
        "",
    ]
    for path in rel_jpgs:
        lines.append(f"- `{path}`")
    lines.extend(["", "## 短视频", ""])
    if video_path:
        lines.append(f"- `{video_path.relative_to(paper_dir).as_posix()}`")
    else:
        lines.append("- 本机 ffmpeg 合成失败，请查看 `video/ffmpeg_failed.txt`。")
    lines.extend(
        [
            "",
            "## 论文图版候选",
            "",
            "- `extracted_figures/contact_sheet.jpg`",
            "- `extracted_figures/README.md`",
            "",
            "## AI 叙事视频提示词",
            "",
            "- `ai_video/README.md`",
            "",
            "## 后续人工替换",
            "",
            "- 当前 JPG 已自动放入提取到的论文图版候选；请按科学故事线检查是否需要换成 contact sheet 中更合适的图。",
            "- 如果要做 Seedance / GPT video 风格短片，先选 4-5 个图版候选，再使用 `ai_video/README.md` 的提示词。",
            "- 录制中文配音后，可把音频放到 `voice/`，再重新剪辑短视频。",
        ]
    )
    (paper_dir / "UPLOAD.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_publish_readme(
    paper_dir: Path,
    markdown: str,
    slides: list[Slide],
    jpg_paths: list[Path],
    video_path: Path | None,
) -> None:
    caption = parse_named_section(markdown, "Caption Draft", "Hashtags")
    hashtags = parse_named_section(markdown, "Hashtags", "Asset Checklist")
    post_title = slides[0].title if slides else PAPER_LABELS.get(paper_dir.name, paper_dir.name)
    rel_images = [path.relative_to(paper_dir).as_posix() for path in jpg_paths]
    lines = [
        "# 发布清单",
        "",
        "## 小红书标题",
        "",
        post_title,
        "",
        "## 正文",
        "",
        caption,
        "",
        "图中数据和照片来自论文原图版裁切，已做科普排版。重点不是承诺治疗效果，而是解释这个神经接口技术解决了什么问题。",
        "",
        "## Hashtags",
        "",
        hashtags,
        "",
        "## 轮播图上传顺序",
        "",
    ]
    for path in rel_images:
        lines.append(f"- `{path}`")
    lines.extend(["", "## 短视频", ""])
    if video_path:
        lines.append(f"- `{video_path.relative_to(paper_dir).as_posix()}`")
    else:
        lines.append("- 未生成短视频。")
    lines.extend(
        [
            "",
            "## 发布前快速检查",
            "",
            "- 每页都应有一个清晰主图、一个证据解读、一个核心结论。",
            "- 如果某页主图不是最能支持文字的图，请从 `extracted_figures/contact_sheet.jpg` 重新选择。",
            "- 不要在正文中写“治愈”“临床可用”等论文没有直接证明的表述。",
            "- 如用 AI 视频工具，使用 `ai_video/README.md`，并上传本页选中的论文图作为 reference images。",
        ]
    )
    (paper_dir / "PUBLISH.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    requested = set(sys.argv[1:])
    paper_dirs = [
        path
        for path in sorted(BASE_DIR.iterdir())
        if path.is_dir() and (path / "README.md").exists() and path.name != "tools"
    ]
    for paper_dir in paper_dirs:
        if requested and paper_dir.name not in requested:
            continue
        markdown = (paper_dir / "README.md").read_text(encoding="utf-8")
        slides = parse_slides(markdown)
        if not slides:
            print(f"SKIP {paper_dir.name}: no slides")
            continue
        label = PAPER_LABELS.get(paper_dir.name, paper_dir.name)
        figure_assets = load_figure_assets(paper_dir, count=len(slides))
        slide_seconds = slide_seconds_for_count(len(slides))
        clear_generated_jpgs(paper_dir)
        jpg_paths = [
            draw_slide(
                paper_dir,
                label,
                slide,
                len(slides),
                figure_assets[index] if index < len(figure_assets) else None,
            )
            for index, slide in enumerate(slides)
        ]
        write_subtitles(paper_dir, slides, slide_seconds)
        write_video_notes(paper_dir, slides, slide_seconds)
        video_path = make_video(paper_dir, jpg_paths, slide_seconds)
        write_upload_readme(paper_dir, jpg_paths, video_path)
        write_publish_readme(paper_dir, markdown, slides, jpg_paths, video_path)
        print(f"DONE {paper_dir.name}: {len(jpg_paths)} jpg, video={bool(video_path)}")


if __name__ == "__main__":
    main()
