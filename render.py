#!/usr/bin/env python3
"""Render entry.png for news-image-20261125 (Wednesday 25 November 2026).

Draws the whole image from the story data below with Pillow only.
Deterministic: fixed fonts, fixed layout, no timestamps, no network.
Run:  python3 render.py            -> writes entry.png next to this file
"""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
NAVY = (16, 39, 63)
NAVY_SOFT = (27, 58, 88)
INK = (24, 33, 45)
GREY = (90, 104, 122)
LIGHT_BG = (238, 242, 247)
CARD_BG = (255, 255, 255)
LINE = (203, 213, 225)
MAP_OCEAN = (232, 238, 245)
MAP_LAND = (195, 206, 219)
MAP_EDGE = (159, 176, 195)
WHITE = (255, 255, 255)

REGION_COLORS = {
    "Europe": (36, 86, 200),
    "Asia-Pacific": (14, 124, 107),
    "Middle East": (180, 83, 9),
    "Africa": (109, 40, 217),
    "North America": (185, 28, 28),
    "Latin America": (190, 24, 93),
    "Global": (71, 85, 105),
}
REGION_SHORT = {
    "Europe": "Europe",
    "Asia-Pacific": "Asia-Pacific",
    "Middle East": "Middle East",
    "Africa": "Africa",
    "North America": "N. America",
    "Latin America": "LatAm",
    "Global": "Global",
}

BADGE_COLORS = {
    "REPORTED": (21, 128, 61),
    "CLAIM": (180, 83, 9),
    "ONGOING": (29, 78, 216),
}


def font(name, size):
    path = "/usr/share/fonts/truetype/dejavu/%s.ttf" % name
    return ImageFont.truetype(path, size)


F_TITLE = font("DejaVuSans-Bold", 33)
F_SUB = font("DejaVuSans", 14)
F_TL_TIME = font("DejaVuSans-Bold", 13)
F_TL_LABEL = font("DejaVuSans", 10)
F_LEAD_HEAD = font("DejaVuSans-Bold", 16)
F_LEAD_BODY = font("DejaVuSans", 12)
F_CLAIM_BODY = font("DejaVuSans", 11)
F_LEAD_META = font("DejaVuSans-Bold", 11)
F_NUM_BIG = font("DejaVuSans-Bold", 22)
F_NUM_LABEL = font("DejaVuSans", 10)
F_MID_HEAD = font("DejaVuSans-Bold", 13)
F_MID_BODY = font("DejaVuSans", 11)
F_MID_META = font("DejaVuSans", 10)
F_SECTION = font("DejaVuSans-Bold", 11)
F_ALSO = font("DejaVuSans", 10)
F_FOOT = font("DejaVuSans", 11)
F_FOOT_B = font("DejaVuSans-Bold", 11)
F_BADGE = font("DejaVuSans-Bold", 9)
F_PIN = font("DejaVuSans-Bold", 8)
F_PIN_BIG = font("DejaVuSans-Bold", 11)
F_LEGEND = font("DejaVuSans", 9)


def wrap(text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_badge(d, x, y, label):
    """Badge with top-left at (x, y); returns width used."""
    w = int(F_BADGE.getlength(label)) + 10
    h = 15
    d.rounded_rectangle([x, y, x + w, y + h], radius=3,
                        fill=BADGE_COLORS[label])
    d.text((x + 5, y + 3), label, font=F_BADGE, fill=WHITE)
    return w


def draw_pin_number(d, cx, cy, num, color, r=11, fnt=None):
    fnt = fnt or F_PIN_BIG
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color,
              outline=WHITE, width=1)
    s = str(num)
    tw = fnt.getlength(s)
    th = fnt.getbbox(s)[3] - fnt.getbbox(s)[1]
    d.text((cx - tw / 2, cy - th / 2 - 1), s, font=fnt, fill=WHITE)


