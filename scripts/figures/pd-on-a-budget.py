#!/usr/bin/env python3
"""Generate the static SVG figures for the post `pd-on-a-budget`.

Pure standard library, no plotting dependency:

    python3 scripts/figures/pd-on-a-budget.py

writes public/statics/images/pd-on-a-budget-*.svg. Every number below is
copied from the measurement write-ups the post cites; change them here, not in
the SVG files.

Colours follow a validated two-series categorical palette (blue = PD,
orange = monolithic), checked for colour-vision deficiency separation and
contrast on the light chart surface.
"""

from __future__ import annotations

import html
import os
import unicodedata

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "public", "statics", "images")

FONT = (
    "-apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', "
    "'Noto Sans CJK SC', 'Microsoft YaHei', 'Segoe UI', sans-serif"
)

# Chart chrome and ink (light surface only: the blog has no dark theme).
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
BORDER = "#d6d5ce"
PANEL = "#f4f4f1"

# Categorical slots 1 and 2.
BLUE = "#2a78d6"  # PD
ORANGE = "#eb6834"  # monolithic

# Status (always with an icon and a label).
CRITICAL = "#d03b3b"
GOOD = "#0ca30c"


# --------------------------------------------------------------------------
# helpers


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def tw(s: str, size: float) -> float:
    """Rough rendered width of a string, for layout only."""
    w = 0.0
    for ch in str(s):
        if unicodedata.east_asian_width(ch) in ("W", "F"):
            w += size
        elif ch == " ":
            w += size * 0.3
        elif ch in "il.,:;'|!":
            w += size * 0.3
        elif ch in "mwMW%":
            w += size * 0.85
        else:
            w += size * 0.56
    return w


def text(x, y, s, size=13, fill=INK, anchor="start", weight=400, extra=""):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" font-weight="{weight}"{extra}>{esc(s)}</text>'
    )


def line(x1, y1, x2, y2, stroke=GRID, width=1, extra=""):
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{stroke}" stroke-width="{width}"{extra}/>'
    )


def rect(x, y, w, h, fill, rx=0, stroke=None, sw=1, extra=""):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="{rx}" fill="{fill}"{s}{extra}/>'
    )


def hbar(x0, y, length, h, fill, r=4):
    """Horizontal bar, square at the baseline (x0), rounded at the data end."""
    if length <= 0:
        return ""
    r = min(r, length / 2, h / 2)
    x1 = x0 + length
    return (
        f'<path d="M{x0:.1f},{y:.1f} H{x1 - r:.1f} '
        f"Q{x1:.1f},{y:.1f} {x1:.1f},{y + r:.1f} V{y + h - r:.1f} "
        f'Q{x1:.1f},{y + h:.1f} {x1 - r:.1f},{y + h:.1f} H{x0:.1f} Z" fill="{fill}"/>'
    )


def vbar(x, y0, w, height, fill, r=4):
    """Vertical bar, square at the baseline (y0), rounded at the top."""
    if height <= 0:
        return ""
    r = min(r, height / 2, w / 2)
    y1 = y0 - height
    return (
        f'<path d="M{x:.1f},{y0:.1f} V{y1 + r:.1f} '
        f"Q{x:.1f},{y1:.1f} {x + r:.1f},{y1:.1f} H{x + w - r:.1f} "
        f'Q{x + w:.1f},{y1:.1f} {x + w:.1f},{y1 + r:.1f} V{y0:.1f} Z" fill="{fill}"/>'
    )


def polyline(points, stroke, width=2):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (
        f'<polyline points="{pts}" fill="none" stroke="{stroke}" stroke-width="{width}" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
    )


def dot(x, y, fill, r=4):
    # 2px surface ring keeps markers legible where lines cross.
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{SURFACE}" stroke-width="2"/>'


def arrow_head(x, y, direction, color, size=7):
    """Filled triangle whose tip is at (x, y)."""
    if direction == "right":
        pts = [(x, y), (x - size, y - size * 0.6), (x - size, y + size * 0.6)]
    elif direction == "left":
        pts = [(x, y), (x + size, y - size * 0.6), (x + size, y + size * 0.6)]
    elif direction == "down":
        pts = [(x, y), (x - size * 0.6, y - size), (x + size * 0.6, y - size)]
    else:  # up
        pts = [(x, y), (x - size * 0.6, y + size), (x + size * 0.6, y + size)]
    p = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    return f'<polygon points="{p}" fill="{color}"/>'


