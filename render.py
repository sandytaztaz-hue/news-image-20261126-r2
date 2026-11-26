#!/usr/bin/env python3
"""Build-time renderer for the Sum 26 broadsheet (news-image-20261126-r2).

Runs locally only (Pillow). Produces entry.png next to this file.
Deterministic: no network, no clock, no randomness.
The submitted program (main.py) is stdlib-only and copies entry.png.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

PAPER = (248, 244, 233)
INK = (26, 26, 26)
RULE = (26, 26, 26)
MUTED = (90, 84, 70)
RED = (178, 34, 34)
BLUE = (31, 78, 121)
OCEAN = (207, 227, 238)
LAND = (181, 201, 154)
LAND2 = (217, 201, 163)
GOLD = (184, 134, 11)
SCENE_SKY = (174, 214, 241)
PIN = (178, 34, 34)

_font_cache = {}


def load_font(size, bold=False):
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    names = []
    if bold:
        names.append(os.path.join(HERE, "fonts", "LiberationSerif-Bold.ttf"))
        names.append("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf")
    else:
        names.append(os.path.join(HERE, "fonts", "LiberationSerif-Regular.ttf"))
        names.append("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf")
    fnt = None
    for path in names:
        try:
            fnt = ImageFont.truetype(path, size)
            break
        except Exception:
            continue
    if fnt is None:
        try:
            fnt = ImageFont.load_default()
        except Exception:
            fnt = ImageFont.load_default()
    _font_cache[key] = fnt
    return fnt


def wrap(draw, text, fnt, maxw):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill=INK, leading=None):
    if leading is None:
        leading = fnt.size + 3
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def box(draw, x0, y0, x1, y1, outline=RULE, width=1, fill=None):
    draw.rectangle([x0, y0, x1, y1], outline=outline, width=width, fill=fill)


def status_tag(draw, x, y, status):
    colours = {"OFFICIAL": BLUE, "CONFIRMED": (46, 125, 50),
               "REPORTED": GOLD, "CLAIM": RED, "ONGOING": (120, 60, 140)}
    col = colours.get(status, MUTED)
    fnt = load_font(9, bold=True)
    w = draw.textlength(status, font=fnt) + 8
    draw.rectangle([x, y, x + w, y + 12], fill=col)
    draw.text((x + 4, y + 1), status, font=fnt, fill=(255, 255, 255))
    return x + w + 4

# ---------------------------------------------------------------- data
HEROES = [
    {
        "num": 1, "status": "OFFICIAL", "source": "Macy's / NYC",
        "headline": "Macy's 100th parade postponed to Saturday",
        "body": ("The 100th Thanksgiving parade in New York moves to "
                 "Saturday 28 Nov, 8:30 a.m. ET, as a nor'easter brings "
                 "gusts to 60 mph, heavy rain and coastal flooding. First "
                 "postponement ever; balloons are deflated tonight and "
                 "return Saturday. Philadelphia's parade is cancelled."),
        "scene": "parade",
    },
    {
        "num": 2, "status": "OFFICIAL", "source": "PTI / Govt of India",
        "headline": "India marks 18 years since the 26/11 attacks",
        "body": ("Tributes across India on the anniversary of the 2008 "
                 "Mumbai attacks, as the nation also marks 77 years of "
                 "its Constitution. Memorials in Mumbai and Delhi honour "
                 "the victims and the security forces who fought back."),
        "scene": "memorial",
    },
    {
        "num": 3, "status": "CONFIRMED", "source": "FIDE",
        "headline": "Gukesh meets Sindarov in Game 3 of the title match",
        "body": ("World Chess Championship, Geneva: Game 3 today, 14:00 "
                 "UTC (15:00 CET), Sindarov with White. The match is "
                 "level 1-1 after two draws (38 moves, then 20). First "
                 "to 7.5 points wins; prize fund $2.5 million."),
        "scene": "chess",
    },
]

MEDIUMS = [
    ("4", "CLAIM", "Houthis say they hit Saudi refinery",
     "Ras Tanura, the kingdom's largest at 550,000 barrels a day; "
     "satellite images show black smoke; four drones downed; Brent "
     "jumped over 2% to about $93.60.", "Reuters"),
    ("5", "REPORTED", "Two tankers hit mines in Hormuz",
     "Naval mines strike two tankers in the Strait of Hormuz, the "
     "world's busiest oil chokepoint; crews safe, spill feared.", "Reuters"),
    ("6", "REPORTED", "Israeli strike kills Hamas security chief",
     "A Hamas security chief is killed in Gaza in an Israeli strike, "
     "as ceasefire talks stall and aid convoys wait at the border.", "AP"),
    ("7", "CLAIM", "Ukraine says a laser downed a jet drone",
     "Kyiv says a laser weapon brought down a jet-powered drone, a "
     "first claimed battlefield kill for the new system.", "Reuters"),
    ("8", "REPORTED", "Russian strikes cut power in five regions",
     "Overnight strikes leave five Ukrainian regions without power "
     "as winter bites; engineers race to restore the grid.", "AP"),
    ("9", "CONFIRMED", "US proposes tariffs on 14 partners",
     "Washington proposes new tariffs on 14 trading partners, "
     "reopening trade fights with allies and rivals alike.", "Reuters"),
    ("10", "CONFIRMED", "Bangladesh lifts garment wage 36%",
     "The garment minimum wage rises 36% to Tk 17,000 a month, a "
     "win for millions of factory workers after street protests.", "AFP"),
    ("11", "CONFIRMED", "Shenzhou-24 docks; Pakistani in orbit",
     "Shenzhou-24 docks with Tiangong station; the first Pakistani "
     "astronaut reaches orbit aboard the Chinese crew.", "Xinhua"),
    ("12", "REPORTED", "Leaked data put Russian war dead near 500,000",
     "Leaked figures put Russian war dead at 490,334, the grimmest "
     "tally yet of the war's human cost.", "Reuters"),
    ("13", "CONFIRMED", "Solomon Islands signs Australia pact",
     "A A$740m security pact with Australia is signed, deepening "
     "ties across the Pacific as regional rivalry grows.", "Reuters"),
]

BRIEFS = [
    ("14", "India and Nepal sign a Rs 15,000 crore package", "PTI"),
    ("15", "US jobless claims fall to 189,000", "Reuters"),
    ("16", "Nvidia sell-off drags S&P and Nasdaq down", "Reuters"),
    ("17", "EU imposes visa bans on Chinese cars", "Reuters"),
    ("18", "Colombia police free 20 supermarket hostages", "AP"),
    ("19", "Sudan drone strikes kill 19 in Blue Nile", "Reuters"),
    ("20", "Saudi national kidnapped by IS in Niger", "Reuters"),
    ("21", "Cairo tanker fire kills at least 30", "Reuters"),
    ("22", "Plane crash into Gulf of Mexico, six aboard", "AP"),
    ("23", "PIA shifts UK flights to its own 777 fleet", "Reuters"),
    ("24", "Beijing stunner as Real Madrid rout PSG", "UEFA"),
    ("25", "Sooryavanshi, 15, smashes 204 off 53 balls", "Cricinfo"),
    ("26", "IITs add 6,000 seats in robotics, AI, space", "Govt of India"),
    ("27", "Tempus buys Personalis in $600m cash deal", "Investing.com"),
    ("28", "Xi probe hits Shanghai chief Chen Jining", "Reuters"),
    ("29", "Hera reveals DART crater on Dimorphos", "ESA"),
    ("30", "Brazil mosquitoes cut viral infections 68%", "Study"),
    ("31", "Palm Beach ferries strike shuts services", "NSW Govt"),
    ("32", "Malaysia sues Google for $146m over YouTube", "Reuters"),
    ("33", "Swiss tourist killed by elephants in Cameroon", "AP"),
    ("34", "Army blows up 5 tonnes of explosives in Iowa", "Al Jazeera"),
    ("35", "Coalition hits Hodeidah after Houthi attacks", "Reuters"),
    ("36", "UN Gaza staff sacked on unproven claims", "The Guardian"),
]

NUMBERS = [
    ("100", "parade years"), ("60 mph", "nor'easter gusts"),
    ("18", "years since 26/11"), ("1-1", "chess score"),
    ("550,000", "Ras Tanura bpd"), ("490,334", "Russian war dead"),
]

TIMELINE = [
    ("00:00", "Thanksgiving Day begins"),
    ("06:00", "Delhi: Constitution Day"),
    ("13:30", "Parade was due to step off"),
    ("14:00", "Chess Game 3, Geneva"),
    ("15:00", "NY wind warning begins"),
    ("23:00", "36 stories filed"),
]

EXCLUDED = [
    ("Nvidia reinstates Jensen Huang", "24 Nov"),
    ("COP31 ends without a pact", "22 Nov"),
    ("Ukraine drones hit Russian ships off Libya", "22 Nov"),
    ("Belgium strike grounds flights", "23 Nov"),
    ("Israel kills Hamas chief Naeem Abu Nahal", "24 Nov"),
    ("Trump-Putin-Xi trilateral in Shenzhen", "17 Nov"),
    ("UNRWA worker killed in Gaza strike", "23 Nov"),
    ("US shelves Russia business-deal peace plan", "25 Nov"),
]

REGIONS = [
    ("North America", 6), ("South Asia", 6), ("Europe", 6),
    ("Middle East", 4), ("Africa", 4), ("World", 3),
    ("East Asia", 3), ("Oceania", 2), ("South America", 2),
]

PINS = [
    (1, 148, 42), (2, 442, 84), (3, 328, 38), (4, 398, 68),
    (5, 418, 76), (6, 384, 60), (7, 336, 22), (8, 368, 40),
    (9, 118, 48), (10, 470, 78), (11, 502, 52), (12, 428, 22),
    (13, 556, 128),
]

# ---------------------------------------------------------------- scenes

def scene_parade(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=SCENE_SKY)
    # buildings
    for bx, bw, bh in [(0, 46, 62), (52, 40, 84), (98, 52, 58), (156, 44, 78),
                       (206, 48, 60), (260, 44, 82), (310, 24, 66)]:
        draw.rectangle([x0 + bx, y1 - bh, x0 + bx + bw, y1], fill=(96, 110, 130))
        for wy in range(y1 - bh + 8, y1 - 6, 12):
            for wx in range(x0 + bx + 6, x0 + bx + bw - 6, 12):
                draw.rectangle([wx, wy, wx + 5, wy + 6], fill=(255, 214, 120))
    # street
    draw.rectangle([x0, y1 - 12, x1, y1], fill=(70, 70, 74))
    # balloons: big round balloon + long balloon, sagging
    draw.ellipse([x0 + 120, y0 + 8, x0 + 200, y0 + 52], fill=(178, 34, 34),
                 outline=(120, 20, 20))
    draw.ellipse([x0 + 210, y0 + 16, x0 + 300, y0 + 48], fill=(255, 200, 40),
                 outline=(160, 120, 0))
    draw.line([x0 + 160, y0 + 52, x0 + 158, y1 - 12], fill=(60, 60, 60), width=2)
    draw.line([x0 + 255, y0 + 48, x0 + 252, y1 - 12], fill=(60, 60, 60), width=2)
    # rain streaks + confetti
    for rx in range(x0 + 8, x1 - 8, 26):
        draw.line([rx, y0 + 6, rx - 6, y0 + 22], fill=(255, 255, 255), width=2)
    for cx, cy, col in [(30, 20, RED), (90, 14, GOLD), (230, 60, BLUE),
                        (290, 12, RED), (60, 60, GOLD)]:
        draw.ellipse([x0 + cx, y0 + cy, x0 + cx + 5, y0 + cy + 5], fill=col)


def scene_memorial(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(32, 42, 68))
    # Gateway of India arch silhouette
    cx = (x0 + x1) // 2
    draw.rectangle([cx - 70, y0 + 30, cx + 70, y1 - 14], fill=(201, 162, 39))
    draw.rectangle([cx - 34, y0 + 62, cx + 34, y1 - 14], fill=(32, 42, 68))
    draw.ellipse([cx - 34, y0 + 42, cx + 34, y0 + 78], fill=(32, 42, 68))
    draw.rectangle([cx - 86, y0 + 22, cx + 86, y0 + 32], fill=(201, 162, 39))
    draw.rectangle([cx - 58, y0 + 12, cx + 58, y0 + 22], fill=(201, 162, 39))
    # saffron / white / green band
    draw.rectangle([x0, y1 - 14, x1, y1 - 10], fill=(255, 153, 51))
    draw.rectangle([x0, y1 - 10, x1, y1 - 6], fill=(255, 255, 255))
    draw.rectangle([x0, y1 - 6, x1, y1], fill=(19, 136, 8))
    # candles with flames
    for fx in [x0 + 24, x0 + 58, x1 - 58, x1 - 24]:
        draw.rectangle([fx - 3, y1 - 34, fx + 3, y1 - 16], fill=(240, 230, 200))
        draw.ellipse([fx - 4, y1 - 44, fx + 4, y1 - 33], fill=(255, 180, 0))
    # stars
    for sx, sy in [(20, 12), (70, 22), (300, 14), (250, 26)]:
        draw.text((x0 + sx, y0 + sy), "*", font=load_font(12, bold=True),
                  fill=(255, 255, 255))


def scene_chess(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(58, 44, 30))
    bs = (y1 - y0 - 8) // 8
    bx0, by0 = x0 + 8, y0 + 4
    for r in range(8):
        for c in range(8):
            col = (240, 217, 181) if (r + c) % 2 == 0 else (181, 136, 99)
            draw.rectangle([bx0 + c * bs, by0 + r * bs,
                            bx0 + (c + 1) * bs, by0 + (r + 1) * bs], fill=col)
    # pieces as discs with letters
    pieces = [(0, 4, "K", False), (0, 3, "Q", False), (1, 4, "P", False),
              (7, 4, "K", True), (7, 3, "Q", True), (6, 3, "P", True),
              (2, 5, "N", False), (5, 2, "B", True)]
    fnt = load_font(11, bold=True)
    for r, c, letter, white in pieces:
        px, py = bx0 + c * bs, by0 + r * bs
        fill = (250, 250, 250) if white else (30, 30, 30)
        edge = (30, 30, 30) if white else (200, 200, 200)
        draw.ellipse([px + 2, py + 2, px + bs - 2, py + bs - 2],
                     fill=fill, outline=edge)
        tw = draw.textlength(letter, font=fnt)
        draw.text((px + (bs - tw) / 2, py + 1), letter, font=fnt,
                  fill=(30, 30, 30) if white else (250, 250, 250))
    # clock
    draw.rectangle([x1 - 66, y0 + 6, x1 - 8, y0 + 30], fill=(20, 20, 20))
    draw.text((x1 - 62, y0 + 9), "14:00 UTC", font=load_font(11, bold=True),
              fill=(255, 220, 90))
    # matchup panel right of the board
    px = bx0 + 8 * bs + 14
    draw.text((px, y0 + 10), "GUKESH", font=load_font(16, bold=True),
              fill=(255, 255, 255))
    draw.text((px, y0 + 30), "vs", font=load_font(12), fill=(220, 200, 160))
    draw.text((px, y0 + 48), "SINDAROV", font=load_font(16, bold=True),
              fill=(255, 255, 255))
    draw.text((px, y0 + 70), "Score 1-1  |  First to 7.5",
              font=load_font(11, bold=True), fill=(255, 220, 90))


SCENES = {"parade": scene_parade, "memorial": scene_memorial,
          "chess": scene_chess}

# ---------------------------------------------------------------- masthead + heroes

def draw_masthead(draw):
    draw.text((10, 8), "THE WORLD IN ONE DAY", font=load_font(40, bold=True),
              fill=INK)
    counts = [("36", "STORIES"), ("9", "REGIONS"), ("15", "SOURCES")]
    cx = 1014
    for num, label in reversed(counts):
        fnum = load_font(20, bold=True)
        flab = load_font(9, bold=True)
        w = max(draw.textlength(num, font=fnum),
                draw.textlength(label, font=flab)) + 16
        cx -= int(w) + 6
        box(draw, cx, 14, cx + int(w), 48, width=2)
        draw.text((cx + 8, 16), num, font=fnum, fill=RED)
        draw.text((cx + 8, 38), label, font=flab, fill=INK)
    draw.text((10, 56), "THURSDAY 26 NOVEMBER 2026",
              font=load_font(14, bold=True), fill=RED)
    sub = ("Macy's 100th parade postponed  |  India marks 18 years since "
           "26/11  |  Gukesh-Sindarov Game 3 in Geneva")
    draw.text((10, 76), sub, font=load_font(12), fill=INK)
    draw.line([10, 96, 1014, 96], fill=RULE, width=2)


def draw_heroes(draw):
    cols = [(10, 344), (348, 682), (686, 1014)]
    for hero, (x0, x1) in zip(HEROES, cols):
        box(draw, x0, 100, x1, 306, width=2)
        SCENES[hero["scene"]](draw, x0 + 2, 102, x1 - 2, 196)
        draw.line([x0, 196, x1, 196], fill=RULE, width=1)
        y = 200
        x = status_tag(draw, x0 + 6, y, hero["status"])
        draw.text((x, y + 1), "No. %d - %s" % (hero["num"], hero["source"]),
                  font=load_font(9, bold=True), fill=MUTED)
        y += 16
        hl = wrap(draw, hero["headline"], load_font(15, bold=True),
                  x1 - x0 - 12)
        y = draw_lines(draw, hl[:2], x0 + 6, y, load_font(15, bold=True),
                       leading=17)
        body = wrap(draw, hero["body"], load_font(11), x1 - x0 - 12)
        draw_lines(draw, body[:4], x0 + 6, y + 2, load_font(11), leading=13)

# ---------------------------------------------------------------- mediums + strips

def draw_mediums(draw):
    rows = [(310, 412), (416, 518)]
    col_w = 197
    for ri, (y0, y1) in enumerate(rows):
        for ci in range(5):
            idx = ri * 5 + ci
            num, status, head, body, src = MEDIUMS[idx]
            x0 = 10 + ci * (col_w + 4)
            x1 = x0 + col_w
            box(draw, x0, y0, x1, y1, width=1)
            y = y0 + 5
            x = status_tag(draw, x0 + 5, y, status)
            draw.text((x, y + 1), "No. %s" % num, font=load_font(9, bold=True),
                      fill=MUTED)
            y += 16
            hl = wrap(draw, head, load_font(12, bold=True), x1 - x0 - 10)
            y = draw_lines(draw, hl[:2], x0 + 5, y, load_font(12, bold=True),
                           leading=13)
            bl = wrap(draw, body, load_font(10), x1 - x0 - 10)
            y = draw_lines(draw, bl[:3], x0 + 5, y + 2, load_font(10),
                           leading=12)
            draw.text((x0 + 5, y1 - 14), src, font=load_font(9, bold=True),
                      fill=MUTED)


def draw_numbers(draw):
    box(draw, 10, 522, 1014, 556, width=2, fill=(26, 26, 26))
    draw.text((18, 531), "IN NUMBERS", font=load_font(13, bold=True),
              fill=(255, 220, 90))
    x = 130
    for num, label in NUMBERS:
        draw.text((x, 529), num, font=load_font(16, bold=True),
                  fill=(255, 255, 255))
        w = draw.textlength(num, font=load_font(16, bold=True))
        draw.text((x + w + 5, 533), label, font=load_font(10),
                  fill=(220, 220, 220))
        x += int(w) + draw.textlength(label, font=load_font(10)) + 28


def draw_timeline(draw):
    box(draw, 10, 560, 1014, 596, width=1)
    draw.text((14, 568), "UTC TIMELINE", font=load_font(11, bold=True),
              fill=RED)
    x = 128
    for t, label in TIMELINE:
        draw.text((x, 568), t, font=load_font(11, bold=True), fill=BLUE)
        w = draw.textlength(t, font=load_font(11, bold=True))
        draw.text((x + w + 4, 568), label, font=load_font(10), fill=INK)
        x += int(w) + draw.textlength(label, font=load_font(10)) + 14

# ---------------------------------------------------------------- map + briefs + footer

CONTINENTS = [
    [(70, 618), (170, 612), (205, 640), (175, 680), (120, 692), (70, 660)],
    [(180, 700), (215, 695), (225, 725), (200, 748), (182, 730)],
    [(330, 622), (365, 614), (385, 632), (360, 652), (330, 646)],
    [(330, 662), (375, 656), (395, 690), (370, 728), (335, 712), (325, 686)],
    [(395, 614), (540, 606), (585, 636), (545, 682), (455, 688), (400, 656)],
    [(540, 712), (580, 706), (590, 728), (552, 740)],
]


def draw_map(draw):
    box(draw, 10, 600, 660, 756, width=1)
    draw.rectangle([12, 602, 658, 754], fill=OCEAN)
    for poly in CONTINENTS:
        draw.polygon(poly, fill=LAND, outline=(120, 140, 100))
    draw.polygon(CONTINENTS[3], fill=LAND2, outline=(120, 140, 100))
    draw.text((18, 606), "WORLD MAP — PINS 1-13", font=load_font(10, bold=True),
              fill=INK)
    for num, px, py in PINS:
        ax, ay = 14 + px, 604 + py
        draw.ellipse([ax - 8, ay - 8, ax + 8, ay + 8], fill=PIN,
                     outline=(255, 255, 255), width=1)
        label = str(num)
        tw = draw.textlength(label, font=load_font(9, bold=True))
        draw.text((ax - tw / 2, ay - 6), label, font=load_font(9, bold=True),
                  fill=(255, 255, 255))
    # legend
    lx = 664
    box(draw, lx, 600, 1014, 756, width=1)
    draw.text((lx + 8, 606), "9 REGIONS — 36 STORIES",
              font=load_font(11, bold=True), fill=RED)
    y = 626
    for i, (name, count) in enumerate(REGIONS):
        col_x = lx + 8 + (i % 3) * 116
        if i % 3 == 0 and i > 0:
            y += 13
        draw.text((col_x, y), "%s %d" % (name, count), font=load_font(10),
                  fill=INK)
    y += 16
    draw.text((lx + 8, y), "HOW SURE:", font=load_font(10, bold=True),
              fill=INK)
    y += 14
    key = [("OFFICIAL", "government / institution"),
           ("CONFIRMED", "two or more wires"),
           ("REPORTED", "one wire"),
           ("CLAIM", "one side claims it"),
           ("ONGOING", "still unfolding")]
    for status, meaning in key:
        fnt = load_font(9, bold=True)
        draw.text((lx + 8, y), status, font=fnt, fill=BLUE)
        w = draw.textlength(status, font=fnt)
        draw.text((lx + 8 + w + 6, y), "= " + meaning, font=load_font(9),
                  fill=INK)
        y += 12


def draw_briefs(draw):
    draw.text((10, 760), "THE BRIEFS — 14-36",
              font=load_font(12, bold=True), fill=RED)
    draw.line([10, 776, 1014, 776], fill=RULE, width=1)
    fnt = load_font(11)
    fsrc = load_font(10, bold=True)
    for i, (num, text, src) in enumerate(BRIEFS):
        if i < 12:
            x, y = 10, 782 + i * 13
        else:
            x, y = 516, 782 + (i - 12) * 13
        draw.text((x, y), "%s. %s" % (num, text), font=fnt, fill=INK)
        w = draw.textlength("%s. %s" % (num, text), font=fnt)
        draw.text((x + w + 4, y), "— " + src, font=fsrc, fill=MUTED)


def draw_datecheck(draw):
    box(draw, 10, 944, 1014, 986, width=1, fill=(255, 243, 224))
    draw.text((16, 947), "DATE CHECK — NOT 26 NOVEMBER, EXCLUDED:",
              font=load_font(10, bold=True), fill=RED)
    cap = "Every story here happened or was first reported on Thu 26 Nov 2026."
    draw.text((1014 - draw.textlength(cap, font=load_font(9)) - 8, 948),
              cap, font=load_font(9), fill=INK)
    fnt = load_font(9)
    for i, (name, date) in enumerate(EXCLUDED):
        col = i % 4
        row = i // 4
        x = 16 + col * 252
        y = 962 + row * 11
        draw.text((x, y), "%s — %s" % (name, date), font=fnt, fill=INK)


def draw_footer(draw):
    draw.text((512 - draw.textlength(
        "Drawn by an AI agent for make.fun — news-image-20261126",
        font=load_font(10)) / 2, 992),
        "Drawn by an AI agent for make.fun — news-image-20261126",
        font=load_font(10), fill=MUTED)
    draw.text((512 - draw.textlength(
        "Scenes are drawn illustrations, not photographs.",
        font=load_font(10)) / 2, 1006),
        "Scenes are drawn illustrations, not photographs.",
        font=load_font(10), fill=MUTED)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    box(draw, 4, 4, 1020, 1020, width=2)
    draw_masthead(draw)
    draw_heroes(draw)
    draw_mediums(draw)
    draw_numbers(draw)
    draw_timeline(draw)
    draw_map(draw)
    draw_briefs(draw)
    draw_datecheck(draw)
    draw_footer(draw)
    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG")
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