# ---------------------------------------------------------------- data
# (num, lon, lat, region) for the schematic map.
PINS = [
    (1, 100, 40, "Asia-Pacific"), (2, 2, 56, "Global"),
    (3, 149, -35, "Asia-Pacific"), (4, -74, 5, "Latin America"),
    (5, 36, 50, "Europe"), (6, 30, 50, "Europe"),
    (7, 32, 49, "Europe"), (8, 28, -26, "Africa"),
    (9, 4, 51, "Europe"), (10, 50, 53, "Europe"),
    (11, 50, 27, "Middle East"), (12, 34, 31, "Middle East"),
    (13, 121, 31, "Asia-Pacific"), (14, 127, 37, "Global"),
    (15, 107, -6.5, "Asia-Pacific"), (16, 36, 32, "Middle East"),
    (17, -75, 10, "Latin America"), (18, -4, 40, "Europe"),
    (19, 0, 16, "Africa"), (20, 152, -33, "Asia-Pacific"),
    (21, 35, 49.5, "Europe"), (22, -77, 39, "Global"),
    (23, 0.5, 52.8, "Europe"), (24, -0.1, 51.5, "Europe"),
    (25, 77, 29, "Asia-Pacific"), (26, -75, 37, "North America"),
    (27, 151, -34, "Asia-Pacific"), (28, 34, 48, "Europe"),
    (29, 106, -6, "Asia-Pacific"), (30, 28.7, 50.3, "Europe"),
]
# Small nudges (dx, dy in px) so clustered pins do not overlap.
NUDGE = {
    2: (8, -10), 3: (-12, 6), 4: (-12, 10), 5: (14, -8), 6: (-16, 8),
    7: (0, 14), 9: (10, 10), 12: (10, 10), 15: (-10, 10), 16: (-12, -8),
    17: (10, -8), 20: (14, 8), 21: (16, 4), 22: (-10, -8), 23: (12, 8),
    24: (-12, 6), 26: (12, 8), 27: (8, -12), 28: (-12, -10),
    29: (12, -8), 30: (10, -12),
}

TIMELINE = [
    ("00:18", "Shenzhou-24 lifts off, Jiuquan"),
    ("01:37", "Brent crude $90.97 a barrel"),
    ("03:15", "Australia-Solomons treaty signed"),
    ("05:30", "Bernal signs new INEOS deal"),
    ("08:00", "Ukraine: 88 of 112 drones downed"),
    ("08:34", "Ramaphosa wins Farmgate case"),
    ("10:09", "EU curbs trade with 15 entities"),
]

LEADS = [
    dict(num=1, region="Asia-Pacific", badge="REPORTED",
         time="00:18 UTC", source="Reuters",
         head="China launches Shenzhou-24 with Pakistan's first astronaut",
         body=("Long March-2F lifts off from Jiuquan at 00:18 UTC. Crew: "
               "Tang Hongbo, Wu Yi and Muhammad Zeeshan Ali, 40 - the first "
               "foreign astronaut to visit the Tiangong station. Stay: 5-10 days.")),
    dict(num=3, region="Asia-Pacific", badge="CLAIM",
         time="03:15 UTC", source="BBC News",
         head="Solomon Islands signs security treaty with Australia",
         body=("Canberra named \"primary security partner\"; no foreign "
               "base on Solomons soil."),
         claim=("CLAIM - Australian media: Honiara told Beijing it will not "
                "renew the 2022 China pact."),
         denial=("NO CONFIRM - PM Wale declined to confirm, citing an NDA. "
                 "China neither confirmed nor denied.")),
    dict(num=7, region="Europe", badge="REPORTED",
         time="08:00 UTC", source="Ukrinform",
         head="Russia fires 112 drones overnight; Ukraine downs 88",
         body=("Attack ran from 18:00 on 24 Nov. 66 were jet-powered "
               "Shaheds; 47 of those downed. Hits at 18 sites, debris "
               "at 13. Air Force figures as of 08:00.")),
]

NUMBERS = [
    ("112", "drones fired at Ukraine overnight"),
    ("88", "drones downed by Ukrainian defences"),
    ("$90.97", "Brent crude, -0.5%"),
    ("4.9%", "Australia CPI (Oct)"),
    ("15", "Russian entities hit by EU trade curbs"),
    ("1 in 3", "young Brits never had sex"),
]