def arrow(x1, y1, x2, y2, color=INK2, width=1.5, head=7):
    """Straight horizontal or vertical arrow from (x1,y1) to (x2,y2)."""
    if abs(x2 - x1) >= abs(y2 - y1):
        d = "right" if x2 > x1 else "left"
        xe = x2 - head if d == "right" else x2 + head
        return line(x1, y1, xe, y2, color, width) + arrow_head(x2, y2, d, color, head)
    d = "down" if y2 > y1 else "up"
    ye = y2 - head if d == "down" else y2 + head
    return line(x1, y1, x2, ye, color, width) + arrow_head(x2, y2, d, color, head)


def svg_doc(w, h, body, title, desc):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d" font-family="{esc(FONT)}">\n'
        f'<title id="t">{esc(title)}</title>\n<desc id="d">{esc(desc)}</desc>\n'
        f'<rect width="{w}" height="{h}" fill="{SURFACE}"/>\n' + "\n".join(body) + "\n</svg>\n"
    )


def legend(x, y, items):
    """items: [(label, color, kind)] kind in {'line', 'bar'}; returns svg and width."""
    out = []
    cx = x
    for label, color, kind in items:
        if kind == "line":
            out.append(line(cx, y - 4, cx + 22, y - 4, color, 2))
            out.append(dot(cx + 11, y - 4, color))
            cx += 30
        else:
            out.append(rect(cx, y - 11, 14, 14, color, rx=3))
            cx += 22
        out.append(text(cx, y, label, 13, INK2))
        cx += tw(label, 13) + 24
    return out


def write(name, svg):
    path = os.path.join(OUT_DIR, f"pd-on-a-budget-{name}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", os.path.relpath(path))


# --------------------------------------------------------------------------
# data: 5090 capacity test, mono (1 GPU) vs PD 1P+1D (2 GPUs), same image,
# replay of the production traffic mix. E2E TTFA = time to the 10th token
# convolved with the TTS engine's other stages.

MONO_X = [2, 4, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40]
MONO_P95 = [289, 296, 325, 327, 336, 365, 347, 401, 427, 459, 452, 507]
MONO_P99 = [409, 414, 453, 421, 420, 489, 511, 492, 532, 557, 571, 596]
MONO_P1 = [63.8, 57.4, 48.1, 43.4, 41.8, 37.9, 38.1, 36.3, 33.6, 29.9, 27.5, 25.7]
MONO_GAP = [0.00, 0.00, 0.12, 0.19, 0.00, 0.38, 0.32, 0.73, 5.33, 12.80, 19.28, 54.02]

PD_X = [2, 4, 8, 16, 24, 32, 40, 44, 48, 56, 64]
PD_P95 = [300, 290, 304, 328, 361, 392, 406, 457, 451, 506, 487]
PD_P99 = [404, 362, 429, 442, 511, 517, 579, 598, 612, 633, 672]
PD_P1 = [61.5, 60.4, 56.3, 50.1, 45.1, 42.7, 38.5, 36.7, 34.3, 34.0, 32.6]
PD_GAP = [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.38, 17.78, 40.07, 49.87]


def scale(d0, d1, r0, r1):
    return lambda v: r0 + (v - d0) * (r1 - r0) / (d1 - d0)


def line_panel(body, x0, x1, y0, y1, xdom, ydom, yticks, xticks, series, ylabel_fmt, title):
    """One small-multiple line panel. series: [(xs, ys, color)]."""
    sx = scale(xdom[0], xdom[1], x0, x1)
    sy = scale(ydom[0], ydom[1], y1, y0)
    body.append(text(x0, y0 - 14, title, 14, INK, weight=600))
    for t in yticks:
        y = sy(t)
        body.append(line(x0, y, x1, y, GRID if t != ydom[0] else AXIS, 1))
        body.append(text(x0 - 8, y + 4, ylabel_fmt(t), 12, MUTED, anchor="end"))
    for t in xticks:
        body.append(text(sx(t), y1 + 18, str(t), 12, MUTED, anchor="middle"))
    for xs, ys, color in series:
        pts = [(sx(a), sy(b)) for a, b in zip(xs, ys)]
        body.append(polyline(pts, color))
        for px, py in pts:
            body.append(dot(px, py, color))
    return sx, sy


