from __future__ import annotations

import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


STYLE_PROMPT = """竖屏 9:16 科研科普短视频，30-60 秒，中文旁白，面向小红书观众。风格应当像高质量科学纪录片片段：干净、克制、专业、有故事节奏；使用真实论文 figure panel 作为数据证据，穿插少量 AI 生成的抽象生物电子/神经信号动画。画面不要夸张，不要医疗广告感，不要科幻化，不要制造论文中没有的数据。"""

NEGATIVE_PROMPT = """不要生成真实患者脸部、手术血腥画面、虚假的仪器读数、夸张治疗承诺、临床治愈暗示、药品广告风格、过度赛博朋克风格、不可读的伪文字、错误的脑区标注。所有数据图只使用提供的论文 figure，不要重绘或改动数值关系。"""


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


def parse_slides(markdown: str) -> list[dict[str, str]]:
    section = parse_section(
        markdown,
        "## 4-5 Page Xiaohongshu Carousel",
        "## 60-90 Second Dubbed Video Script",
    )
    chunks = re.split(r"\n### Page\s+(\d+)[^\n]*\n", section)
    slides: list[dict[str, str]] = []
    for i in range(1, len(chunks), 2):
        number = chunks[i]
        body = chunks[i + 1]
        slides.append(
            {
                "number": number,
                "title": parse_field(body, "Title"),
                "visual": parse_field(body, "Visual"),
                "copy": parse_field(body, "Copy"),
                "takeaway": parse_field(body, "Takeaway"),
            }
        )
    return [slide for slide in slides if slide["title"]]


def parse_field(text: str, field: str) -> str:
    match = re.search(rf"^{re.escape(field)}:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def parse_voice_script(markdown: str) -> list[str]:
    section = parse_section(
        markdown,
        "## 60-90 Second Dubbed Video Script",
        "## Figure Story Map",
    )
    lines = []
    for line in section.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^\d+-\d+s:\s*", "", line)
        lines.append(line)
    return lines


def parse_candidates(paper_dir: Path) -> list[str]:
    manifest = paper_dir / "extracted_figures" / "manifest.txt"
    if not manifest.exists():
        return []
    candidates = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        filename = line.split("\t", 1)[0]
        candidates.append(f"extracted_figures/{filename}")
    return candidates


def write_ai_video_brief(paper_dir: Path) -> None:
    markdown = (paper_dir / "README.md").read_text(encoding="utf-8")
    slides = parse_slides(markdown)
    voice_lines = parse_voice_script(markdown)
    candidates = parse_candidates(paper_dir)
    out_dir = paper_dir / "ai_video"
    out_dir.mkdir(exist_ok=True)

    lines = [
        "# AI Story Video Brief",
        "",
        "目标：把这篇论文做成一个 30-60 秒的中文小红书科普短视频，强调故事线、主结论和论文 figure 证据。",
        "",
        "## 推荐工作流",
        "",
        "1. 先打开 `../extracted_figures/contact_sheet.jpg`，从候选图里选 4-5 个最适合的主图。",
        "2. 把选中的图作为 reference images 上传到 Seedance / GPT video / Sora 类视频工具。",
        "3. 使用下面的总提示词和分镜提示；数据图出现时只做轻微推拉、框选、箭头标注，不改动原图。",
        "4. 生成视频后，再用 `../video/subtitles.srt` 或本文件旁白稿做字幕/配音。",
        "",
        "## 总提示词",
        "",
        STYLE_PROMPT,
        "",
        "## 负面提示词",
        "",
        NEGATIVE_PROMPT,
        "",
        "## 参考图文件",
        "",
    ]
    if candidates:
        lines.extend([f"- `{candidate}`" for candidate in candidates])
    else:
        lines.append("- 尚未提取到 figure candidates，请先运行 `../tools/extract_pdf_figures.py`。")

    lines.extend(["", "## 30-60 秒分镜", ""])
    total = len(slides)
    for index, slide in enumerate(slides, start=1):
        start = int((index - 1) * 42 / max(total, 1))
        end = int(index * 42 / max(total, 1))
        figure_hint = candidates[index - 1] if index - 1 < len(candidates) else "从 contact_sheet 选择最相关 figure"
        lines.extend(
            [
                f"### Shot {index}: {start}-{end}s",
                "",
                f"- 画面目标：{slide['title']}",
                f"- 使用图像：`{figure_hint}`",
                f"- 动画方式：从抽象神经信号/器件局部过渡到论文图；对关键区域做温和高亮、箭头或放大框。",
                f"- 屏幕文字：{slide['takeaway']}",
                f"- 旁白要点：{slide['copy']}",
                "",
            ]
        )

    lines.extend(["## 中文旁白稿", ""])
    for line in voice_lines:
        lines.append(f"- {line}")

    lines.extend(
        [
            "",
            "## 一键复制版提示词",
            "",
            "```text",
            STYLE_PROMPT,
            "",
            "请根据以下分镜生成一个 9:16、30-60 秒中文科研科普短视频。数据证据画面必须来自上传的论文 figure reference images；其余过渡画面可以生成抽象神经信号、柔性电子、植入式设备、动物自由活动等非写实背景。整体克制、清晰、可信。",
            "",
        ]
    )
    for index, slide in enumerate(slides, start=1):
        figure_hint = candidates[index - 1] if index - 1 < len(candidates) else "选择最相关论文图"
        lines.append(f"{index}. {slide['title']}；使用 {figure_hint}；屏幕文字：{slide['takeaway']}；旁白：{slide['copy']}")
    lines.extend(["", "避免：", NEGATIVE_PROMPT, "```", ""])

    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    for paper_dir in sorted(BASE_DIR.iterdir()):
        if not paper_dir.is_dir() or paper_dir.name == "tools":
            continue
        if not (paper_dir / "README.md").exists():
            continue
        write_ai_video_brief(paper_dir)
        print(f"DONE {paper_dir.name}")


if __name__ == "__main__":
    main()