MIDS = [
    dict(num=2, region="Global", badge="REPORTED", time="01:37 UTC",
         source="Reuters",
         head="Oil slides on supply-glut fears",
         body=("Brent -$0.43 to $90.97; WTI -$0.47 to $81.58, despite "
               "Middle East disruption fears.")),
    dict(num=8, region="Africa", badge="REPORTED", time="08:34 UTC",
         source="Reuters",
         head="Ramaphosa wins court bid to scrap 'Farmgate' report",
         body=("Panel had found he may have breached the constitution "
               "over the Farmgate affair.")),
    dict(num=9, region="Europe", badge="REPORTED", time="10:09 UTC",
         source="Council of the EU",
         head="EU curbs trade with 15 Russian entities",
         body=("Tighter dual-use and advanced-tech export rules; "
               "1 entity removed from the list.")),
    dict(num=10, region="Europe", badge="CLAIM", time="25 Nov",
         source="Reuters",
         head="Ukrainian drones hit Samara refineries; 1 killed",
         body=("145 drones downed overnight, governor says. Refinery fires "
               "reported on social media, not verified by Reuters.")),
    dict(num=11, region="Middle East", badge="CLAIM", time="25 Nov",
         source="Reuters",
         head="Houthis claim strikes on Saudi refinery, Riyadh",
         body=("Claimed fires at Ras Tanura refinery; coalition says 4 "
               "drones intercepted. 11 hurt in a Riyadh tower strike Tue.")),
    dict(num=12, region="Middle East", badge="REPORTED", time="25 Nov",
         source="Reuters",
         head="Israeli strike kills Hamas security chief, family",
         body=("Col. Abuelouf, his wife and 2 children killed in Gaza City; "
               "2nd senior Hamas security official killed in 24 hours.")),
    dict(num=13, region="Asia-Pacific", badge="REPORTED", time="25 Nov",
         source="Reuters",
         head="China probes Politburo member Chen Jining",
         body=("Shanghai chief is the 4th Politburo probe since 2025. "
               "Politburo down to 21 acting members of 24.")),
    dict(num=14, region="Global", badge="REPORTED", time="25 Nov",
         source="Reuters",
         head="Asian stocks tumble as AI rally fizzles",
         body=("MSCI Asia ex-Japan -2.3%; Korea -5.3%, Taiwan -5.1%, "
               "Nikkei -2.9%. Nvidia -5.9%.")),
    dict(num=15, region="Asia-Pacific", badge="ONGOING", time="25 Nov",
         source="Reuters",
         head="Rescuers hunt for 'dozens' in West Java mine",
         body=("Miners stuck 100 m down in an unauthorised gold mine at "
               "Pongkor, Bogor, since Monday. 30 reported trapped.")),
    dict(num=17, region="Latin America", badge="REPORTED", time="25 Nov",
         source="Reuters",
         head="All hostages freed in Cartagena supermarket siege",
         body=("Day-long siege ends; 1 captor killed. It began Tue after a "
               "failed armoured-truck robbery; about 30 held.")),
]

ALSO = [
    (4, "05:30 Bernal signs new INEOS deal — Reuters"),
    (5, "Drone hits bus in Kharkiv; 1 killed, 7 hurt — UNIAN"),
    (6, "1 killed in Bila Tserkva; Epicentr hit — Independent"),
    (16, "Jordan death sentence over officer killing — Reuters"),
    (18, "Spain: Madrid building vs Catalonia rent caps — Reuters"),
    (19, "Sahel insurgents take war to skies with drones — Reuters"),
    (20, "Australia inflation jumps to 4.9%; core 3.8% — Reuters"),
    (21, "Attack sets Naftogaz facility ablaze, Poltava — Reuters"),
    (22, "FT: US shelves pitch to end Ukraine war — Reuters"),
    (23, "Two men charged over Sandringham break-in — CNN"),
    (24, "Natsal: 1 in 3 young Brits never had sex — BBC News"),
    (25, "'Cockroach' leader petitions Delhi court — Bar and Bench"),
    (26, "Pentagon hires firms to audit base schools — AP"),
    (27, "Sydney policeman guilty of double murder — TVNZ"),
    (28, "Russia strikes DTEK power plant, output halted — Reuters"),
    (29, "Danantara unit to run seized forest land — Reuters"),
    (30, "Russian drones hit Zhytomyr sites; 1 hurt — Ukrinform"),
]