# --------------------------------------------------------------------------
# figure 3: TTFA vs concurrency


def fig_ttfa():
    W, H = 960, 470
    b = []
    b.append(text(24, 34, "首段音频时间（E2E TTFA）随并发的变化", 18, INK, weight=600))
    b.append(
        text(24, 58, "5090，线上流量配比回放。单体 = 1 张卡；PD 1P1D = 2 张卡。越低越好。", 13, INK2)
    )
    b += legend(24, 90, [("PD 1P1D（2 卡）", BLUE, "line"), ("单体（1 卡）", ORANGE, "line")])
    xt = [0, 8, 16, 24, 32, 40, 48, 56, 64]
    yt = [200, 300, 400, 500, 600, 700]
    fmt = lambda v: f"{v}"
    top, bottom = 140, 380
    sx, sy = line_panel(
        b, 70, 450, top, bottom, (0, 64), (200, 700), yt, xt,
        [(MONO_X, MONO_P95, ORANGE), (PD_X, PD_P95, BLUE)], fmt, "p95（ms）",
    )
    b.append(text(sx(40) + 8, sy(507) - 10, "单体只测到 40 路", 12, INK2))
    sx2, sy2 = line_panel(
        b, 550, 930, top, bottom, (0, 64), (200, 700), yt, xt,
        [(MONO_X, MONO_P99, ORANGE), (PD_X, PD_P99, BLUE)], fmt, "p99（ms）",
    )
    b.append(text(260, bottom + 42, "并发路数（整组）", 12, MUTED, anchor="middle"))
    b.append(text(740, bottom + 42, "并发路数（整组）", 12, MUTED, anchor="middle"))
    b.append(
        text(
            24, H - 14,
            "纵轴从 200 ms 起。按每卡算，PD 的首包并不更快：每卡 16 路时单体 p95 347 ms，PD（32 路）392 ms。PD 买的是不卡顿，见下一张图。",
            12, MUTED,
        )
    )
    write(
        "ttfa",
        svg_doc(
            W, H, b, "首段音频时间随并发的变化：单体与 PD 1P1D",
            "两个小图分别是 E2E TTFA 的 p95 和 p99。单体（1 卡）从 2 路到 40 路，p95 从 289 ms 涨到 507 ms；"
            "PD 1P1D（2 卡）从 2 路到 64 路，p95 从 300 ms 涨到 487 ms。同样并发下两者接近，PD 略低。",
        ),
    )


# --------------------------------------------------------------------------
# figure 4: stutter share and slowest-1% speed


