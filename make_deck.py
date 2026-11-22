from __future__ import annotations

from pathlib import Path
from html import escape
import re


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "morphdream_ppt169_20261122"
SVG_DIR = PROJECT / "svg_output"
SVG_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1280, 720
BG = "#F8FAFC"
TEXT = "#253143"
MUTED = "#667085"
BLUE = "#1F4E9A"
BLUE_2 = "#DCE7F8"
BLUE_3 = "#EEF3FB"
GRAY = "#A8B0BA"
GRAY_2 = "#EEF2F7"
GRAY_3 = "#D6DCE5"
ROBOT = "#D8C5A7"
APPLE = "#D94343"
GREEN = "#4E8C70"
WHITE = "#FFFFFF"


def esc(s: str) -> str:
    return escape(str(s), quote=True)


def attrs(**kwargs) -> str:
    return " ".join(f'{k.replace("_", "-")}="{esc(v)}"' for k, v in kwargs.items())


def text(x, y, s, size=18, fill=TEXT, weight="normal", anchor="start", family="Source Han Sans SC", opacity=None):
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return f'<text x="{x}" y="{y}" font-family="{esc(family)}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{op}>{esc(s)}</text>'


def multiline(x, y, lines, size=18, fill=TEXT, line=1.35, weight="normal", family="Source Han Sans SC", anchor="start"):
    out = [f'<text x="{x}" y="{y}" font-family="{esc(family)}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">']
    for i, s in enumerate(lines):
        dy = 0 if i == 0 else size * line
        out.append(f'<tspan x="{x}" dy="{dy}">{esc(s)}</tspan>')
    out.append('</text>')
    return "".join(out)


def rect(x, y, w, h, fill=WHITE, stroke="none", sw=1, r=12, opacity=None, dash=None, rid=None):
    extra = ""
    if opacity is not None:
        extra += f' opacity="{opacity}"'
    if dash:
        extra += f' stroke-dasharray="{dash}"'
    if rid:
        extra += f' id="{rid}"'
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}/>'


def line(x1, y1, x2, y2, stroke=GRAY, sw=2, dash=None, marker=None, opacity=None):
    extra = ""
    if dash:
        extra += f' stroke-dasharray="{dash}"'
    if marker:
        extra += f' marker-end="url(#{marker})"'
    if opacity is not None:
        extra += f' opacity="{opacity}"'
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{extra}/>'


def circle(cx, cy, r, fill=WHITE, stroke="none", sw=1, opacity=None):
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{op}/>'


def polygon(points, fill=BLUE, stroke="none", sw=1, opacity=None):
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{op}/>'


def path(d, fill="none", stroke=BLUE, sw=2, dash=None, marker=None, opacity=None):
    extra = ""
    if dash:
        extra += f' stroke-dasharray="{dash}"'
    if marker:
        extra += f' marker-end="url(#{marker})"'
    if opacity is not None:
        extra += f' opacity="{opacity}"'
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}/>'


def small_label(x, y, s, fill=BLUE, bg=BLUE_3, width=None):
    width = width or max(72, 16 + 9.2 * len(s))
    return rect(x, y - 20, width, 26, bg, "none", r=13) + text(x + 12, y - 2, s, 13, fill, "bold")


def header(title, section, n, kicker=None):
    out = [rect(0, 0, W, H, BG, "none", r=0, rid="background"),
           rect(52, 38, 7, 54, BLUE, "none", r=3),
           text(76, 57, section.upper(), 12, BLUE, "bold", family="Inter"),
           text(76, 91, title, 29, TEXT, "bold"),
           text(1218, 61, f"{n:02d}", 15, BLUE, "bold", "end", "Inter")]
    if kicker:
        out.append(text(1218, 86, kicker, 11, MUTED, "normal", "end"))
    out.append(line(76, 112, 1204, 112, GRAY_3, 1))
    return "".join(out)


def footer(n, label="MorphAction · Protean Perception"):
    return line(76, 684, 1204, 684, GRAY_3, 1) + text(76, 705, label, 11, MUTED, family="Inter") + text(1204, 705, f"{n:02d} / 24", 11, MUTED, "normal", "end", "Inter")


def svg_wrap(body, role="content", n=None):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" lang="zh-CN" data-pptx-page-role="{role}" font-family="Source Han Sans SC">' + defs() + body + '</svg>'


def defs():
    return '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><polygon points="0,0 10,5 0,10" fill="#1F4E9A"/></marker><marker id="arrow-gray" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><polygon points="0,0 10,5 0,10" fill="#A8B0BA"/></marker></defs>'