# Simplified continent outlines (lon, lat), schematic only.
CONTINENTS = [
    [(-168, 66), (-155, 71), (-140, 70), (-130, 71), (-120, 70), (-110, 68),
     (-100, 69), (-90, 69), (-85, 66), (-80, 73), (-75, 72), (-70, 62),
     (-65, 60), (-60, 55), (-55, 52), (-60, 47), (-65, 44), (-70, 42),
     (-74, 39), (-76, 35), (-80, 32), (-81, 26), (-84, 30), (-88, 29),
     (-91, 19), (-95, 19), (-97, 26), (-102, 23), (-105, 20), (-110, 23),
     (-114, 28), (-117, 33), (-122, 37), (-124, 42), (-124, 48), (-130, 55),
     (-140, 60), (-150, 61), (-158, 58), (-165, 60)],
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-78, -10), (-75, -15),
     (-71, -18), (-70, -23), (-70, -30), (-71, -35), (-73, -42), (-73, -48),
     (-74, -53), (-70, -55), (-66, -55), (-68, -50), (-66, -45), (-63, -40),
     (-58, -35), (-53, -33), (-48, -28), (-43, -23), (-39, -17), (-35, -9),
     (-35, -6), (-40, -3), (-44, -2), (-50, 0), (-53, 4), (-57, 6),
     (-61, 9), (-66, 11), (-71, 12), (-76, 10)],
    [(-17, 15), (-16, 20), (-13, 27), (-10, 31), (-6, 34), (-1, 35),
     (3, 37), (9, 37), (11, 34), (15, 32), (20, 32), (25, 32), (30, 31),
     (32, 31), (34, 28), (36, 24), (38, 20), (39, 15), (43, 11), (48, 11),
     (51, 12), (46, 5), (42, 0), (40, -4), (40, -10), (38, -15),
     (35, -20), (33, -26), (29, -31), (25, -34), (20, -35), (17, -33),
     (15, -28), (13, -20), (12, -12), (10, -4), (9, 4), (6, 5), (0, 6),
     (-7, 5), (-12, 8), (-16, 11)],
    [(-10, 36), (-9, 39), (-9, 43), (-4, 44), (-2, 46), (-4, 48), (-1, 49),
     (1, 51), (3, 53), (5, 53), (7, 54), (8, 55), (8, 57), (10, 59),
     (7, 60), (5, 60), (6, 62), (10, 64), (13, 66), (16, 68), (20, 70),
     (25, 71), (30, 70), (34, 68), (38, 68), (42, 66), (44, 68), (48, 69),
     (52, 68), (56, 69), (60, 69), (64, 70), (68, 72), (72, 73), (76, 73),
     (80, 73), (85, 74), (90, 75), (95, 76), (100, 77), (105, 77),
     (110, 74), (115, 73), (120, 73), (125, 72), (130, 72), (135, 71),
     (140, 72), (145, 72), (150, 70), (155, 69), (158, 66), (160, 62),
     (162, 58), (158, 55), (155, 59), (150, 59), (145, 59), (142, 55),
     (142, 50), (140, 45), (138, 43), (135, 43), (132, 42), (130, 40),
     (128, 38), (126, 38), (124, 39), (122, 38), (120, 34), (122, 31),
     (121, 28), (120, 24), (116, 23), (112, 21), (110, 20), (108, 17),
     (106, 10), (104, 8), (102, 7), (100, 8), (98, 10), (97, 14),
     (94, 17), (92, 21), (90, 22), (88, 22), (86, 20), (84, 19),
     (81, 16), (80, 13), (78, 9), (76, 10), (74, 15), (72, 20),
     (70, 21), (68, 23), (66, 25), (64, 25), (61, 25), (58, 25),
     (56, 26), (53, 27), (50, 29), (48, 30), (46, 29), (44, 29),
     (41, 30), (39, 31), (37, 33), (36, 36), (34, 36), (31, 36),
     (29, 36), (27, 37), (26, 38), (24, 39), (23, 40), (22, 40),
     (20, 40), (19, 42), (18, 44), (16, 44), (14, 45), (12, 44),
     (10, 44), (8, 44), (6, 43), (3, 43), (0, 40), (-2, 37), (-5, 36),
     (-8, 37)],
    [(-3, 58), (-1, 57), (0, 53), (-2, 51), (-5, 50), (-5, 53)],
    [(130, 31), (133, 34), (136, 35), (139, 37), (141, 39), (141, 41),
     (143, 43), (145, 44), (142, 45), (140, 42), (138, 38), (135, 34),
     (131, 33)],
    [(113, -22), (114, -28), (115, -33), (118, -35), (122, -34), (126, -32),
     (129, -32), (132, -32), (135, -35), (137, -35), (140, -38), (143, -39),
     (146, -39), (149, -37), (151, -35), (153, -32), (153, -28), (151, -24),
     (148, -20), (146, -19), (143, -16), (142, -11), (140, -17), (138, -17),
     (136, -15), (135, -12), (132, -12), (130, -13), (127, -14), (124, -15),
     (121, -17), (118, -20), (115, -21)],
    [(-45, 60), (-40, 64), (-35, 68), (-30, 68), (-25, 70), (-20, 70),
     (-22, 74), (-30, 76), (-40, 76), (-50, 74), (-55, 70), (-58, 64),
     (-52, 60)],
    [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38), (178, -37),
     (175, -40), (172, -43), (169, -46)],
]