def fig_stutter():
    W, H = 960, 470
    b = []
    b.append(text(24, 34, "卡顿占比与最慢 1% 的流速", 18, INK, weight=600))
    b.append(
        text(
            24, 58,
            "同一次测试。卡顿 = 按首窗 10,10,12,32,64 播放时出现空隙的流的占比；流速 p1 = 最慢 1% 的流的 tok/s。",
            13, INK2,
        )
    )
    b += legend(24, 90, [("PD 1P1D（2 卡）", BLUE, "bar"), ("单体（1 卡）", ORANGE, "bar")])

    # left: grouped bars at the concurrency levels both setups ran.
    x0, x1, top, bottom = 70, 450, 140, 380
    b.append(text(x0, top - 14, "卡顿流占比（%）", 14, INK, weight=600))
    sy = scale(0, 60, bottom, top)
    for t in [0, 10, 20, 30, 40, 50, 60]:
        y = sy(t)
        b.append(line(x0, y, x1, y, GRID if t else AXIS, 1))
        b.append(text(x0 - 8, y + 4, str(t), 12, MUTED, anchor="end"))
    levels = [8, 16, 24, 32, 40]
    mono = {x: g for x, g in zip(MONO_X, MONO_GAP)}
    pd = {x: g for x, g in zip(PD_X, PD_GAP)}
    band = (x1 - x0) / len(levels)
    bw = 22
    for i, lv in enumerate(levels):
        cx = x0 + band * (i + 0.5)
        xa = cx - bw - 1  # PD
        xb = cx + 1  # mono (2px surface gap between the pair)
        hp = bottom - sy(pd[lv])
        hm = bottom - sy(mono[lv])
        b.append(vbar(xa, bottom, bw, hp, BLUE))
        b.append(vbar(xb, bottom, bw, hm, ORANGE))
        b.append(text(xa + bw / 2, bottom - hp - 6, "0", 11, INK2, anchor="middle"))
        lab = f"{mono[lv]:.2f}" if mono[lv] < 1 else f"{mono[lv]:.1f}"
        b.append(text(xb + bw / 2, bottom - hm - 6, lab, 11, INK2, anchor="middle"))
        b.append(text(cx, bottom + 18, str(lv), 12, MUTED, anchor="middle"))
    b.append(text((x0 + x1) / 2, bottom + 40, "并发路数（整组）", 12, MUTED, anchor="middle"))

    # right: slowest-1% speed with the 42 tok/s floor.
    sx, sy2 = line_panel(
        b, 550, 930, top, bottom, (0, 64), (20, 70),
        [20, 30, 40, 50, 60, 70], [0, 8, 16, 24, 32, 40, 48, 56, 64],
        [(MONO_X, MONO_P1, ORANGE), (PD_X, PD_P1, BLUE)], lambda v: f"{v}", "最慢 1% 的流速（tok/s）",
    )
    yf = sy2(42)
    b.append(line(550, yf, 930, yf, INK2, 1.5))
    b.append(text(926, yf - 7, "42 tok/s 底线（RTF ≤ 0.5）", 12, INK2, anchor="end"))
    b.append(text(740, bottom + 40, "并发路数（整组）", 12, MUTED, anchor="middle"))
    b.append(
        text(
            24, H - 14,
            "单体 8 路起就有卡顿流；PD 到 40 路都是 0，44 路开始出现（1.38%），48 路 17.8%。每卡 16 路时 PD p1 42.7，单体 38.1。",
            12, MUTED,
        )
    )
    write(
        "stutter",
        svg_doc(
            W, H, b, "卡顿占比与最慢 1% 流速：单体与 PD 1P1D",
            "左图：在 8、16、24、32、40 路时，单体卡顿流占比为 0.12%、0.32%、5.33%、19.28%、54.02%，PD 1P1D 全部为 0。"
            "右图：最慢 1% 的流速，单体 8 路 48.1、16 路 38.1、40 路 25.7 tok/s；PD 16 路 50.1、32 路 42.7、40 路 38.5 tok/s；"
            "参考线为 42 tok/s。",
        ),
    )


# --------------------------------------------------------------------------
# figure 5: waterfall of the slowest 1% (B300 1P1D replay, steady state)

WATERFALL = [
    # (stage, note, ms) — means over the slowest 1% to the 10th token; they add up to 392 ms.
    ("客户端 → LB → Prefill", "网络 + LB 解析和转发", 3.2),
    ("Prefill 接收与调度准入", "交给调度器、反序列化、排队；后来用紧凑数组传 prompt", 86.1),
    ("Prefill 前向", "含冷热请求同批造成的队头阻塞", 58.2),
    ("KV 传输链", "等 D 的页表、发送排队、拷贝、通知", 21.0),
    ("Decode 接入", "发现传输完成、提交、等下一步才入批", 21.5),
    ("Decode 前 9 步", "大头；每步 GPU + 主机时间，后来开了 overlap", 199.6),
    ("Decode 输出 → LB → 客户端", "第 10 个 token 的转发", 2.5),
]