def draw_robot(x, y, scale=1.0, form="quad", view=True, label=None):
    # warm beige, modular robot silhouette with gray joints and blue camera cone
    parts = []
    if form == "snake":
        for i in range(5):
            xx = x + i * 34 * scale
            yy = y + (4 if i % 2 else -2) * scale
            parts.append(rect(xx, yy, 34 * scale, 18 * scale, ROBOT, GRAY, 1.5, 7))
            if i < 4:
                parts.append(circle(xx + 34 * scale, yy + 9 * scale, 4 * scale, GRAY))
        hx, hy = x + 5 * 34 * scale + 3 * scale, y - 3 * scale
        parts += [rect(hx, hy, 22 * scale, 22 * scale, ROBOT, GRAY, 1.5, 6), circle(hx + 17 * scale, hy + 6 * scale, 3 * scale, BLUE)]
    elif form == "centaur":
        parts += [rect(x + 28 * scale, y - 30 * scale, 66 * scale, 30 * scale, ROBOT, GRAY, 1.5, 10), rect(x + 75 * scale, y - 62 * scale, 27 * scale, 32 * scale, ROBOT, GRAY, 1.5, 8), circle(x + 96 * scale, y - 52 * scale, 3 * scale, BLUE)]
        for dx in (35, 78):
            parts.append(line(x + dx * scale, y, x + (dx - 10) * scale, y + 42 * scale, GRAY, 5))
        parts.append(line(x + 48 * scale, y - 15 * scale, x + 93 * scale, y - 48 * scale, GRAY, 4))
    elif form == "periscope":
        parts += [rect(x, y, 64 * scale, 24 * scale, ROBOT, GRAY, 1.5, 8), rect(x + 23 * scale, y - 46 * scale, 18 * scale, 46 * scale, ROBOT, GRAY, 1.5, 6), rect(x + 17 * scale, y - 60 * scale, 42 * scale, 16 * scale, ROBOT, GRAY, 1.5, 6), circle(x + 52 * scale, y - 52 * scale, 3 * scale, BLUE)]
        parts += [line(x + 10 * scale, y + 24 * scale, x + 4 * scale, y + 45 * scale, GRAY, 5), line(x + 54 * scale, y + 24 * scale, x + 62 * scale, y + 45 * scale, GRAY, 5)]
    elif form == "hex":
        parts += [rect(x + 20 * scale, y - 22 * scale, 70 * scale, 26 * scale, ROBOT, GRAY, 1.5, 8), rect(x + 79 * scale, y - 44 * scale, 30 * scale, 24 * scale, ROBOT, GRAY, 1.5, 7), circle(x + 102 * scale, y - 36 * scale, 3 * scale, BLUE)]
        for dx in (25, 45, 72):
            parts.append(line(x + dx * scale, y + 2 * scale, x + (dx - 10) * scale, y + 35 * scale, GRAY, 4))
            parts.append(line(x + (dx + 20) * scale, y + 2 * scale, x + (dx + 28) * scale, y + 35 * scale, GRAY, 4))
    else:  # quad
        parts += [rect(x + 20 * scale, y - 28 * scale, 64 * scale, 30 * scale, ROBOT, GRAY, 1.5, 9), rect(x + 70 * scale, y - 55 * scale, 30 * scale, 28 * scale, ROBOT, GRAY, 1.5, 7), circle(x + 93 * scale, y - 47 * scale, 3 * scale, BLUE)]
        for dx in (30, 72):
            parts.append(line(x + dx * scale, y, x + (dx - 10) * scale, y + 34 * scale, GRAY, 5))
            parts.append(line(x + (dx + 20) * scale, y, x + (dx + 28) * scale, y + 34 * scale, GRAY, 5))
    if view:
        cx, cy = (x + 100 * scale, y - 47 * scale) if form in ("quad", "hex") else (x + 52 * scale, y - 52 * scale)
        parts.append(path(f"M {cx} {cy} L {cx + 108*scale} {cy - 34*scale} L {cx + 108*scale} {cy + 34*scale} Z", fill=BLUE_2, stroke=BLUE, sw=1, opacity=0.75))
    if label:
        parts.append(text(x + 50 * scale, y + 62 * scale, label, 14, TEXT, "bold", "middle"))
    return "".join(parts)


def draw_bed(x, y, scale=1.0, apple=True):
    out = [rect(x, y, 210 * scale, 24 * scale, GRAY, "none", r=4), rect(x + 12 * scale, y + 24 * scale, 190 * scale, 82 * scale, WHITE, GRAY, 2, 4), rect(x + 12 * scale, y + 24 * scale, 190 * scale, 18 * scale, GRAY_2, "none", r=3), line(x + 28 * scale, y + 106 * scale, x + 28 * scale, y + 132 * scale, GRAY, 5), line(x + 184 * scale, y + 106 * scale, x + 184 * scale, y + 132 * scale, GRAY, 5)]
    if apple:
        out += [circle(x + 112 * scale, y + 115 * scale, 10 * scale, APPLE), line(x + 112 * scale, y + 105 * scale, x + 116 * scale, y + 99 * scale, GREEN, 2)]
    return "".join(out)


def card(x, y, w, h, title, body_lines, accent=BLUE, icon=None, fill=WHITE, title_size=17, body_size=14):
    out = [rect(x, y, w, h, fill, GRAY_3, 1, 14), rect(x, y, 6, h, accent, "none", r=3)]
    if icon:
        out.append(circle(x + 28, y + 27, 13, BLUE_3 if accent == BLUE else GRAY_2, accent, 1))
        out.append(text(x + 28, y + 32, icon, 12, accent, "bold", "middle", "Inter"))
        tx = x + 52
    else:
        tx = x + 22
    out.append(text(tx, y + 30, title, title_size, TEXT, "bold"))
    out.append(multiline(tx, y + 58, body_lines, body_size, MUTED, 1.38))
    return "".join(out)


def bullet_list(x, y, items, width=520, size=17, gap=34, accent=BLUE):
    out=[]
    for i, s in enumerate(items):
        yy=y+i*gap
        out += [circle(x, yy-6, 4, accent), text(x+16, yy, s, size, TEXT)]
    return "".join(out)


def table(x, y, widths, headers, rows, row_h=42, font=13, header_fill=BLUE, highlight_row=None, alignments=None):
    out=[]
    total=sum(widths)
    out.append(rect(x, y, total, row_h, header_fill, "none", r=8))
    xx=x
    for i,h in enumerate(headers):
        out.append(text(xx+widths[i]/2, y+27, h, font, WHITE, "bold", "middle"))
        xx += widths[i]
    for r_idx,row in enumerate(rows):
        yy=y+row_h*(r_idx+1)
        fill=BLUE_3 if highlight_row==r_idx else (WHITE if r_idx%2==0 else GRAY_2)
        out.append(rect(x, yy, total, row_h, fill, GRAY_3, 0.6, 0))
        xx=x
        for c_idx,cell in enumerate(row):
            align = (alignments[c_idx] if alignments and c_idx < len(alignments) else "start")
            tx=xx+10 if align=="start" else xx+widths[c_idx]/2
            color=BLUE if str(cell)=="✓" else (MUTED if str(cell) in ("✗","—") else TEXT)
            weight="bold" if (highlight_row==r_idx or str(cell) in ("✓","✗")) else "normal"
            out.append(text(tx, yy+27, cell, font, color, weight, align))
            xx += widths[c_idx]
    return "".join(out)


