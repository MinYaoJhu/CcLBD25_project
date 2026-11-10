"""Generate the logo (assets/logo.svg) and workflow figure (assets/workflow.svg).

Green & gold palette shared with Cuscuta_LCM_project. The workflow shows the
tissue-type RNA-seq data (Ranjan et al. 2014) analyzed here with MDS, PCA,
a 6x2 SOM (kohonen numbering: SOM9 = top row, third unit) and a gene
co-expression network. Pure Python, fixed seeds.

Usage: python3 assets/make_figures.py
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).parent
BG, BG2, EDGE = "#13261F", "#1C3A2F", "#E3B23C"          # dark forest green, panel green, gold
HOST, HOST_LT, HOST_DK, VASC = "#4E9A5B", "#7FBF7A", "#2F6B3B", "#C9E4A6"
DODDER, DODDER_DK = "#F0A93B", "#C27A17"
TEXT, SOFT = "#FFFFFF", "#A9C7B4"
STAGE = {"Early": "#F6D28B", "Intermediate": "#F0A93B", "Mature": "#D9731A", "Control": "#7FBF7A"}
SANS = 'font-family="Inter, -apple-system, Segoe UI, Helvetica, Arial, sans-serif"'
MONO = 'font-family="SFMono-Regular, Menlo, Consolas, monospace"'


class Doc:
    def __init__(self, w, h, seed=7):
        self.w, self.h, self.b, self.defs = w, h, [], []
        self.rng = random.Random(seed)
        self.n = 0

    def add(self, s):
        self.b.append(s)

    def uid(self):
        self.n += 1
        return f"k{self.n}"

    def svg(self, label):
        mk = (f'<marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" '
              f'orient="auto-start-reverse"><path d="M1.5 1.5L8 5L1.5 8.5" fill="none" stroke="{EDGE}" '
              f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></marker>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
                f'height="{self.h}" role="img" aria-label="{label}">\n<defs>{mk}{"".join(self.defs)}</defs>\n'
                + "\n".join(self.b) + "\n</svg>\n")

    def T(self, x, y, t, size=13, w=400, fill=TEXT, anchor="middle", font=SANS, ls=None):
        t = str(t).replace("&", "&amp;")
        e = f' letter-spacing="{ls}"' if ls else ""
        self.add(f'<text x="{x}" y="{y}" {font} font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}"{e}>{t}</text>')

    def arrow(self, x1, y1, x2, y2):
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{EDGE}" stroke-width="2" stroke-linecap="round" marker-end="url(#ah)"/>')

    # ------------------------------------------------------------ icons
    def stem_section(self, cx, cy, r, stage=None, laser=False, beam=False):
        """Tomato stem cross-section (epidermis, cortex, vascular ring, pith) with a dodder
        stem attached at the upper right. Early: prehaustorium touching the surface;
        Intermediate: haustorium in the cortex; Mature: connected to a vascular bundle."""
        ang = -math.pi / 4
        ring = 0.60                       # vascular bundles sit on this ring (fraction of r)
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{HOST}" stroke="{HOST_DK}" stroke-width="2.2"/>')
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.93:.1f}" fill="none" stroke="{HOST_LT}" stroke-width="1" opacity="0.6"/>')
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.48:.1f}" fill="{HOST_LT}" opacity="0.45"/>')   # pith
        for k in range(10):               # one bundle exactly where the haustorium arrives
            a = ang + k / 10 * 2 * math.pi
            bx, by = cx + r * ring * math.cos(a), cy + r * ring * math.sin(a)
            hit = (k == 0 and stage == "Mature")
            self.add(f'<ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="{r * 0.1:.1f}" ry="{r * 0.065:.1f}" '
                     f'fill="{EDGE if hit else VASC}" stroke="{HOST_DK}" stroke-width="0.9" '
                     f'transform="rotate({math.degrees(a):.0f} {bx:.1f} {by:.1f})"/>')
        if stage is None:
            return
        ux, uy = math.cos(ang), math.sin(ang)          # outward direction
        px, py = -uy, ux                               # perpendicular
        dr = r * 0.4
        gap = {"Early": 0.06, "Intermediate": 0.0, "Mature": 0.0}[stage]
        dx, dy = cx + (r + dr * (1 + gap)) * ux, cy + (r + dr * (1 + gap)) * uy
        sx, sy = cx + r * 1.0 * ux, cy + r * 1.0 * uy   # host surface point
        if stage == "Early":
            # prehaustorium: a swelling pressed flat against the epidermis, no penetration
            mx, my = cx + (r + dr * 0.42) * ux, cy + (r + dr * 0.42) * uy
            self.add(f'<ellipse cx="{mx:.1f}" cy="{my:.1f}" rx="{dr * 0.45:.1f}" ry="{dr * 0.62:.1f}" fill="{DODDER}" '
                     f'stroke="{DODDER_DK}" stroke-width="1.2" transform="rotate({math.degrees(ang):.0f} {mx:.1f} {my:.1f})"/>')
            self.add(f'<path d="M{sx + px * dr * 0.5:.1f},{sy + py * dr * 0.5:.1f} L{sx - px * dr * 0.5:.1f},{sy - py * dr * 0.5:.1f}" '
                     f'stroke="{DODDER_DK}" stroke-width="2.4" stroke-linecap="round"/>')
            tipx, tipy = sx, sy
        else:
            depth = {"Intermediate": 0.22, "Mature": 0.30}[stage]
            tipx, tipy = cx + r * (1 - depth) * ux, cy + r * (1 - depth) * uy
            w = r * 0.17
            self.add(f'<path d="M{sx + px * w:.1f},{sy + py * w:.1f} L{tipx + px * w * 0.35:.1f},{tipy + py * w * 0.35:.1f} '
                     f'Q{tipx - ux * 2:.1f},{tipy - uy * 2:.1f} {tipx - px * w * 0.35:.1f},{tipy - py * w * 0.35:.1f} '
                     f'L{sx - px * w:.1f},{sy - py * w:.1f} Z" fill="{DODDER}" stroke="{DODDER_DK}" stroke-width="1"/>')
            if stage == "Intermediate":   # searching hyphae spreading in the cortex
                for sgn in (-1, 0, 1):
                    ex = tipx - ux * r * 0.06 + sgn * px * r * 0.14
                    ey = tipy - uy * r * 0.06 + sgn * py * r * 0.14
                    self.add(f'<path d="M{tipx:.1f},{tipy:.1f} L{ex:.1f},{ey:.1f}" stroke="{DODDER}" stroke-width="1.5" stroke-linecap="round"/>')
            else:                          # hyphae bridging to the vascular bundle in the ring
                bx, by = cx + r * ring * ux, cy + r * ring * uy
                for sgn in (-1, 1):
                    self.add(f'<path d="M{tipx + sgn * px * r * 0.04:.1f},{tipy + sgn * py * r * 0.04:.1f} '
                             f'L{bx + sgn * px * r * 0.05 + ux * r * 0.05:.1f},{by + sgn * py * r * 0.05 + uy * r * 0.05:.1f}" '
                             f'stroke="{DODDER_DK}" stroke-width="1.8" stroke-linecap="round"/>')
        self.add(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="{dr:.1f}" fill="{DODDER}" stroke="{DODDER_DK}" stroke-width="1.5"/>')
        self.add(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="{dr * 0.42:.1f}" fill="{DODDER_DK}" opacity="0.35"/>')
        if laser:
            mx, my = (sx + tipx) / 2 + ux * r * 0.02, (sy + tipy) / 2 + uy * r * 0.02
            rx = max(r * 0.2, math.hypot(sx - tipx, sy - tipy) / 2 + r * 0.12)
            self.add(f'<ellipse cx="{mx:.1f}" cy="{my:.1f}" rx="{rx:.1f}" ry="{r * 0.26:.1f}" fill="none" stroke="{EDGE}" '
                     f'stroke-width="2" stroke-dasharray="4 3" transform="rotate({math.degrees(ang):.0f} {mx:.1f} {my:.1f})"/>')
        if beam:
            mx, my = (sx + tipx) / 2, (sy + tipy) / 2
            self.add(f'<path d="M{mx - 26:.1f},{cy - r - 34:.1f} L{mx:.1f},{my:.1f}" stroke="{EDGE}" stroke-width="3" stroke-linecap="round" opacity="0.9"/>')
            self.add(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="4" fill="{TEXT}" stroke="{EDGE}" stroke-width="2"/>')

    def tube(self, cx, cy, col, label):
        self.add(f'<path d="M{cx - 11},{cy - 30} h22 v40 a11,11 0 0 1 -22,0 z" fill="{BG2}" stroke="{SOFT}" stroke-width="1.5"/>')
        self.add(f'<path d="M{cx - 11},{cy - 2} h22 v12 a11,11 0 0 1 -22,0 z" fill="{col}"/>')
        self.add(f'<rect x="{cx - 14}" y="{cy - 34}" width="28" height="6" rx="2" fill="{SOFT}"/>')
        self.T(cx, cy + 40, label, 11, 600, col)

    def reads(self, cx, cy):
        for i in range(6):
            off = self.rng.randrange(-16, 10)
            for j, c in enumerate(["#4E9A5B", "#F0A93B", "#E3B23C", "#7FBF7A"][: 2 + i % 3]):
                self.add(f'<rect x="{cx - 30 + off + j * 14}" y="{cy - 28 + i * 10}" width="12" height="6" rx="1.5" fill="{c}" opacity="0.9"/>')

    def scatter(self, cx, cy, s=38, kind="mds"):
        self.add(f'<rect x="{cx - s}" y="{cy - s}" width="{2 * s}" height="{2 * s}" rx="8" fill="{BG2}" stroke="#2E5444"/>')
        self.add(f'<path d="M{cx - s + 8},{cy + s - 8} H{cx + s - 6} M{cx - s + 8},{cy + s - 8} V{cy - s + 6}" stroke="{SOFT}" stroke-width="1.2" fill="none"/>')
        centers = {"Early": (-0.45, 0.35), "Intermediate": (0.05, -0.35), "Mature": (0.5, 0.25)}
        if kind == "pca":
            centers = {"Early": (-0.5, 0.0), "Intermediate": (0.1, -0.4), "Mature": (0.45, 0.4)}
        for st, (ux, uy) in centers.items():
            for _ in range(4):
                self.add(f'<circle cx="{cx + (ux + self.rng.uniform(-0.12, 0.12)) * s * 0.85:.1f}" '
                         f'cy="{cy + (uy + self.rng.uniform(-0.12, 0.12)) * s * 0.85:.1f}" r="3.6" fill="{STAGE[st]}"/>')

    def som(self, cx, cy, r=13):
        cols = ["#F6D28B", "#F0A93B", "#D9731A", "#7FBF7A", "#4E9A5B", "#E3B23C"]
        k = 0
        for row in range(2):
            for col in range(3):
                x = cx + (col - 1) * r * 1.75 + (r * 0.875 if row else 0) - r * 0.44
                y = cy + (row - 0.5) * r * 1.52
                pts = " ".join(f"{x + r * math.cos(math.radians(60 * i - 30)):.1f},{y + r * math.sin(math.radians(60 * i - 30)):.1f}" for i in range(6))
                self.add(f'<polygon points="{pts}" fill="{cols[k]}" stroke="{BG}" stroke-width="2"/>')
                k += 1



def badge_frame(d):
    d.add(f'<rect x="6" y="6" width="228" height="228" rx="42" fill="{BG}" stroke="{EDGE}" stroke-width="7"/>')


FONT = 'font-family="Helvetica, Arial, sans-serif"'


def name(d):
    d.T(120, 197, "CcLBD25", 25, 700, TEXT, font=FONT)
    d.T(120, 219, "HAUSTORIUM GCN", 13, 400, EDGE, font=FONT, ls="2")


def network(d, cx, cy, s, hub=True, seed=1):
    """Small gene co-expression network: a gold hub (CcLBD25) linked to green/orange genes."""
    import random
    rng = random.Random(seed)
    nodes = [(cx, cy)]
    for k in range(9):
        a = k / 9 * 2 * math.pi + rng.uniform(-0.2, 0.2)
        rr = s * rng.uniform(0.55, 1.0)
        nodes.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    edges = [(0, i) for i in range(1, 10)] + [(1, 2), (3, 4), (4, 5), (6, 7), (8, 9), (2, 3), (7, 8)]
    for i, j in edges:
        (x1, y1), (x2, y2) = nodes[i], nodes[j]
        d.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{SOFT}" stroke-width="1.6" opacity="0.8"/>')
    for i, (x, y) in enumerate(nodes[1:], 1):
        col = [HOST_LT, DODDER, HOST][i % 3]
        d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s * 0.11:.1f}" fill="{col}" stroke="{BG}" stroke-width="1.5"/>')
    if hub:
        d.add(f'<circle cx="{cx}" cy="{cy}" r="{s * 0.2:.1f}" fill="{EDGE}" stroke="{TEXT}" stroke-width="2"/>')


def logo():
    d = Doc(240, 240, 3)
    badge_frame(d)
    network(d, 120, 92, 62, seed=2)
    name(d)
    return d


def tissue_icon(d, x, y, kind):
    if kind == "Seeds":
        for dx, dy in [(-9, 4), (6, -4), (8, 10)]:
            d.add(f'<ellipse cx="{x + dx}" cy="{y + dy}" rx="8" ry="6" fill="#B07A3A" stroke="{DODDER_DK}" stroke-width="1"/>')
    elif kind == "Seedlings":
        d.add(f'<path d="M{x - 2},{y + 22} C{x - 6},{y + 4} {x + 10},{y - 4} {x + 4},{y - 20}" fill="none" stroke="{DODDER}" stroke-width="5" stroke-linecap="round"/>')
        d.add(f'<path d="M{x - 2},{y + 22} q-8,4 -14,2 M{x - 2},{y + 22} q6,6 12,4" stroke="#B07A3A" stroke-width="2" fill="none"/>')
    elif kind == "Stems":
        d.add(f'<path d="M{x - 22},{y + 12} C{x - 10},{y - 20} {x + 8},{y + 22} {x + 22},{y - 14}" fill="none" stroke="{DODDER}" stroke-width="6" stroke-linecap="round"/>')
    elif kind == "Prehaustoria":
        d.add(f'<rect x="{x + 6}" y="{y - 24}" width="10" height="48" rx="5" fill="{HOST}"/>')
        d.add(f'<path d="M{x - 22},{y - 8} Q{x - 4},{y + 6} {x + 4},{y + 2}" fill="none" stroke="{DODDER}" stroke-width="6" stroke-linecap="round"/>')
        d.add(f'<ellipse cx="{x + 5}" cy="{y + 2}" rx="4" ry="6" fill="{DODDER_DK}"/>')
    elif kind == "Haustoria":
        d.add(f'<rect x="{x + 2}" y="{y - 24}" width="16" height="48" rx="8" fill="{HOST}"/>')
        d.add(f'<path d="M{x - 22},{y - 6} Q{x - 6},{y + 6} {x + 2},{y + 2}" fill="none" stroke="{DODDER}" stroke-width="6" stroke-linecap="round"/>')
        d.add(f'<path d="M{x + 1},{y - 3} L{x + 12},{y + 2} L{x + 1},{y + 7} Z" fill="{DODDER}" stroke="{DODDER_DK}" stroke-width="1"/>')
    elif kind == "Flowers":
        for dx, dy in [(-8, -6), (6, -8), (0, 6), (10, 6), (-10, 8)]:
            d.add(f'<circle cx="{x + dx}" cy="{y + dy}" r="6.5" fill="#F4EBD8" stroke="#C9BFA8" stroke-width="1"/>')
            d.add(f'<circle cx="{x + dx}" cy="{y + dy}" r="2" fill="{EDGE}"/>')


def som_grid(d, cx, cy, r=11, hi=8):
    cols = ["#F6D28B", "#F0A93B", "#D9731A", "#7FBF7A", "#4E9A5B", "#E3B23C"]
    k = 0
    for row in range(2):
        for col in range(6):
            x = cx + (col - 2.5) * r * 1.75 + (r * 0.875 if row else 0) - r * 0.44
            y = cy - (row - 0.5) * r * 1.52   # kohonen: units 1-6 bottom row, 7-12 top row
            pts = " ".join(f"{x + r * math.cos(math.radians(60 * i - 30)):.1f},{y + r * math.sin(math.radians(60 * i - 30)):.1f}" for i in range(6))
            sel = (k == hi)
            d.add(f'<polygon points="{pts}" fill="{EDGE if sel else cols[k % 6]}" fill-opacity="{1 if sel else 0.55}" '
                  f'stroke="{TEXT if sel else BG}" stroke-width="{2.2 if sel else 1.5}"/>')
            k += 1


def workflow():
    d = Doc(1000, 450, 9)
    d.add(f'<rect x="0" y="0" width="1000" height="450" rx="18" fill="{BG}"/>')
    d.T(40, 42, "1 · TISSUE-TYPE RNA-SEQ (RANJAN ET AL. 2014)", 12, 700, EDGE, "start", ls="1.5")
    d.T(40, 258, "2 · ANALYSIS IN THIS REPOSITORY", 12, 700, EDGE, "start", ls="1.5")
    y1 = 118
    for i, k in enumerate(["Seeds", "Seedlings", "Stems", "Prehaustoria", "Haustoria", "Flowers"]):
        x = 75 + i * 100
        d.add(f'<circle cx="{x}" cy="{y1}" r="38" fill="{BG2}" stroke="#2E5444" stroke-width="1.5"/>')
        tissue_icon(d, x, y1, k)
        d.T(x, y1 + 60, k, 12.5, 600, TEXT)
    d.T(325, y1 + 82, "six Cuscuta campestris tissues", 11, 400, SOFT)
    d.arrow(640, y1, 700, y1)
    d.add(f'<rect x="712" y="{y1 - 40}" width="240" height="80" rx="12" fill="#0E1C17" stroke="{EDGE}" stroke-width="2"/>')
    d.T(832, y1 - 8, "TMM-normalized counts", 13, 700, EDGE, font=MONO)
    d.T(832, y1 + 16, "edgeR · genome: Vogel et al. 2018", 11, 400, SOFT)
    d.add(f'<path d="M832,{y1 + 44} V222 H75 V292" fill="none" stroke="{SOFT}" stroke-width="1.5" stroke-dasharray="5 5" marker-end="url(#ah)"/>')
    y2 = 345
    d.scatter(85, y2, 34, "mds")
    d.T(85, y2 + 52, "MDS", 13.5, 600)
    d.arrow(128, y2, 170, y2)
    d.scatter(215, y2, 34, "pca")
    d.T(215, y2 + 52, "PCA", 13.5, 600)
    d.T(215, y2 + 69, "CV > 0.85", 11, 400, SOFT, font=MONO)
    d.arrow(258, y2, 300, y2)
    som_grid(d, 395, y2)
    d.T(395, y2 + 52, "SOM 6×2", 13.5, 600)
    d.T(395, y2 + 69, "SOM9 selected", 11, 400, EDGE)
    d.arrow(490, y2, 545, y2)
    network(d, 610, y2, 40, seed=3)
    d.T(610, y2 + 60, "Co-expression network", 13.5, 600)
    d.T(610, y2 + 77, "normal quantile 0.93", 11, 400, SOFT, font=MONO)
    d.arrow(675, y2, 730, y2)
    d.add(f'<rect x="742" y="{y2 - 34}" width="200" height="68" rx="10" fill="{BG2}" stroke="#2E5444"/>')
    d.T(842, y2 - 6, "Edge & node tables", 13, 600)
    d.T(842, y2 + 14, "→ Cytoscape (RCy3)", 11.5, 400, SOFT)
    d.T(842, y2 + 52, "key regulators incl. CcLBD25", 11, 400, EDGE)
    return d


if __name__ == "__main__":
    (OUT / "logo.svg").write_text(logo().svg("CcLBD25 logo"))
    (OUT / "workflow.svg").write_text(workflow().svg("CcLBD25 workflow"))
    print("wrote assets/logo.svg and assets/workflow.svg")