def fig_waterfall():
    W, H = 960, 520
    b = []
    b.append(text(24, 34, "最慢的 1% 请求，时间都花在哪", 18, INK, weight=600))
    b.append(
        text(
            24, 58,
            "B300 1P1D，线上流量回放（7.8 万请求）。稳态下最慢 1% 请求到第 10 个 token 的分段均值，合计 392 ms。",
            13, INK2,
        )
    )
    lx, x0, x1 = 24, 370, 900
    top = 100
    row = 50
    sx = scale(0, 400, x0, x1)
    n = len(WATERFALL)
    bottom = top + row * n
    for t in [0, 100, 200, 300, 400]:
        b.append(line(sx(t), top - 8, sx(t), bottom, GRID if t else AXIS, 1))
        b.append(text(sx(t), bottom + 18, f"{t}", 12, MUTED, anchor="middle"))
    b.append(text(sx(400), bottom + 36, "ms", 12, MUTED, anchor="end"))
    acc = 0.0
    bh = 18
    prev_end = None
    for i, (stage, note, ms) in enumerate(WATERFALL):
        yc = top + row * i + row / 2
        b.append(text(lx, yc - 3, stage, 14, INK, weight=600))
        b.append(text(lx, yc + 15, note, 12, MUTED))
        xs, xe = sx(acc), sx(acc + ms)
        if prev_end is not None:
            b.append(line(prev_end, yc - row + bh / 2, prev_end, yc - bh / 2, AXIS, 1))
        w = max(xe - xs, 2)
        r = min(3, w / 2)
        b.append(rect(xs, yc - bh / 2, w, bh, BLUE, rx=r))
        lab = f"{ms:.1f} ms" if ms < 10 else f"{ms:.0f} ms"
        b.append(text(xe + 6, yc + 4, lab, 12, INK2))
        acc += ms
        prev_end = xe
    b.append(
        text(
            24, H - 14,
            "各段首尾相接、没有空隙，加起来等于客户端实测时间。突发时最慢 1%（按首 token）里，Prefill 调度一项就占 786 ms 中的 501 ms。",
            12, MUTED,
        )
    )
    write(
        "waterfall",
        svg_doc(
            W, H, b, "最慢 1% 请求的时间瀑布",
            "七段依次为：客户端到 Prefill 3.2 ms，Prefill 接收与调度准入 86 ms，Prefill 前向 58 ms，KV 传输链 21 ms，"
            "Decode 接入 21.5 ms，Decode 前 9 步 200 ms，输出转发 2.5 ms，合计 392 ms。",
        ),
    )


# --------------------------------------------------------------------------
# figure 6: unit start-up time

STARTUP = [
    ("改之前", "D 140 s、P 119 s 就绪", 148),
    ("+ 按角色捕获 graph、并行预编译 JIT", "D 65 s、P 76 s 就绪", 79),
    ("+ P 的 piecewise 封顶、HiCache 后台锁页", "D 39 s、P 45 s 就绪", 47),
]

WASTE = [
    ("Decode", [
        ("JIT 模块第一次用时串行 nvcc 编译", 49),
        ("piecewise extend graph（D 从来不跑 extend）", 29),
        ("HiCache 64 GiB 主机池同步锁页", 20.5),
    ]),
    ("Prefill", [
        ("decode graph bs 1–128（P 从来不 decode）", 23),
        ("采样器 graph 梯子捕获到 128", 23),
        ("piecewise 梯子封顶 2048 后省下", 20.2),
        ("HiCache 24 GiB 主机池同步锁页", 8),
    ]),
]


def fig_startup():
    W, H = 960, 640
    b = []
    b.append(text(24, 34, "PD 单元启动：148 s → 47 s", 18, INK, weight=600))
    b.append(text(24, 58, "5090 上一个 1P1D 单元，从 Pod 启动到 LB /health 返回 200。", 13, INK2))

    lx, x0, x1 = 24, 380, 860
    sx = scale(0, 160, x0, x1)
    top = 96
    row = 52
    bottom = top + row * len(STARTUP)
    for t in [0, 40, 80, 120, 160]:
        b.append(line(sx(t), top - 6, sx(t), bottom, GRID if t else AXIS, 1))
        b.append(text(sx(t), bottom + 18, f"{t} s", 12, MUTED, anchor="middle"))
    for i, (label, sub, v) in enumerate(STARTUP):
        yc = top + row * i + row / 2
        b.append(text(lx, yc - 3, label, 14, INK, weight=600))
        b.append(text(lx, yc + 15, sub, 12, MUTED))
        b.append(hbar(x0, yc - 10, sx(v) - x0, 20, BLUE))
        b.append(text(sx(v) + 8, yc + 5, f"{v} s", 14, INK, weight=600))

    # lower panel: the measured waste, by role.
    y = bottom + 66
    b.append(text(24, y, "测出来的浪费（秒）", 15, INK, weight=600))
    b.append(text(24 + tw("测出来的浪费（秒）", 15) + 12, y, "P 和 D 并行启动，这些数不能直接相加", 12, MUTED))
    sx2 = scale(0, 60, x0, x1)
    y += 24
    # lay the rows out first so the grid sits under the bars
    rows = []
    for role, items in WASTE:
        rows.append(("head", role, None, y))
        y += 24
        for label, v in items:
            rows.append(("item", label, v, y))
            y += 28
        y += 6
    grid_top, grid_bottom = rows[0][3] + 4, y - 6
    for t in [0, 20, 40, 60]:
        b.append(line(sx2(t), grid_top, sx2(t), grid_bottom, GRID if t else AXIS, 1))
        b.append(text(sx2(t), grid_bottom + 18, f"{t} s", 12, MUTED, anchor="middle"))
    for kind, label, v, ry in rows:
        if kind == "head":
            b.append(text(lx, ry + 14, label, 13, INK2, weight=600))
            continue
        b.append(text(lx + 12, ry + 13, label, 13, INK))
        b.append(hbar(x0, ry, sx2(v) - x0, 16, BLUE))
        lab = "≈49 s" if v == 49 else f"{v:g} s"
        b.append(text(sx2(v) + 8, ry + 13, lab, 12, INK2))
    write(
        "startup",
        svg_doc(
            W, H, b, "PD 单元启动时间从 148 秒降到 47 秒",
            "上半部分：原始版本 148 秒，按角色捕获 graph 并行预编译 JIT 后 79 秒，再加 piecewise 封顶和 HiCache 后台锁页后 47 秒。"
            "下半部分：测出来的浪费，Decode 侧 JIT 串行编译约 49 秒、无用 piecewise graph 29 秒、同步锁页 20.5 秒；"
            "Prefill 侧无用 decode graph 23 秒、采样器 graph 23 秒、piecewise 封顶省 20 秒、同步锁页 8 秒。",
        ),
    )