def formula_block(x, y, w, h, latex, preview, font_size=30):
    safe_latex = latex.replace('\\', '\\\\').replace('"', '\\"')
    meta = '{"latex":"' + safe_latex + '","display":"block","font_size":' + str(font_size) + ',"color":"#253143","align":"center"}'
    return f'<g id="formula" data-pptx-replace-with="formula" data-pptx-x="{x}" data-pptx-y="{y}" data-pptx-width="{w}" data-pptx-height="{h}" data-pptx-bounds="{x} {y} {w} {h}"><metadata type="application/json"><![CDATA[{meta}]]></metadata>{text(x+w/2, y+h*0.68, preview, font_size, TEXT, "normal", "middle", "Cambria Math")}</g>'


def radar(cx, cy, r, values, labels=None):
    pts=[]; n=len(values)
    for i,v in enumerate(values):
        a=-3.14159/2 + i*2*3.14159/n
        pts.append(f"{cx + r*v*__import__('math').cos(a):.1f},{cy + r*v*__import__('math').sin(a):.1f}")
    outline=[]
    for i in range(n):
        a=-3.14159/2+i*2*3.14159/n
        outline.append(f"{cx+r*__import__('math').cos(a):.1f},{cy+r*__import__('math').sin(a):.1f}")
    out=[polygon(" ".join(outline), "none", GRAY_3, 1), polygon(" ".join(pts), BLUE_2, BLUE, 1.5)]
    for i in range(n):
        a=-3.14159/2+i*2*3.14159/n
        out.append(line(cx,cy,cx+r*__import__('math').cos(a),cy+r*__import__('math').sin(a),GRAY_3,1))
    return "".join(out)


def write_slide(n, body, role="content"):
    (SVG_DIR / f"slide_{n:02d}.svg").write_text(svg_wrap(body, role, n), encoding="utf-8")


