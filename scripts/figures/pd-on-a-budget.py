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
# data: 5090 load test, mono (1 GPU) vs PD 1P+1D (2 GPUs), same image, replay
# of the production traffic mix. "Stutter" = share of streams whose playback
# had a gap. E2E TTFA = time to the first audio chunk, convolved with the TTS
# engine's other stages.

MONO_X = [2, 4, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40]
MONO_P95 = [289, 296, 325, 327, 336, 365, 347, 401, 427, 459, 452, 507]
MONO_GAP = [0.00, 0.00, 0.12, 0.19, 0.00, 0.38, 0.32, 0.73, 5.33, 12.80, 19.28, 54.02]

PD_X = [2, 4, 8, 16, 24, 32, 40, 44, 48, 56, 64]
PD_P95 = [300, 290, 304, 328, 361, 392, 406, 457, 451, 506, 487]
PD_GAP = [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.38, 17.78, 40.07, 49.87]


def scale(d0, d1, r0, r1):
    return lambda v: r0 + (v - d0) * (r1 - r0) / (d1 - d0)


# --------------------------------------------------------------------------
# figure: TTFA p95 vs concurrency


def fig_ttfa():
    W, H = 960, 450
    b = []
    b.append(text(24, 34, "首段音频时间（TTFA p95）", 18, INK, weight=600))
    b.append(text(24, 58, "同一次压测。单体 = 1 张卡，PD 1P1D = 2 张卡。越低越好。", 13, INK2))
    b += legend(24, 90, [("PD 1P1D（2 卡）", BLUE, "line"), ("单体（1 卡）", ORANGE, "line")])
    x0, x1, top, bottom = 80, 920, 130, 380
    sx = scale(0, 64, x0, x1)
    sy = scale(200, 600, bottom, top)
    for t in [200, 300, 400, 500, 600]:
        y = sy(t)
        b.append(line(x0, y, x1, y, GRID if t != 200 else AXIS, 1))
        b.append(text(x0 - 8, y + 4, f"{t} ms", 12, MUTED, anchor="end"))
    for t in [0, 8, 16, 24, 32, 40, 48, 56, 64]:
        b.append(text(sx(t), bottom + 18, str(t), 12, MUTED, anchor="middle"))
    for xs, ys, color in [(MONO_X, MONO_P95, ORANGE), (PD_X, PD_P95, BLUE)]:
        pts = [(sx(a), sy(c)) for a, c in zip(xs, ys)]
        b.append(polyline(pts, color))
        for px, py in pts:
            b.append(dot(px, py, color))
    b.append(text(sx(40) + 10, sy(507) - 8, "单体 40 路：507 ms", 12, INK2))
    b.append(text(sx(40) + 10, sy(406) + 20, "PD 40 路：406 ms", 12, INK2))
    b.append(text((x0 + x1) / 2, bottom + 40, "并发路数", 12, MUTED, anchor="middle"))
    write(
        "ttfa",
        svg_doc(
            W, H, b, "首段音频时间 p95 随并发的变化：单体与 PD 1P1D",
            "单体（1 卡）从 2 路到 40 路，TTFA p95 从 289 ms 涨到 507 ms；PD 1P1D（2 卡）从 2 路到 64 路，"
            "从 300 ms 涨到 487 ms。8 路以上，同样并发下 PD 都更低，40 路时 406 vs 507 ms。纵轴从 200 ms 起。",
        ),
    )


# --------------------------------------------------------------------------
# figure: stutter share, mono vs PD


def fig_stutter():
    W, H = 960, 430
    b = []
    b.append(text(24, 34, "多少路流会卡顿：单体 vs PD", 18, INK, weight=600))
    b.append(text(24, 58, "按线上真实请求的样子压测。单体 = 1 张卡，PD 1P1D = 2 张卡。", 13, INK2))
    b += legend(24, 90, [("PD 1P1D（2 卡）", BLUE, "bar"), ("单体（1 卡）", ORANGE, "bar")])
    x0, x1, top, bottom = 80, 920, 130, 360
    sy = scale(0, 60, bottom, top)
    for t in [0, 20, 40, 60]:
        y = sy(t)
        b.append(line(x0, y, x1, y, GRID if t else AXIS, 1))
        b.append(text(x0 - 8, y + 4, f"{t}%", 12, MUTED, anchor="end"))
    levels = [8, 16, 24, 32, 40]
    mono = dict(zip(MONO_X, MONO_GAP))
    pd = dict(zip(PD_X, PD_GAP))
    band = (x1 - x0) / len(levels)
    bw = 24
    for i, lv in enumerate(levels):
        cx = x0 + band * (i + 0.5)
        xa = cx - bw - 1  # PD
        xb = cx + 1  # mono, 2px surface gap between the pair
        hp = bottom - sy(pd[lv])
        hm = bottom - sy(mono[lv])
        b.append(vbar(xa, bottom, bw, hp, BLUE))
        b.append(vbar(xb, bottom, bw, hm, ORANGE))
        b.append(text(xa + bw / 2, bottom - hp - 7, "0", 12, INK2, anchor="middle"))
        lab = f"{mono[lv]:.2f}%" if mono[lv] < 1 else f"{mono[lv]:.1f}%"
        b.append(text(xb + bw / 2, bottom - hm - 7, lab, 12, INK2, anchor="middle"))
        b.append(text(cx, bottom + 20, f"{lv} 路", 13, INK2, anchor="middle"))
    b.append(text(24, H - 16, "PD 到 40 路都是 0 卡顿；单体 8 路就开始有流卡顿。", 12, MUTED))
    write(
        "stutter",
        svg_doc(
            W, H, b, "卡顿流占比：单体与 PD 1P1D",
            "在 8、16、24、32、40 路时，单体（1 卡）卡顿流占比为 0.12%、0.32%、5.33%、19.28%、54.02%；"
            "PD 1P1D（2 卡）全部为 0。",
        ),
    )