# --------------------------------------------------------------------------
# figure 1: architecture of one 1P1D unit


def box(b, x, y, w, h, title, lines=(), fill="#ffffff", stroke=BORDER, title_size=14, sub_size=12, rx=8, title_fill=INK):
    b.append(rect(x, y, w, h, fill, rx=rx, stroke=stroke, sw=1))
    b.append(text(x + 12, y + 22, title, title_size, title_fill, weight=600))
    for i, s in enumerate(lines):
        b.append(text(x + 12, y + 42 + i * 17, s, sub_size, INK2))


def fig_architecture():
    W, H = 960, 622
    b = []
    b.append(text(24, 34, "部署形态：固定的 1P1D 单元", 18, INK, weight=600))
    b.append(text(24, 58, "一个单元 = 一个 Pod = 同一台机器上的 2 张卡。扩容就是多起几个单元。", 13, INK2))

    # left column: upstream, router, KEDA
    box(b, 24, 96, 190, 64, "TTS 引擎", ["文本 → token 请求"])
    b.append(arrow(119, 160, 119, 196))
    box(b, 24, 196, 190, 80, "Router", ["按会话亲和分发到单元", "不关心单元里面是什么"])
    box(b, 24, 330, 190, 96, "KEDA", ["按 decode 在途路数", "扩缩单元个数，", "目标留出突发余量"], fill=PANEL)

    # ghost units behind the main one
    for k, off in enumerate([16, 8]):
        b.append(rect(270 + off, 92 - off, 666, 352, "#ffffff", rx=10, stroke=BORDER))
    b.append(text(926, 80, "单元 2 … N", 12, MUTED, anchor="end"))

    ux, uy, uw, uh = 262, 100, 666, 352
    b.append(rect(ux, uy, uw, uh, "#ffffff", rx=10, stroke=INK2, sw=1.2))
    b.append(text(ux + 16, uy + 26, "1P1D 单元（一个 Pod）", 15, INK, weight=600))

    # router -> unit, KEDA -> unit
    b.append(arrow(214, 236, 296, 236))
    b.append(arrow(214, 378, 262, 378, MUTED, 1.2))
    b.append(text(220, 372, "扩缩", 11, MUTED))

    # pd-lb
    box(b, 296, 196, 170, 96, "pd-lb（Rust）", ["只转发给本单元的 P 和 D", "预热通过才就绪", "退出前把在途流放完"])

    # prefill / decode
    px, py, pw, ph = 540, 132, 190, 78
    dx, dy = 540, 300
    box(b, px, py, pw, ph, "Prefill（GPU A）", ["算 prompt 的 KV 和首 token"], stroke=INK2)
    box(b, dx, dy, pw, ph, "Decode（GPU B）", ["逐 token 解码，流式吐出"], stroke=INK2)

    # lb -> P, lb -> D (the two legs)
    b.append(line(466, 222, 503, 222, INK2, 1.5))
    b.append(line(503, 222, 503, 171, INK2, 1.5))
    b.append(arrow(503, 171, 540, 171))
    b.append(line(466, 250, 503, 250, INK2, 1.5))
    b.append(line(503, 250, 503, 322, INK2, 1.5))
    b.append(arrow(503, 322, 540, 322))
    b.append(text(472, 214, "请求", 11, MUTED))
    # D -> lb stream
    b.append(line(540, 352, 488, 352, INK2, 1.2))
    b.append(line(488, 352, 488, 292, INK2, 1.2))
    b.append(arrow_head(488, 292, "up", INK2, 6))
    b.append(text(392, 372, "token 流（SSE）回到 LB", 11, MUTED))

    # KV arrow P -> D
    b.append(line(635, 210, 635, 292, BLUE, 4))
    b.append(arrow_head(635, 300, "down", BLUE, 12))
    b.append(text(648, 250, "KV 同机拷贝", 13, INK, weight=600))
    b.append(text(648, 268, "不出这台机器", 12, INK2))

    # sidecars
    box(b, 752, 132, 160, 78, "注册 sidecar", ["健康才注册到 Router，", "退出时先摘掉"], fill=PANEL)
    box(b, 752, 228, 160, 150, "nvlink-proxy", ["sidecar，仅 5090", "看得见所有卡", "替 P 把 KV 拷给 D", "每对卡 P2P 自检，", "不过就走主机内存"], fill=PANEL)

    # bottom: the two same-node transfer paths
    y = 474
    box(
        b, 24, y, 440, 124, "B300：FABRIC 直写",
        [
            "D 的 KV 池用 FABRIC 内存分配并导出句柄（IMEX）",
            "P 导入后，一个 gather kernel 直接写进 D 的页",
            "2048 条散落的行 0.47 ms；上游逐块拷贝约 296 ms",
            "跨机或自检失败时退回 TCP（慢但对）",
        ],
        fill=PANEL, stroke=BORDER,
    )
    box(
        b, 488, y, 440, 124, "RTX 5090：nvlink-proxy",
        [
            "sidecar 不申请 GPU，NVIDIA_VISIBLE_DEVICES=all",
            "替两边打开 CUDA IPC 句柄，走 PCIe P2P（~50 GB/s）",
            "坏掉的卡对改走 pinned 主机内存中转",
            "端到端 KV 校验：对不上就中止这个请求",
        ],
        fill=PANEL, stroke=BORDER,
    )
    write(
        "architecture",
        svg_doc(
            W, H, b, "PD 部署架构：Router 后面挂固定的 1P1D 单元",
            "TTS 引擎把请求发给 Router，Router 按会话亲和分发到多个单元，KEDA 按 decode 在途路数扩缩单元。"
            "每个单元是一个 Pod：Rust 写的 pd-lb 同时把请求发给 Prefill 和 Decode，Prefill 把 KV 在同一台机器上拷给 Decode，"
            "Decode 把 token 流回 LB。B300 上 Prefill 通过 FABRIC 句柄直接写 Decode 的 KV 池；5090 上由 nvlink-proxy sidecar 代做 P2P 拷贝。",
        ),
    )