def build():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # ---- header (0-68)
    d.rectangle([0, 0, W, 68], fill=NAVY)
    d.text((16, 8), "WEDNESDAY 25 NOVEMBER 2026", font=F_TITLE, fill=WHITE)
    d.text((16, 46), "THE WORLD IN ONE IMAGE  •  30 STORIES  •  7 REGIONS",
           font=F_SUB, fill=(159, 184, 216))

    # ---- timeline strip (68-108)
    d.rectangle([0, 68, W, 108], fill=LIGHT_BG)
    d.line([0, 108, W, 108], fill=LINE, width=1)
    col_w = W / 7
    for i, (t, label) in enumerate(TIMELINE):
        x = int(i * col_w) + 12
        if i:
            d.line([int(i * col_w), 74, int(i * col_w), 102], fill=LINE, width=1)
        d.text((x, 71), t, font=F_TL_TIME, fill=NAVY)
        for j, ln in enumerate(wrap(label, F_TL_LABEL, col_w - 22)):
            d.text((x, 86 + j * 11), ln, font=F_TL_LABEL, fill=INK)

    # ---- leads (110-326)
    lead_y, lead_h, lead_w = 110, 216, 328
    for k, lead in enumerate(LEADS):
        x0 = 8 + k * (lead_w + 12)
        x1 = x0 + lead_w
        d.rounded_rectangle([x0, lead_y, x1, lead_y + lead_h], radius=6,
                            fill=CARD_BG, outline=LINE, width=1)
        color = REGION_COLORS[lead["region"]]
        d.rounded_rectangle([x0, lead_y, x1, lead_y + 6], radius=3, fill=color)
        d.rectangle([x0, lead_y + 3, x1, lead_y + 6], fill=color)
        draw_pin_number(d, x0 + 24, lead_y + 28, lead["num"], color, r=13)
        bw = draw_badge(d, x1 - 8 - (int(F_BADGE.getlength(lead["badge"])) + 10),
                        lead_y + 20, lead["badge"])
        y = lead_y + 48
        for ln in wrap(lead["head"], F_LEAD_HEAD, lead_w - 24):
            d.text((x0 + 12, y), ln, font=F_LEAD_HEAD, fill=INK)
            y += 19
        y += 2
        if "claim" in lead:
            for ln in wrap(lead["body"], F_LEAD_BODY, lead_w - 24):
                d.text((x0 + 12, y), ln, font=F_LEAD_BODY, fill=INK)
                y += 15
            y += 4
            for tag, txt, bg in (("CLAIM", lead["claim"], (254, 243, 199)),
                                 ("NO CONFIRM", lead["denial"], (241, 245, 249))):
                box_y = y
                lines = wrap(txt, F_CLAIM_BODY, lead_w - 36)
                box_h = len(lines) * 12 + 5
                d.rounded_rectangle([x0 + 12, box_y, x1 - 12, box_y + box_h],
                                    radius=4, fill=bg)
                ly = box_y + 3
                for ln in lines:
                    d.text((x0 + 18, ly), ln, font=F_CLAIM_BODY, fill=INK)
                    ly += 12
                y = box_y + box_h + 5
        else:
            for ln in wrap(lead["body"], F_LEAD_BODY, lead_w - 24):
                d.text((x0 + 12, y), ln, font=F_LEAD_BODY, fill=INK)
                y += 15
        d.text((x0 + 12, lead_y + lead_h - 20),
               "%s  •  %s" % (lead["time"], lead["source"]),
               font=F_LEAD_META, fill=NAVY)

    # ---- the day in numbers (330-384)
    d.text((16, 330), "THE DAY IN NUMBERS", font=F_SECTION, fill=NAVY)
    num_y = 348
    cell_w = 168
    for i, (big, label) in enumerate(NUMBERS):
        x = 8 + i * 170
        d.rounded_rectangle([x, num_y, x + cell_w, num_y + 36], radius=5,
                            fill=LIGHT_BG)
        d.text((x + 10, num_y + 5), big, font=F_NUM_BIG, fill=NAVY)
        lx = x + 10 + int(F_NUM_BIG.getlength(big)) + 8
        for j, ln in enumerate(wrap(label, F_NUM_LABEL, x + cell_w - lx - 6)):
            d.text((lx, num_y + 5 + j * 12), ln, font=F_NUM_LABEL, fill=INK)

    # ---- mid stories (386-671): 2 cols x 5 rows
    mid_y0, row_h = 386, 57
    for i, mid in enumerate(MIDS):
        col, row = i % 2, i // 2
        x0 = 8 + col * 508
        y0 = mid_y0 + row * row_h
        color = REGION_COLORS[mid["region"]]
        d.line([x0, y0 + row_h - 1, x0 + 500, y0 + row_h - 1], fill=LINE, width=1)
        draw_pin_number(d, x0 + 12, y0 + 12, mid["num"], color, r=11)
        bw = draw_badge(d, x0 + 500 - (int(F_BADGE.getlength(mid["badge"])) + 10),
                        y0 + 4, mid["badge"])
        head_w = 500 - 30 - bw - 12
        head = mid["head"]
        while F_MID_HEAD.getlength(head) > head_w and len(head) > 4:
            head = head[:-2]
        if head != mid["head"]:
            head = head.rstrip() + "…"
        d.text((x0 + 28, y0 + 3), head, font=F_MID_HEAD, fill=INK)
        by = y0 + 20
        for ln in wrap(mid["body"], F_MID_BODY, 500 - 28):
            d.text((x0 + 28, by), ln, font=F_MID_BODY, fill=(51, 65, 85))
            by += 13
        d.text((x0 + 28, y0 + 46),
               "%s  •  %s" % (mid["time"], mid["source"]),
               font=F_MID_META, fill=GREY)

    # ---- map (671-791)
    d.text((16, 673), "WHERE IT HAPPENED — 30 STORIES, 7 REGIONS (SCHEMATIC MAP)",
           font=F_SECTION, fill=NAVY)
    lx = 560
    for region in ("Europe", "Asia-Pacific", "Middle East", "Africa",
                   "North America", "Latin America", "Global"):
        c = REGION_COLORS[region]
        d.ellipse([lx, 676, lx + 8, 684], fill=c)
        d.text((lx + 11, 674), REGION_SHORT[region], font=F_LEGEND, fill=GREY)
        lx += 11 + int(F_LEGEND.getlength(REGION_SHORT[region])) + 10

    map_x0, map_x1, map_y0, map_y1 = 8, 1016, 688, 790

    def proj(lon, lat):
        x = map_x0 + (lon + 180.0) / 360.0 * (map_x1 - map_x0)
        y = map_y0 + (78.0 - lat) / 136.0 * (map_y1 - map_y0)
        return x, y

    d.rectangle([map_x0, map_y0, map_x1, map_y1], fill=MAP_OCEAN)
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=MAP_LAND, outline=MAP_EDGE)
    for num, lon, lat, region in PINS:
        px, py = proj(lon, lat)
        dx, dy = NUDGE.get(num, (0, 0))
        color = REGION_COLORS[region]
        if (dx, dy) != (0, 0):
            d.line([px, py, px + dx, py + dy], fill=color, width=1)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=color)
            cx, cy = px + dx, py + dy
        else:
            cx, cy = px, py
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=color,
                  outline=WHITE, width=1)
        s = str(num)
        tw = F_PIN.getlength(s)
        d.text((cx - tw / 2, cy - 5), s, font=F_PIN, fill=WHITE)
    d.rectangle([map_x0, map_y0, map_x1, map_y1], outline=LINE, width=1)

    # ---- also (793-934)
    d.text((16, 795), "ALSO ON 25 NOVEMBER", font=F_SECTION, fill=NAVY)
    cols_x = [8, 344, 680]
    cols_w = [330, 330, 336]
    for i, (num, text) in enumerate(ALSO):
        col, row = (i // 6), (i % 6)
        x0 = cols_x[col]
        y0 = 810 + row * 21
        color = REGION_COLORS[[p[3] for p in PINS if p[0] == num][0]]
        d.ellipse([x0, y0 + 1, x0 + 13, y0 + 14], fill=color)
        s = str(num)
        tw = F_PIN.getlength(s)
        d.text((x0 + 6.5 - tw / 2, y0 + 4), s, font=F_PIN, fill=WHITE)
        while F_ALSO.getlength(text) > cols_w[col] - 20 and len(text) > 4:
            text = text[:-2]
        if text != ALSO[i][1]:
            text = text.rstrip() + "…"
        d.text((x0 + 18, y0 + 2), text, font=F_ALSO, fill=INK)

    # ---- footer (936-1024)
    d.rectangle([0, 936, W, H], fill=NAVY)
    fy = 942
    blocks = [
        ("DATE CHECK — ",
         "Wires read to 10:37 UTC. 7 stories carry an exact UTC hour; 23 carry "
         "a 25 Nov dateline (no hour in source). Every story here happened, or "
         "was first reported, on 25 Nov 2026."),
        ("LEFT OUT — ",
         "Not 25 Nov news: UCL matches 24 Nov; Trump tariff plan 24 Nov; Huawei "
         "verdict 24 Nov; Shein $100m FTC deal 24 Nov; Russia ~500,000 war "
         "deaths first reported 23 Nov; Democrats' 259th House seat called 24 Nov."),
        ("HOW SURE — ",
         "REPORTED: confirmed by the named source. CLAIM: one side's claim, "
         "not yet verified. ONGOING: still developing at 10:37 UTC."),
    ]
    for label, text in blocks:
        full = label + text
        lines = wrap(full, F_FOOT, W - 32)
        for ln in lines:
            if ln.startswith(label):
                d.text((16, fy), label, font=F_FOOT_B, fill=WHITE)
                d.text((16 + F_FOOT_B.getlength(label), fy),
                       ln[len(label):], font=F_FOOT, fill=(207, 224, 242))
            else:
                d.text((16, fy), ln, font=F_FOOT, fill=(207, 224, 242))
            fy += 13
        fy += 3

    img.save(OUT, optimize=True)
    data = open(OUT, "rb").read()
    print("wrote %s  %d bytes  sha256=%s" % (OUT, len(data),
          hashlib.sha256(data).hexdigest()))
    return OUT


if __name__ == "__main__":
    build()
