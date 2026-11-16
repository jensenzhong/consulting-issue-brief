# -*- coding: utf-8 -*-
"""Render a vertical current-state process chart for a consulting issue brief.

Fill in a JSON file (see steps-template.json) with the stages found in *this*
company's materials, then run:

    python make_flow_chart.py steps.json -o flowchart.png

Do not reuse the placeholder steps or any other company's chart. The visual
rules are fixed; the stage names, handoffs, and tags must come from the
source materials.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

NAVY = (27, 54, 93)
ORANGE = (192, 86, 33)
CREAM = (248, 237, 227)
PALE = (232, 238, 244)
BG = (255, 255, 255)
TEXT = (28, 32, 38)
MUTED = (92, 101, 112)
CARD = (247, 249, 251)
WHITE = (255, 255, 255)

# Printed on A4 at this pixel size (~16.3 cm x 25.2 cm, 250 dpi).
DEFAULT_SIZE = (1604, 2480)
MIN_TITLE_PX = 48  # ~14 pt at 250 dpi
MIN_BODY_PX = 38   # ~11 pt
MIN_TAG_PX = 34    # ~10 pt
MIN_NUM_PX = 38


def _first_existing(candidates):
    for path in candidates:
        if path and Path(path).is_file():
            return str(path)
    return None


def find_fonts():
    """Locate KaiTi and Times New Roman without hard-coding one machine."""
    home = Path.home()
    here = Path(__file__).resolve().parent
    kai = _first_existing(
        [
            here / "fonts" / "simkai.ttf",
            home / ".fonts" / "simkai.ttf",
            Path("C:/Windows/Fonts/simkai.ttf"),
            Path("C:/Windows/Fonts/KAIU.TTF"),
            Path("C:/Windows/Fonts/STKAITI.TTF"),
            Path("/usr/share/fonts/truetype/arphic/ukai.ttc"),
        ]
    )
    tnr = _first_existing(
        [
            here / "fonts" / "TimesNewRoman.ttf",
            home / ".fonts" / "TimesNewRoman.ttf",
            Path("C:/Windows/Fonts/times.ttf"),
            Path("C:/Windows/Fonts/timesnr.ttf"),
        ]
    )
    tnr_b = _first_existing(
        [
            here / "fonts" / "TimesNewRoman-Bold.ttf",
            home / ".fonts" / "TimesNewRoman-Bold.ttf",
            Path("C:/Windows/Fonts/timesbd.ttf"),
        ]
    )
    if not kai or not tnr:
        missing = []
        if not kai:
            missing.append("楷体 (simkai.ttf / KaiTi)")
        if not tnr:
            missing.append("Times New Roman")
        raise SystemExit(
            "找不到字体："
            + "、".join(missing)
            + "。请把授权字体放到本目录的 fonts/ 下，或安装到系统字体目录。"
        )
    return kai, tnr, tnr_b or tnr


KAI_PATH, TNR_PATH, TNR_BOLD_PATH = None, None, None


def _load_fonts():
    global KAI_PATH, TNR_PATH, TNR_BOLD_PATH
    if KAI_PATH is None:
        KAI_PATH, TNR_PATH, TNR_BOLD_PATH = find_fonts()


def kai(size):
    _load_fonts()
    return ImageFont.truetype(KAI_PATH, size)


def tnr(size, bold=False):
    _load_fonts()
    return ImageFont.truetype(TNR_BOLD_PATH if bold else TNR_PATH, size)


def is_latin_char(ch):
    return ord(ch) < 0x2E80


def text_width(text, size, bold=False):
    font_k = kai(size)
    font_t = tnr(size, bold=bold)
    return sum((font_t if is_latin_char(ch) else font_k).getlength(ch) for ch in text)


def draw_mixed(draw, x, y, text, size, fill, bold=False):
    font_k = kai(size)
    font_t = tnr(size, bold=bold)
    cx = x
    for ch in text:
        f = font_t if is_latin_char(ch) else font_k
        draw.text((cx, y), ch, font=f, fill=fill)
        cx += f.getlength(ch)
    return cx - x


def wrap_text(text, size, max_w, bold=False):
    lines = []
    for para in text.split("\n"):
        buf = ""
        for ch in para:
            trial = buf + ch
            if text_width(trial, size, bold) <= max_w:
                buf = trial
            else:
                if buf:
                    lines.append(buf)
                buf = ch
        if buf or not para:
            lines.append(buf)
    return lines


def rounded_rect(draw, box, radius, fill, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_arrow(draw, x, y0, y1, color=NAVY):
    shaft_w = 5
    draw.rectangle([x - shaft_w // 2, y0, x + shaft_w // 2, y1 - 18], fill=color)
    draw.polygon([(x, y1), (x - 12, y1 - 20), (x + 12, y1 - 20)], fill=color)


def render(data, out_path, size=DEFAULT_SIZE):
    steps = data["steps"]
    if not steps:
        raise SystemExit("JSON 里没有 steps。")
    if len(steps) > 9:
        raise SystemExit("环节超过 9 个，请拆成多张图以保持可读。")

    W, H = size
    im = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(im)

    title = data.get("title") or "现行链路"
    subtitle = data.get("subtitle") or ""
    footer = data.get("footer") or ""

    tw = text_width(title, 52)
    draw_mixed(draw, (W - tw) / 2, 36, title, 52, NAVY)
    if subtitle:
        sw = text_width(subtitle, 28)
        draw_mixed(draw, (W - sw) / 2, 108, subtitle, 28, MUTED)
    draw.rectangle([W // 2 - 80, 160, W // 2 + 80, 166], fill=ORANGE)

    top = 190
    bottom_reserve = 110 if footer else 48
    n = len(steps)
    gap = 36
    avail = H - top - bottom_reserve - gap * (n - 1)
    box_h = avail // n
    margin_x = 70
    box_w = W - margin_x * 2

    # Keep type readable: if boxes are short, shrink padding/tags first, not type.
    title_size = max(MIN_TITLE_PX, 40)
    body_size = max(MIN_BODY_PX, 30)
    tag_size = max(MIN_TAG_PX, 26)
    num_size = max(MIN_NUM_PX, 28)
    if box_h < 220:
        title_size = MIN_TITLE_PX
        body_size = MIN_BODY_PX
        tag_size = MIN_TAG_PX
        num_size = MIN_NUM_PX

    for i, step in enumerate(steps):
        y = top + i * (box_h + gap)
        x0, y0 = margin_x, y
        x1, y1 = margin_x + box_w, y + box_h
        missing = bool(step.get("missing"))
        fill = CREAM if missing else CARD
        outline = ORANGE if missing else NAVY
        ow = 6 if missing else 3
        rounded_rect(draw, (x0, y0, x1, y1), 18, fill, outline=outline, width=ow)

        bar_color = ORANGE if missing else NAVY
        draw.rounded_rectangle([x0, y0, x0 + 12, y1], radius=6, fill=bar_color)
        draw.rectangle([x0 + 6, y0, x0 + 12, y1], fill=bar_color)

        num = str(step.get("num") or f"{i + 1:02d}")
        draw_mixed(draw, x0 + 36, y0 + 22, num, num_size, bar_color, bold=True)
        title_x = x0 + 36 + text_width(num, num_size, bold=True) + 18
        draw_mixed(draw, title_x, y0 + 16, step.get("title") or f"[环节 {i + 1}]", title_size, NAVY)

        if missing:
            badge = step.get("badge") or "现状基本缺失"
            bw = text_width(badge, 24) + 28
            bh = 38
            bx = x1 - 28 - bw
            by = y0 + 16
            rounded_rect(draw, (bx, by, bx + bw, by + bh), 8, ORANGE)
            draw_mixed(draw, bx + 14, by + 5, badge, 24, WHITE)

        text_max = box_w - 80
        by = y0 + 78
        lines = wrap_text(step.get("who") or "", body_size, text_max)
        if by + 44 * len(lines) > y1 - 68:
            raise SystemExit(f"第 {i + 1} 个环节说明过长，请缩短或拆图。")
        for line in lines:
            draw_mixed(draw, x0 + 36, by, line, body_size, TEXT)
            by += 44

        tags = list(step.get("tags") or [])
        badge_text = step.get("badge") or "现状基本缺失"
        tx, ty = x0 + 36, y1 - 58
        for tag in tags:
            if missing and tag == badge_text:
                continue
            twid = text_width(tag, tag_size) + 28
            if tx + twid > x1 - 28:
                raise SystemExit(f"第 {i + 1} 个环节标签过长，请缩短标签。")
            rounded_rect(draw, (tx, ty, tx + twid, ty + 40), 8, CREAM, outline=ORANGE, width=2)
            draw_mixed(draw, tx + 14, ty + 5, tag, tag_size, ORANGE)
            tx += twid + 16

        if i < n - 1:
            draw_arrow(draw, W // 2, y1 + 2, y1 + gap - 2, color=NAVY)

    if footer:
        fw = text_width(footer, 26)
        fy = H - 70
        draw.rectangle([70, fy - 28, W - 70, H - 28], fill=PALE)
        draw_mixed(draw, max(86, (W - fw) / 2), fy - 16, footer, 26, MUTED)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "PNG", optimize=True)
    print(f"wrote {out} {im.size}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Draw a vertical current-state process chart.")
    parser.add_argument(
        "json_path",
        nargs="?",
        default=str(Path(__file__).with_name("steps-template.json")),
        help="Step list JSON (default: steps-template.json)",
    )
    parser.add_argument("-o", "--output", required=True, help="Output PNG path")
    args = parser.parse_args(argv)

    src = Path(args.json_path)
    if not src.is_file():
        raise SystemExit(f"找不到 JSON：{src}")
    data = json.loads(src.read_text(encoding="utf-8"))
    out = args.output
    render(data, out)


if __name__ == "__main__":
    main()