# --------------------------------------------------------------------------
# figure 2: hardware constraints


def gpu_row(b, x, y, n, label, w=50, gap=8, fill="#ffffff"):
    for i in range(n):
        gx = x + i * (w + gap)
        b.append(rect(gx, y, w, 34, fill, rx=5, stroke=INK2, sw=1))
        b.append(text(gx + w / 2, y + 22, label, 12, INK, anchor="middle", weight=600))


def status_mark(b, x, y, ok, label):
    color = GOOD if ok else CRITICAL
    glyph = "✓" if ok else "✗"
    b.append(text(x, y, glyph, 14, color, weight=700))
    b.append(text(x + 18, y, label, 12, INK2))


def cluster_panel(b, x, title, gpu, inlink, inlink_note, crosslink, crossnote, marks):
    w = 440
    gw, gap = 50, 8
    b.append(rect(x, 80, w, 380, PANEL, rx=10))
    b.append(text(x + 16, 106, title, 15, INK, weight=600))
    for k, ny in enumerate([126, 300]):
        b.append(rect(x + 16, ny, w - 32, 110, "#ffffff", rx=8, stroke=BORDER))
        b.append(text(x + 28, ny + 20, f"节点 {'AB'[k]}（8 卡，画了 4 张）", 12, MUTED))
        gx0 = x + 32
        gpu_row(b, gx0, ny + 62, 4, gpu, gw, gap)
        c0 = gx0 + gw / 2
        c3 = c0 + 3 * (gw + gap)
        b.append(line(c0, ny + 48, c3, ny + 48, BLUE, 3))
        for i in range(4):
            cx = c0 + i * (gw + gap)
            b.append(line(cx, ny + 48, cx, ny + 62, BLUE, 3))
        if k == 0:
            lx = gx0 + 4 * (gw + gap) + 8
            b.append(text(lx, ny + 74, inlink, 12, INK, weight=600))
            b.append(text(lx, ny + 92, inlink_note, 12, INK2))
    # cross-node link
    b.append(line(x + 110, 236, x + 110, 300, MUTED, 1.5))
    b.append(text(x + 124, 262, crosslink, 12, INK, weight=600))
    b.append(text(x + 124, 280, crossnote, 12, INK2))
    yy = 438
    xx = x + 20
    for ok, label in marks:
        status_mark(b, xx, yy, ok, label)
        xx += 18 + tw(label, 12) + 20