# --------------------------------------------------------------------------
# figure: waterfall of the slowest 1% (B300 1P1D replay, steady state)

WATERFALL = [
    # (stage, note, ms): means over the slowest 1% up to the first audio chunk; they add up to 392 ms.
    ("客户端 → LB → Prefill", "网络 + LB 解析和转发", 3.2),
    ("Prefill 接收与调度准入", "交给调度器、反序列化、排队；后来用紧凑数组传 prompt", 86.1),
    ("Prefill 前向", "含冷热请求同批造成的队头阻塞", 58.2),
    ("KV 传输链", "等 D 的页表、发送排队、拷贝、通知", 21.0),
    ("Decode 接入", "发现传输完成、提交、等下一步才入批", 21.5),
    ("Decode 到首段音频", "9 步解码；每步 GPU + 主机时间，后来开了 overlap", 199.6),
    ("Decode 输出 → LB → 客户端", "首段音频的最后一个 token 转发出去", 2.5),
]


def fig_waterfall():
    W, H = 960, 520
    b = []
    b.append(text(24, 34, "最慢的 1% 请求，时间都花在哪", 18, INK, weight=600))
    b.append(
        text(
            24, 58,
            "B300 1P1D，线上流量回放（7.8 万请求）。稳态下最慢 1% 请求到首段音频的分段均值，合计 392 ms。",
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
            "Decode 接入 21.5 ms，Decode 到首段音频 200 ms，输出转发 2.5 ms，合计 392 ms。",
        ),
    )


# --------------------------------------------------------------------------
# figure: architecture of one 1P1D unit


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
    box(b, 296, 196, 170, 96, "pd-lb", ["只转发给本单元的 P 和 D", "P、D 都健康才就绪", "退出前把在途流放完"])

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
    box(b, 752, 228, 160, 132, "nvlink-proxy", ["sidecar，仅 5090", "看得见所有卡", "替 P 把 KV 拷给 D", "每个单元独享一个"], fill=PANEL)

    # bottom: the two same-node transfer paths
    y = 474
    box(
        b, 24, y, 440, 124, "B300：FABRIC 直写",
        [
            "D 的 KV 池用 FABRIC 内存分配并导出句柄（IMEX）",
            "P 导入后，一个 gather kernel 直接写进 D 的页",
            "2048 条散落的行 0.47 ms；上游逐块拷贝约 296 ms",
            "跨机或 FABRIC 不可用时退回 TCP（慢但对）",
        ],
        fill=PANEL, stroke=BORDER,
    )
    box(
        b, 488, y, 440, 124, "RTX 5090：nvlink-proxy",
        [
            "sidecar 不申请 GPU，NVIDIA_VISIBLE_DEVICES=all",
            "替两边打开 CUDA IPC 句柄，走 PCIe P2P（~50 GB/s）",
            "每个单元一个，不再和同机的其他单元排队",
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
            "Decode 把 token 流回 LB。B300 上 Prefill 通过 FABRIC 句柄直接写 Decode 的 KV 池；5090 上由每个单元自己的 nvlink-proxy sidecar 代做 P2P 拷贝。",
        ),
    )


# --------------------------------------------------------------------------
# figure: hardware constraints


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
        [(False, "IB 卡没到位"), (False, "RoCE 没暴露给 Pod")],
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
            "B300 机器：机内 NVLink 0.54 ms；跨机只能走约 3.4 GB/s 的 Pod 网络，85 ms；IB 卡没到位，RoCE 没暴露给 Pod。",
        ),
    )


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    fig_architecture()
    fig_hardware()
    fig_ttfa()
    fig_stutter()
    fig_waterfall()