def make_slides():
    # P01
    b = rect(0,0,W,H,BG,"none",r=0) + rect(0,0,18,H,BLUE,"none",r=0)
    b += small_label(86, 72, "组会 / 开题汇报", BLUE, BLUE_3, 118)
    b += text(86, 182, "梦蝶：为看见而物化", 52, TEXT, "bold")
    b += text(90, 232, "可重构机器人的跨形态主动视觉搜索", 26, BLUE, "bold")
    b += text(90, 273, "Protean Perception  ·  MorphAction", 18, MUTED, "normal", family="Inter")
    b += line(90, 320, 470, 320, BLUE, 3)
    b += text(90, 370, "机器人能看到什么，取决于它的身体。", 22, TEXT, "bold")
    b += text(90, 408, "因此，选择用什么身体去看，本身就是一个感知决策。", 18, MUTED)
    b += text(90, 604, "目标会议  ICML 2027", 16, TEXT, "bold")
    b += text(90, 632, "2026 年 11 月 22 日  ·  汇报人与单位留空", 14, MUTED)
    b += draw_bed(730, 440, 1.55) + draw_robot(635, 438, 1.55, "quad", True)
    b += circle(1110, 130, 28, BLUE_3, BLUE, 1.2) + text(1110, 138, "✦", 22, BLUE, "bold", "middle", "Inter")
    b += text(1110, 171, "物化", 13, BLUE, "bold", "middle")
    write_slide(1,b,"cover")

    # P02
    b = header("同一个目标，换一具身体才看得见", "问题直觉", 2)
    xs=[76,438,800]
    titles=["清醒：看不到","梦：跨形态想象","变形并验证"]
    for i,x in enumerate(xs):
        b += rect(x, 152, 324, 380, WHITE, GRAY_3, 1, 16) + small_label(x+22, 190, titles[i], BLUE if i==1 else TEXT, BLUE_3 if i==1 else GRAY_2, 112 if i!=1 else 136)
    b += draw_bed(120, 340, 0.9) + draw_robot(103, 340, 0.9, "quad", True)
    b += text(238, 486, "床沿挡住视线", 16, MUTED, "bold", "middle") + text(238, 512, "苹果仍在床底", 14, APPLE, "normal", "middle")
    b += circle(600, 300, 78, BLUE_3, BLUE, 1.2) + text(600, 276, "梦", 30, BLUE, "bold", "middle") + text(600, 309, "试用三种身体", 15, TEXT, "bold", "middle")
    for px,py,form,ok in [(532,390,"snake",True),(602,390,"centaur",False),(674,390,"periscope",None)]:
        b += draw_robot(px,py,0.45,form,False) + text(px+25, 455, "✓" if ok else ("✗" if ok is False else "部分"), 18, GREEN if ok else (APPLE if ok is False else BLUE), "bold", "middle", "Inter")
    b += draw_bed(842, 340, 0.9) + draw_robot(836, 425, 0.9, "snake", True)
    b += text(962, 486, "真实相机照到苹果", 16, GREEN, "bold", "middle")
    b += text(640, 589, "想象只用于决定下一步做什么，绝不当作证据写进记忆。", 16, BLUE, "bold", "middle")
    b += footer(2)
    write_slide(2,b)

    # P03
    b = header("机器人需要把变形当作感知决策", "问题定义", 3)
    b += small_label(76, 150, "三个子问题", BLUE, BLUE_3, 104)
    qs=[("01","用哪种形态去感知？"),("02","每种形态怎么感知？"),("03","何时变形、怎么变过去？")]
    for i,(num,q) in enumerate(qs):
        yy=205+i*84
        b += rect(76,yy,360,62,WHITE,GRAY_3,1,12)+circle(110,yy+31,19,BLUE)+text(110,yy+37,num,12,WHITE,"bold","middle","Inter")+text(150,yy+38,q,18,TEXT,"bold")
    b += rect(500, 150, 704, 220, BLUE, "none", r=18) + text(536, 194, "核心主张", 14, BLUE_2, "bold")
    b += multiline(536, 246, ["重构身体是一种信息采集动作。", "它抬高的是“能获得哪些证据”的上限。", "更多思考和更好视点规划都无法替代这一上限。"], 23, WHITE, 1.42, "bold")
    claims=[("C1","存在性","变形扩展可见集合"),("C2","归因","区分位姿受限与身体受限"),("C3","决策","知道何时变、变成什么、何时不变"),("C4","物理","代价与稳定性来自实测")]
    for i,(c,t,d) in enumerate(claims):
        x=500+i*176
        b += rect(x, 420, 160, 118, WHITE, GRAY_3, 1, 12)+text(x+16,454,c,14,BLUE,"bold","start","Inter")+text(x+16,480,t,16,TEXT,"bold")+multiline(x+16,507,[d],13,MUTED,1.3)
    b += footer(3)
    write_slide(3,b)

    # P04
    b = header("多项研究把瓶颈指向身体带来的观测限制", "相关工作", 4)
    cards=[("TVRBench","2026 预印本",["只转头时尚可；需要移动身体时显著下降","最好闭源模型成功率只有 12%"],"12%"),("PhysVLM-AVR / Theory of Space","NeurIPS 2025 · ICLR 2026",["模型能察觉信息缺失，却难主动获取","自行探索反而比直接给观测更差"],"缺失"),("VLN-PE","ICCV 2025",["同一导航模型跨人形、四足、轮式性能下降","受限观测空间是原因之一"],"跨具身"),("相机高度研究","2020",["高相机整体视野更好","地面柜内目标由低相机更有利"],"高度")]
    for i,(t,sub,lines,badge) in enumerate(cards):
        x=76+(i%2)*564; y=152+(i//2)*210
        b += card(x,y,532,178,t,[sub]+lines,BLUE if i in (0,2) else GRAY, badge, WHITE, 17, 14)
    b += text(76, 602, "共同指向", 15, BLUE, "bold") + text(170, 602, "观测空间由身体决定，现有模型很难跨越这一限制。", 18, TEXT, "bold")
    b += footer(4)
    write_slide(4,b)

    # P05
    b = header("真正的难点是判断何时换、换成什么、值不值得", "挑战", 5)
    challenges=[("01","代价地形随身体改变","可达性、成像质量和代价同时变化"),("02","回报取决于信念且边际递减","看过的地方不再提供新信息"),("03","能力耦合","P(m) ⊂ P，视点变多也可能动作变少"),("04","变形有真实代价","耗时、跌倒、过渡失败，系统要会不变形"),("05","感知运动协调不同","稳像、步态相位与自遮挡随形态变化"),("06","新形态要即插即用","新增形态不能要求重新训练")]
    for i,(num,t,d) in enumerate(challenges):
        x=76+(i%3)*378; y=150+(i//3)*214
        b += card(x,y,344,170,t,[d],BLUE if i in (2,3) else GRAY, num, WHITE, 16, 14)
    b += small_label(76, 596, "护城河", BLUE, BLUE_3, 78) + text(168, 596, "能力耦合  ·  真实代价  ·  会选择不变形", 17, TEXT, "bold")
    b += footer(5)
    write_slide(5,b)

    # P06
    b = header("现有工作尚未同时满足感知驱动重构的六个条件", "相关工作", 6)
    headers=["工作类别","位姿可动","构型在线改变","为感知改变","能力耦合","实测代价","会不变形"]
    rows=[
        ["主动视觉 / 具身问答","✓","✗","—","✗","✗","✗"],
        ["视点 / 变焦基准","✓","✗","—","✗","✗","✗"],
        ["变形机器人（为运动）","✗","✓","✗","部分","部分","✗"],
        ["在线变形强化学习","✗","✓","✗","✗","✗","✗"],
        ["感知驱动重构（Daudelin 2018）","✓","✓","✗","✗","✗","✗"],
        ["姿态服务感知（POSE）","✓","仅姿态","✓","✗","✗","✗"],
        ["设计期可见—可达（VRW）","—","设计期","✓","✓","✗","—"],
        ["跨具身基础模型","—","视为干扰","✗","✗","✗","✗"],
        ["本项目","✓","✓","✓","✓","✓","✓"],
    ]
    b += table(76, 145, [318,122,140,122,112,112,112], headers, rows, 44, 12, BLUE, 8, ["start","middle","middle","middle","middle","middle","middle"])
    b += text(76, 610, "RING、NavFoM、X-VLA 等跨具身模型把身体差异当作泛化干扰。", 15, MUTED) + text(76, 636, "本项目把身体差异当作可利用的感知资源。", 17, BLUE, "bold")
    b += footer(6)
    write_slide(6,b)

    # P07
    b = header("最接近的工作仍把形态当作运动或姿态工具", "相关工作", 7)
    headers=["工作","它做了什么","我们的区别"]
    rows=[
        ["Daudelin 等，Science Robotics 2018","先感知环境，再选构型执行任务","为获取证据而变形，并计入机动性代价"],
        ["Learning to Reconfigure，ICML 2026","为跨越地形而切换，只看本体状态","由视觉证据触发切换"],
        ["POSE，2026 预印本","调节俯仰、横滚扩大覆盖","改变接触模式和可达动作"],
        ["VRW，2026 预印本","设计期提出可见—可达指标","任务进行中的在线选择"],
        ["EMOS，ICLR 2025","在多台机器人间分配任务","在一台机器人的多种形态间选择"],
        ["Pathak 2019 / DittoGym 2024","任务中在线改变形态","目标是运动，本文目标是感知证据"],
    ]
    b += table(76, 148, [280,410,434], headers, rows, 60, 13, BLUE, None, ["start","start","start"])
    b += small_label(76, 610, "审稿人问题", BLUE, BLUE_3, 102) + text(190,610,"Daudelin 已做过感知驱动重构，POSE 也用姿态做感知。",16,TEXT,"bold")
    b += footer(7)
    write_slide(7,b)

    # P08
    b = header("形态决定视点代价地形，重构在地形之间跳转", "核心思想", 8)
    b += rect(76, 150, 620, 390, WHITE, GRAY_3, 1, 16)
    b += text(108, 188, "同一房间，不同形态看到不同区域", 17, TEXT, "bold")
    b += rect(116, 285, 180, 96, GRAY_2, GRAY, 1, 6) + text(206, 340, "床 / 柜", 18, MUTED, "bold", "middle")
    b += draw_robot(154, 286, 0.7, "quad", True) + draw_robot(410, 423, 0.7, "snake", True)
    b += text(201, 463, "四足：台面可见", 15, TEXT, "bold", "middle") + text(455, 493, "蛇形：床底可见", 15, BLUE, "bold", "middle")
    b += circle(580,255,10,BLUE) + text(580,260,"",10)
    b += text(108, 506, "每个视点都同时决定", 15, BLUE, "bold") + text(108, 532, "能否到达 · 成像质量 · 代价", 18, TEXT, "bold")
    b += rect(748, 150, 456, 390, BLUE, "none", r=16)
    b += text(784, 190, "庄周梦蝶的三个关键词", 17, BLUE_2, "bold")
    for i,(t,d) in enumerate([("物化","形态之间可以转化"),("梦","变形前先以另一具身体看一眼"),("梦醒之分","想象不等于证据")]):
        yy=260+i*80
        b += circle(810, yy-8, 18, WHITE) + text(810, yy-2, str(i+1), 13, BLUE, "bold", "middle", "Inter") + text(850, yy-4, t, 20, WHITE, "bold") + text(850, yy+25, d, 15, BLUE_2)
    b += text(76, 592, "视觉是在对光场采样，形态是可重构的视点代价地形。", 18, TEXT, "bold")
    b += footer(8)
    write_slide(8,b)

    # P09
    b = header("三层动作共同追求最短时间获得足够证据", "问题形式化", 9)
    b += small_label(76, 152, "任务", BLUE, BLUE_3, 58) + text(150,152,"在未知室内场景中搜索语言描述的目标，直到获得满足要求的视觉证据。",16,TEXT,"bold")
    layers=[("形态层","切换形态，代价来自履历",BLUE),("注意力层","裁剪、放大、回看",GRAY),("视点层","移动、转向、注视",GRAY)]
    for i,(t,d,c) in enumerate(layers):
        y=230+i*72
        b += rect(76+i*30,y,340-i*30,54,c,"none",r=10)+text(100+i*30,y+23,t,16,WHITE if c==BLUE else TEXT,"bold")+text(100+i*30,y+43,d,12,WHITE if c==BLUE else MUTED)
    b += formula_block(520, 196, 640, 100, r"\min_{\pi}\ \mathbb{E}[T_{evidence}+T_{think}+\lambda_F\mathbb{1}[fall]]", "minπ E[T_evidence + T_think + λF·1[fall]]", 30)
    b += rect(520, 330, 310, 220, BLUE_3, "none", r=14) + rect(850,330,310,220,GRAY_2,"none",r=14)
    b += text(548, 364, "必须保留", 16, BLUE, "bold") + text(878, 364, "可以简化", 16, MUTED, "bold")
    b += bullet_list(548, 403, ["形态之间互补","看哪里取决于已看到什么","过渡有真实代价","存在强基线","想象只能用自身记忆"], 270, 14, 29, BLUE)
    b += bullet_list(878, 403, ["固定拓扑，不做对接","模板由人给定","经典步态加感知调制","静态场景、单目标","深度加语义观测"], 270, 14, 29, GRAY)
    b += footer(9)
    write_slide(9,b)

    # P10
    b = header("梦蝶闭环让每一步都经历提议、想象与择优", "方法总览", 10)
    b += text(78, 148, "Agent loop", 15, BLUE, "bold", family="Inter") + text(960,148,"Memory",15,BLUE,"bold",family="Inter")
    modules=[("a","证据需求解析"),("b","感知瓶颈诊断"),("c","动作提议"),("d","跨形态想象评估"),("e","执行与验证")]
    for i,(k,t) in enumerate(modules):
        y=180+i*70; fill=BLUE if k=="d" else WHITE; stroke=BLUE if k=="d" else GRAY_3; col=WHITE if k=="d" else TEXT
        b += rect(276,y,520,48,fill,stroke,1,12)+circle(306,y+24,14,WHITE if k=="d" else BLUE)+text(306,y+29,k,13,BLUE if k=="d" else WHITE,"bold","middle","Inter")+text(338,y+30,t,17,col,"bold")
        if i<4: b += line(536,y+48,536,y+70,BLUE,2,"", "arrow")
    b += line(796, 492, 240, 492, BLUE, 2, "6 5", "arrow") + text(470, 484, "re-plan every step", 12, BLUE, "bold", "middle", "Inter")
    memories=[("场景记忆","占据、语义、目标假设"),("情景记忆","动作、观测、失败案例"),("形态履历","可达位姿、稳定性、过渡")]
    for i,(t,d) in enumerate(memories):
        y=182+i*114
        b += rect(896,y,308,82,GRAY_2,GRAY_3,1,12)+text(920,y+30,t,16,TEXT,"bold")+text(920,y+56,d,13,MUTED)
        b += line(896,y+41,796,y+41,GRAY,1.5,"4 4","arrow-gray")
    b += rect(76, 580, 1128, 46, BLUE_3, "none", r=12) + text(640, 610, "L1 身体层：步态（CPG）+ 感知调制（注视 · 速度 · 停顿 · 姿态）", 16, BLUE, "bold", "middle")
    b += text(838, 526, "想象 ✗ 记忆", 13, APPLE, "bold", "middle")
    b += line(796, 492, 896, 222, APPLE, 1.5, "5 5")
    b += footer(10)
    write_slide(10,b)

    # P11
    b = header("一具模块化超集机器人覆盖五种视觉生态位", "实验平台", 11)
    b += text(76, 148, "装配体：4 节脊柱模块 · 3 对三自由度腿 · 深度相机与颈部模块 · 拓扑固定", 15, MUTED)
    forms=[("六足","中等高度 · 最稳","hex"),("四足","中等高度 · 转场快","quad"),("人马形","高视点 · 独立注视","centaur"),("蛇形","最低最窄 · 进床底","snake"),("潜望","身体留在窄处","periscope")]
    for i,(name,desc,form) in enumerate(forms):
        x=82+i*226
        b += rect(x, 190, 202, 274, WHITE, GRAY_3,1,14)+small_label(x+18,220,name,BLUE,BLUE_3,72)+draw_robot(x+46, 340, 0.75, form, True)+text(x+101, 404, desc, 13, MUTED, "bold", "middle")
        b += line(x+28, 430, x+176, 430, GRAY_3, 1, "4 4") + text(x+101, 452, "相机高度定性示意", 11, MUTED, "normal", "middle")
    b += rect(76, 498, 1128, 94, BLUE_3, "none", r=12) + text(98, 530, "形态定义", 15, BLUE, "bold") + text(210,530,"锁定哪些关节 + 锁定角度 + 哪些肢体着地",18,TEXT,"bold") + text(98,566,"筛选路径",15,BLUE,"bold") + text(210,566,"先提议候选，再实测履历，最后选出覆盖藏匿类型且冗余最小的子集。",16,TEXT)
    b += footer(11)
    write_slide(11,b)

    # P12
    b = header("履历把能力耦合变成可即插即用的接口", "形态履历", 12)
    b += rect(76, 150, 640, 390, WHITE, GRAY_3,1,16)
    b += text(108, 186, "高层只通过履历认识身体", 18, TEXT, "bold")
    fields=["可达相机位姿","通过尺寸","步态速度","成像稳定性","注视自由度","自遮挡","过渡耗时与成功率","能耗与风险"]
    for i,f in enumerate(fields):
        x=110+(i%2)*276; y=235+(i//2)* sixty if False else 235+(i//2)*56
        b += circle(x, y-6, 4, BLUE) + text(x+14,y,f,15,TEXT)
    b += formula_block(770, 170, 360, 92, r"P(m) \subseteq P", "P(m) ⊂ P", 30)
    b += text(770, 310, "变形扩展一些视点，", 19, TEXT, "bold") + text(770, 340, "也收缩另一些动作。", 19, TEXT, "bold")
    b += text(770, 392, "可见—可达遮罩", 16, BLUE, "bold") + text(770, 423, "把形态能力交给提议器。", 17, TEXT, "bold")
    b += rect(770, 456, 362, 90, BLUE_3, "none", r=12) + text(800, 492, "EMOS 的机器人简历", 14, BLUE, "bold") + text(800, 520, "PhysVLM 的可达空间投影", 14, TEXT)
    b += footer(12)
    write_slide(12,b)

    # P13
    b = header("先诊断看不到的原因，再决定是否换身体", "瓶颈诊断", 13)
    headers=["可见性条件","不满足时的瓶颈","首选补救"]
    rows=[["视线无遮挡","遮挡","视点层；不可达时转形态层"],["目标在视场内","视场","转向、调整注视"],["分辨率足够","尺度","裁剪放大；或走近"],["视角合适","视角","换个角度"],["成像质量够好","模糊或抖动","停顿、稳像"],["补救视点可达","可达性","换成能到达的形态"]]
    b += table(76, 150, [260,360,336], headers, rows, 54, 14, BLUE, 5, ["start","start","start"])
    b += rect(820, 492, 384, 112, BLUE, "none", r=14) + text(850, 528, "触发形态层", 15, BLUE_2, "bold") + multiline(850, 558, ["补救视点不在当前形态可达集内，", "或另一形态代价低得多。"], 17, WHITE, 1.35, "bold")
    b += footer(13)
    write_slide(13,b)

    # P14
    b = header("分层想象在变形前估计证据增益", "想象评估", 14)
    b += formula_block(76, 142, 1128, 90, r"\operatorname{Gain}(m,v) \approx \sum_h p_t(h)P(visible\land identifiable\mid v,m,h)-\lambda\operatorname{Cost}(m,v)", "Gain(m,v) ≈ Σₕ pₜ(h)·P(可见且可识别 | v,m,h) − λ·Cost(m,v)", 24)
    tiers=[("第 0 层","几何光线投射","毫秒级，每个候选都算",GRAY),("第 1 层","结构先验","从家具类别和可见下沿估计间隙",BLUE),("第 2 层","生成式世界模型（可选）","只在决策胶着且涉及变形时使用",GRAY)]
    for i,(t,sub,d,c) in enumerate(tiers):
        x=76+i*378
        b += rect(x, 290, 344, 190, c if i==1 else WHITE, c if i==1 else GRAY_3,1,14)+text(x+22,326,t,17,WHITE if i==1 else TEXT,"bold")+text(x+22,362,sub,16,WHITE if i==1 else BLUE,"bold")+multiline(x+22,400,[d,"保守打分：未知空间取置信下界。"],14,BLUE_2 if i==1 else MUTED,1.45)
    b += text(76, 540, "评估器不需要训练，新形态的零样本能力来自公式结构本身。", 17, BLUE, "bold")
    b += footer(14)
    write_slide(14,b)

    # P15
    b = header("自适应贪心给出决策骨架，切换代价留下理论空间", "决策策略", 15)
    b += rect(76, 154, 480, 382, WHITE, GRAY_3,1,16)
    b += text(106, 190, "每步重新决策", 18, TEXT, "bold")
    steps=[("提议","4–8 个候选"),("想象","只在形态切换时两步前瞻"),("择优","按证据增益减代价")]
    for i,(t,d) in enumerate(steps):
        y=245+i*85
        b += circle(135,y,20,BLUE)+text(135,y+6,str(i+1),14,WHITE,"bold","middle","Inter")+text(174,y-4,t,17,BLUE,"bold")+text(174,y+24,d,14,MUTED)
        if i<2: b += line(135,y+20,135,y+65,BLUE,2,"", "arrow")
    b += rect(618,154,586,164,BLUE_3,"none",r=16)+text(650,190,"理论依据",16,BLUE,"bold")+multiline(650,228,["自适应次模性下，自适应贪心接近最优。","切换代价会破坏这一保证，留下理论切入点。"],18,TEXT,1.45,"bold")+text(650,286,"Golovin & Krause, JAIR 2011",13,MUTED,"normal","start","Inter")
    b += rect(618,340,586,196,GRAY_2,"none",r=16)+text(650,376,"自适应计算分配",16,TEXT,"bold")+text(650,414,"候选越接近、切换代价越大，就想得越多。",18,TEXT,"bold")
    b += line(650,478,1136,478,GRAY,2); b += line(650,478,650,424,BLUE,4); b += line(890,478,890,450,BLUE,4); b += line(1136,478,1136,390,BLUE,4)
    b += text(650,508,"候选差距大",12,MUTED) + text(1136,508,"变形之前多想想",12,BLUE,"bold","end")
    b += footer(15)
    write_slide(15,b)

    # P16
    b = header("大模型提议语义动作，几何模块验证最终选择", "系统分工", 16)
    headers=["模块","实现"]
    rows=[["证据需求解析","开源大语言模型"],["瓶颈诊断","视觉语言模型给语义线索，几何计算判断可见性与可达性"],["动作提议","视觉语言模型做结构化思维链，输入记忆摘要与遮罩"],["证据增益评估","几何想象、结构先验和履历，不用大模型"],["执行验证","仿真真值加噪声；开放词汇检测器或视觉语言模型"],["情景记忆（可选）","借鉴 Reflexion，把失败反馈写成文字经验"]]
    b += table(76, 150, [250, 878], headers, rows, 58, 14, BLUE, 3, ["start","start"])
    b += rect(76, 588, 1128, 54, BLUE, "none", r=12) + text(640, 621, "原则：大模型不进入控制回路，也不独自做最终决策。", 18, WHITE, "bold", "middle")
    b += footer(16)
    write_slide(16,b)

    # P17
    b = header("MuJoCo Warp 与 MolmoSpaces 构成可控验证平台", "实验环境", 17)
    b += card(76, 150, 354, 168, "仿真与渲染", ["MuJoCo Warp 在 A100 上批量仿真","GPU 批量渲染深度与分割图","Mac 负责开发调试"], BLUE, "01")
    b += card(462, 150, 354, 168, "场景规模", ["MolmoSpaces：23 万多个室内场景","13 万多个带元数据物体","按场景来源留出测试集"], BLUE, "02")
    b += card(848, 150, 356, 168, "观测与划分", ["深度图加语义掩码，叠加噪声","开发 / 验证 / 测试","另留一种形态做零样本"], BLUE, "03")
    b += text(76, 368, "五类藏匿位置", 18, TEXT, "bold")
    types=[("低矮缝隙","床底 / 沙发底"),("高处","柜顶 / 台面深处"),("遮挡物之后","被家具挡住"),("柜内低层","开放格内部"),("远处小目标","远距离小物体")]
    for i,(t,d) in enumerate(types):
        x=76+i*226
        b += rect(x, 405, 202, 142, WHITE, GRAY_3,1,14)+circle(x+101,448,25,BLUE_3,BLUE,1)+text(x+101,455,str(i+1),16,BLUE,"bold","middle","Inter")+text(x+101,496,t,15,TEXT,"bold","middle")+text(x+101,521,d,13,MUTED,"normal","middle")
    b += text(76, 594, "每类藏匿位置都应有一种形态是唯一高效的观察方式。", 17, BLUE, "bold")
    b += footer(17)
    write_slide(17,b)

    # P18
    b = header("基线覆盖身体约束、姿态调节和想象替代等解释", "基线设计", 18)
    headers=["基线","回答的质疑"]
    rows=[["最佳固定形态","重构是否必要"],["固定形态 + 连续姿态与注视（强基线）","姿态调节是否就够了"],["固定升级规则：视点 → 注意力 → 形态","证据增益决定何时变形是否更好"],["纯思维链智能体","几何想象是否必要"],["VLFM 式语义前沿探索","与现有语义搜索相比如何"],["只想象、不变形","想象能否替代真实变形"],["自由相机（上界）","是否只是换了个更高的相机"],["理想形态选择（上界）","离最优还有多远"],["训练版评估器","免训练能否追平训练"]]
    b += table(76, 148, [430, 774], headers, rows, 48, 14, BLUE, None, ["start","start"])
    b += text(76, 620, "两个上界行用来标定取舍，不替代真实身体约束下的决策。", 15, MUTED)
    b += footer(18)
    write_slide(18,b)

    # P19
    b = header("五组实验将四个科学主张映射到可检验指标", "实验计划", 19)
    headers=["实验","内容","对应主张"]
    rows=[["E1 主对比","全部藏匿类型上与基线比较","C1、C3"],["E2 零样本新形态","只提供履历","C3"],["E3 思考与身体扩展曲线","候选数、前瞻深度、形态库规模","C1"],["E4 切换何时值得","按类型、距离、代价统计不变形比例","C3"],["E5 消融","去掉诊断、结构先验、两步前瞻、梦醒分离","C2、C3"],["诊断准确率","位姿受限 vs 身体受限","C2"],["物理有效性","实测履历、跌倒率、过渡成功率","C4"]]
    b += table(76, 145, [220, 320, 146], headers, rows, 42, 11, BLUE, None, ["start","start","middle"])
    # schematic chart
    x0,y0=820,648; cw,ch=360,145
    b += rect(x0, y0-ch, cw, ch, WHITE, GRAY_3, 1, 10)
    b += text(x0+18, y0-ch+22, "预期结果（示意）", 14, APPLE, "bold")
    b += line(x0+42,y0-20,x0+42,y0-ch+42,GRAY,1) + line(x0+42,y0-20,x0+338,y0-20,GRAY,1)
    b += path(f"M {x0+42} {y0-48} C {x0+120} {y0-48}, {x0+160} {y0-50}, {x0+338} {y0-48}","none",GRAY,2)
    b += path(f"M {x0+42} {y0-66} C {x0+120} {y0-62}, {x0+190} {y0-66}, {x0+338} {y0-65}","none","#8FB2E6",2)
    b += path(f"M {x0+42} {y0-82} C {x0+120} {y0-70}, {x0+190} {y0-42}, {x0+338} {y0-32}","none",BLUE,3)
    b += text(x0+54,y0-4,"固定",11,MUTED) + text(x0+145,y0-4,"固定+姿态",11,"#5D7FAE") + text(x0+250,y0-4,"可重构（本项目）",11,BLUE,"bold")
    b += text(76, 654, "指标：成功率、获得证据用时（含思考）、切换次数、跌倒率、过渡失败率，至少 8 个随机种子。", 14, MUTED)
    b += footer(19)
    write_slide(19,b)

    # P20
    b = header("九周计划在 1 月 3 日用 G3 决定是否冲刺", "实施计划", 20)
    b += text(76, 148, "2026/11/23", 13, MUTED, "bold", family="Inter") + text(1184,148,"2027/01/22",13,MUTED,"bold","end","Inter")
    tasks=[("S0 基础设施与可行性验证",0,1), ("S1 超集机器人与身体层",0,2),("S2 履历与形态库",2,3),("S3 场景记忆与感知",1,3),("S4 瓶颈诊断与评估器",2,4),("S5 提议器与决策闭环",4,5),("S6 基线",4,5),("S7 实验与分析",5,7),("S8 论文支撑",6,8)]
    x0,y0=320,180; unit=92
    for i,(t,a,z) in enumerate(tasks):
        y=y0+i*42
        b += text(76,y+17,t,14,TEXT,"bold")
        b += line(x0,y+14,x0+8*unit,y+14,GRAY_3,10)
        b += line(x0+a*unit,y+14,x0+z*unit,y+14,BLUE,10)
    for i,g in enumerate([("G1","12/6",2),("G2","12/20",4),("G3","1/3",5),("G4","1/14",7)]):
        lab,date,pos=g; xx=x0+pos*unit
        b += line(xx, 165, xx, 570, BLUE if lab=="G3" else GRAY, 2, "6 5" if lab!="G3" else None)
        b += text(xx, 600, lab, 15, BLUE if lab=="G3" else TEXT, "bold", "middle", "Inter") + text(xx, 620, date, 12, MUTED, "normal", "middle", "Inter")
    b += rect(76, 642, 1128, 28, BLUE_3, "none", r=8) + text(640, 662, "G3：E1 初版超过强基线，决定是否冲刺 ICML 2027。", 14, BLUE, "bold", "middle")
    b += footer(20)
    write_slide(20,b)

    # P21
    b = header("每项主要风险都有对应的降级路径", "风险与对策", 21)
    headers=["风险","对策"]
    rows=[["距截稿只有约 9 周","先用三种形态跑通全流程，再补齐其余形态"],["多形态底层实现量大","经典步态加感知调制，不做端到端运动学习"],["想象在未知区域不准","结构先验加保守打分；生成式想象只用于复核"],["收益被连续姿态调节抵消","设为强基线；转为刻画何时重构值得"],["提示词与参数过拟合开发场景","严格数据划分，提前冻结提示词"],["大模型推理延迟","低频调用、缓存，并把思考时间计入耗时"]]
    b += table(76, 150, [400, 824], headers, rows, 64, 14, BLUE, None, ["start","start"])
    b += text(76, 630, "即使收益有限，“何时重构值得”本身也是可交付结论。", 16, BLUE, "bold")
    b += footer(21)
    write_slide(21,b)

    # P22
    b = rect(0,0,W,H,BG,"none",r=0)+rect(0,0,18,H,BLUE,"none",r=0)
    b += small_label(86, 74, "预期贡献", BLUE, BLUE_3, 92)
    b += text(86, 172, "项目贡献是让机器人", 40, TEXT, "bold") + text(86, 222, "为了看见而改变自己", 50, BLUE, "bold")
    contrib=[("新问题","把形态切换建模为信息采集动作"),("新方法","瓶颈与履历分解 + 跨形态想象 + 梦醒分离"),("新基准","多形态主动视觉搜索任务套件与评测协议"),("实证结论","思考替代不了身体，并给出何时不该变形的条件")]
    for i,(t,d) in enumerate(contrib):
        y=300+i*62
        b += circle(100,y-5,15,BLUE)+text(100,y+1,str(i+1),12,WHITE,"bold","middle","Inter")+text(136,y,t,17,TEXT,"bold")+text(256,y,d,16,MUTED)
    b += line(86, 584, 530, 584, BLUE, 3) + text(86, 626, "“此之谓物化”", 22, BLUE, "bold") + text(278, 626, "—— 为看见而改变自己", 18, TEXT, "bold")
    b += draw_bed(790, 430, 1.2)+draw_robot(756,429,1.15,"snake",True)+circle(1116,140,27,BLUE_3,BLUE,1)+text(1116,148,"✦",22,BLUE,"bold","middle","Inter")
    b += footer(22,"MorphAction · 谢谢大家，欢迎提问")
    write_slide(22,b,"ending")

    # B1
    b = header("人做判断题，编码智能体做实现题", "备份", 23, "BACKUP 01")
    b += rect(76, 150, 516, 418, WHITE, GRAY_3,1,16)+rect(632,150,572,418,BLUE_3,"none",r=16)
    b += text(108,190,"分工边界",18,TEXT,"bold")
    b += bullet_list(108,235,["人：形态模板、阈值、降级、冻结提示词、解读结果","编码智能体：代码、测试、实验、报告"],430,16,62,BLUE)
    b += text(664,190,"防泄漏规则写成代码和测试",18,BLUE,"bold")
    b += bullet_list(664,235,["想象模块不能读取仿真器状态","想象出的观测不能写入场景记忆","提示词冻结后带哈希","测试集评测需人工打开开关","每周五做一次集成测试"],500,16,54,BLUE)
    b += footer(23,"MorphAction · 备份")
    write_slide(23,b)

    # B2
    b = header("参考文献与工具支撑问题、方法和平台", "备份", 24, "BACKUP 02")
    refs=["Bajcsy et al. Revisiting active perception, Autonomous Robots 2018","Daudelin et al. Science Robotics 2018","Learning to Reconfigure, ICML 2026","Pathak et al. NeurIPS 2019 · DittoGym, ICLR 2024","EMOS, ICLR 2025 · PhysVLM, CVPR 2025","PhysVLM-AVR, NeurIPS 2025 · Theory of Space, ICLR 2026","VLN-PE, ICCV 2025 · TVRBench, arXiv 2026","POSE, arXiv 2026 · VRW, arXiv 2026","VLFM, ICRA 2024 · MindJourney, NeurIPS 2025","GenEx, ICLR 2025 · Reflexion, NeurIPS 2023","Golovin & Krause, JAIR 2011 · Kaelbling & Lozano-Pérez, IJRR 2013","MolmoSpaces, arXiv 2026 · MuJoCo Warp"]
    for i,r in enumerate(refs):
        x=76+(i%2)*574; y=150+(i//2)*72
        b += rect(x,y,536,54,WHITE,GRAY_3,1,10)+text(x+16,y+33,r,13,TEXT)
    b += footer(24,"MorphAction · 备份")
    write_slide(24,b)


if __name__ == "__main__":
    make_slides()
