"""Draws the Aiding Allies network, optionally with chosen arcs highlighted."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from data import ORIGINS, PORTS, AIRFIELDS, CITIES

POS = {
    "Boston": (0, 3.6), "Jacksonville": (0, 1.4),
    "Hamburg": (4, 5.0), "Rotterdam": (4, 4.0), "Napoli": (4, 3.0),
    "London": (4, 2.0), "Berlin": (4, 1.0), "Istanbul": (4, 0.0),
    "St Petersburg": (8, 4.0), "Moscow": (8, 2.5), "Rostov": (8, 1.0),
}
COLOUR = {"Transport": "#1f5fbf", "Truck": "#2e8b57", "Globemaster": "#d9822b"}
STYLE = {"Transport": "--", "Truck": ":", "Globemaster": "-"}
FILL = {**{n: "#dbe7f7" for n in ORIGINS}, **{n: "#cfe0f5" for n in PORTS},
        **{n: "#fbe3c8" for n in AIRFIELDS}, **{n: "#f6d4d4" for n in CITIES}}


def _ends(a, b):
    (x1, y1), (x2, y2) = POS[a], POS[b]
    t0, t1 = 0.55 / 4, 1 - 0.5 / 4
    return (x1 + (x2 - x1) * t0, y1 + (y2 - y1) * t0), (x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1)


def draw(arcs, highlight=None, labels=None, title="", node_labels=None):
    """arcs: DataFrame with From, To, Vehicle. highlight: set of (from, to). labels: {(from, to): text}."""
    highlight = highlight or set()
    labels = labels or {}
    node_labels = node_labels or {}
    fig, ax = plt.subplots(figsize=(10.5, 6.4), dpi=110)
    for _, r in arcs.iterrows():
        a, b, v = r["From"], r["To"], r["Vehicle"]
        s, e = _ends(a, b)
        on = (a, b) in highlight
        if not highlight:  # plain network: everything in colour
            col, lw, al = COLOUR[v], 1.3, 0.8
        else:
            col, lw, al = (COLOUR[v], 3.4, 0.95) if on else ("#cccccc", 0.9, 0.7)
        ax.annotate("", xy=e, xytext=s, arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, ls=STYLE[v],
                                                        alpha=al, shrinkA=0, shrinkB=0))
        if (a, b) in labels:
            mx, my = s[0] + (e[0] - s[0]) * 0.42, s[1] + (e[1] - s[1]) * 0.42
            ax.text(mx, my, labels[(a, b)], fontsize=8.5, fontweight="bold", color=COLOUR[v], ha="center",
                    va="center", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=COLOUR[v], lw=0.8))
    for n, (x, y) in POS.items():
        ax.text(x, y, node_labels.get(n, n), ha="center", va="center", fontsize=9.5, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.45", fc=FILL[n], ec="#444", lw=1))
    for x, t in [(0, "UNITED STATES"), (4, "NATO PORTS / AIRFIELDS"), (8, "RUSSIAN FEDERATION")]:
        ax.text(x, 5.9, t, ha="center", fontsize=10, fontweight="bold", color="#333")
    h = [Line2D([0], [0], color=COLOUR["Transport"], ls="--", lw=2.5, label="Transport ship"),
         Line2D([0], [0], color=COLOUR["Truck"], ls=":", lw=2.5, label="PLS truck"),
         Line2D([0], [0], color=COLOUR["Globemaster"], lw=2.5, label="Globemaster")]
    if highlight:
        h.append(Line2D([0], [0], color="#cccccc", lw=1, label="Not used"))
    ax.legend(handles=h, loc="lower center", bbox_to_anchor=(0.5, -0.12), ncol=len(h), frameon=False, fontsize=9)
    ax.set_xlim(-1.1, 9.1); ax.set_ylim(-0.6, 6.2); ax.axis("off")
    if title:
        ax.set_title(title, fontsize=11.5, fontweight="bold")
    fig.tight_layout()
    return fig
