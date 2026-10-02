""" Gráfica de curvas H2 y C13 (matplotlib, sin ventanas: backend Agg) """
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from datos import tiempos_medicion

COLOR_H2 = "#7DB4E6"
COLOR_C13 = "#333333"

# Proporción del gráfico en el PDF (ancho x alto en mm)
ANCHO_MM, ALTO_MM = 128, 72


def crear_grafico(reg, cfg):
    """Devuelve un BytesIO con la imagen PNG de la gráfica."""

    est = cfg["estudio"]
    fig, ax = plt.subplots(figsize=(ANCHO_MM / 25.4, ALTO_MM / 25.4), dpi=220)

    t_h2 = sorted(reg["h2"])
    t_c13 = sorted(reg["c13"])
    ax.plot(t_h2, [reg["h2"][t] for t in t_h2], color=COLOR_H2, marker="o", markersize=3.5, linewidth=1.3, label="H2")
    ax.plot(t_c13, [reg["c13"][t] for t in t_c13], color=COLOR_C13, marker="D", markersize=3, linewidth=1.3, label="C13")

    maximo = max(list(reg["h2"].values()) + list(reg["c13"].values()) + [8])
    ax.set_ylim(0, maximo * 1.15)
    ax.set_xlim(-6, est["duracion_min"] + 6)
    pasos = tiempos_medicion(cfg, reg["intervalo_tiempo"])
    ax.set_xticks(pasos)
    ax.set_xticklabels([f"{t:02d}" for t in pasos], fontsize=6.5, color="#555555")
    ax.tick_params(axis="y", labelsize=6.5, colors="#555555", length=0)
    ax.tick_params(axis="x", length=3, color="#BBBBBB")
    ax.set_ylabel("ppm", fontsize=6.5, color="#555555")
    ax.yaxis.grid(True, color="#DDDDDD", linewidth=0.6)
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)

    ax.spines["bottom"].set_color("#BBBBBB")

    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False, fontsize=7, handlelength=1.6)

    fig.suptitle(est["titulo_grafico"], fontsize=10.5, fontweight="bold", color="#222222", y=0.965)
    fig.text(0.5, 0.875, cfg["centro"]["web"], ha="center", fontsize=6.5, color="#777777")
    fig.subplots_adjust(left=0.08, right=0.86, top=0.80, bottom=0.11)

    buf = BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    
    return buf