def fig_hardware():
    W, H = 960, 700
    b = []
    b.append(text(24, 34, "我们手里的硬件：同机快，跨机慢一到两个数量级", 18, INK, weight=600))
    b.append(text(24, 58, "延迟都是搬 2048 行 KV（一个 2k token 的 prompt，约 288 MiB）的实测 p50。", 13, INK2))
    cluster_panel(
        b, 24, "RTX 5090 集群", "5090", "PCIe P2P ≈ 50 GB/s", "2048 行 5.6 ms",
        "25 GbE ≈ 3 GB/s", "2048 行 104 ms（TCP 和 RoCE 一样，线速封顶）",
        [(False, "没有 NVLink"), (False, "没有 GPUDirect RDMA")],
    )
    cluster_panel(
        b, 496, "B300 机器", "B300", "NVLink（机内）", "2048 行 0.54 ms",
        "Pod 网络 ≈ 3.4 GB/s", "2048 行 85 ms（只有 TCP 能用）",
        [(False, "8 张 CX-8 网卡没接线"), (False, "RoCE 没暴露给 Pod")],
    )

    # bottom: the four numbers as bars
    y0 = 500
    b.append(text(24, y0, "同一份 KV，同机 vs 跨机", 15, INK, weight=600))
    rows = [
        ("B300 同机（NVLink）", 0.54),
        ("5090 同机（PCIe P2P）", 5.58),
        ("B300 跨机（Pod 网络 TCP）", 85.2),
        ("5090 跨机（25 GbE）", 103.9),
    ]
    x0, x1 = 260, 860
    sx = scale(0, 120, x0, x1)
    top = y0 + 20
    row = 34
    bottom = top + row * len(rows)
    for t in [0, 30, 60, 90, 120]:
        b.append(line(sx(t), top, sx(t), bottom, GRID if t else AXIS, 1))
        b.append(text(sx(t), bottom + 18, f"{t} ms", 12, MUTED, anchor="middle"))
    for i, (label, v) in enumerate(rows):
        yc = top + row * i + row / 2
        b.append(text(24, yc + 5, label, 13, INK))
        b.append(hbar(x0, yc - 9, max(sx(v) - x0, 1.5), 18, BLUE))
        lab = f"{v:g} ms"
        b.append(text(max(sx(v), x0 + 1.5) + 8, yc + 5, lab, 12, INK2))
    write(
        "hardware",
        svg_doc(
            W, H, b, "硬件约束：同机与跨机的 KV 传输",
            "5090 集群：机内 PCIe P2P 约 50 GB/s，搬 2048 行 KV 5.6 ms；跨机 25 GbE 约 3 GB/s，104 ms；没有 NVLink，没有 GPUDirect RDMA。"
            "B300 机器：机内 NVLink 0.54 ms；跨机只能走约 3.4 GB/s 的 Pod 网络，85 ms；CX-8 网卡没接线，RoCE 没暴露给 Pod。",
        ),
    )


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    fig_architecture()
    fig_hardware()
    fig_ttfa()
    fig_stutter()
    fig_waterfall()
    fig_startup()
