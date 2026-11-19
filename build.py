#!/usr/bin/env python3
"""Genera el sitio de Banquillo: la app de anotación (raíz) y los informes de
nuestros partidos (informes/), a partir de los archivos de data/partidos/."""

import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from src.analysis import analyze  # noqa: E402
from src.render import build_site, page  # noqa: E402

OUT = os.path.join(ROOT, "docs")
NAV = '<div class="nav"><a class="pill" href="../">📋 Volver a la app</a></div>'


def date_key(g):
    try:
        dd, mm, yy = (g.get("date") or "").split("/")
        return (int(yy), int(mm), int(dd))
    except ValueError:
        return (0, 0, 0)


def main():
    os.makedirs(OUT, exist_ok=True)
    # 1. la app en la raíz del sitio
    shutil.copytree(os.path.join(ROOT, "app"), OUT, dirs_exist_ok=True)

    # 2. informes de los partidos exportados
    d = os.path.join(ROOT, "data", "partidos")
    games = []
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not f.endswith(".json"):
            continue
        try:
            with open(os.path.join(d, f), encoding="utf-8") as fh:
                data = json.load(fh)
            games.append(analyze(data["pbp"], data.get("header") or {}, os.path.splitext(f)[0], "EQ"))
        except Exception as e:
            print(f"  ! {f}: {e}")
    out = os.path.join(OUT, "informes")
    if not games:
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(page("Informes", '<header class="top"><div class="kicker">Informes de nuestro equipo</div>'
                          '<h1>Aún no hay partidos</h1><p class="sub">Anota un partido con la app, expórtalo y '
                          'súbelo a la carpeta <b>data/partidos</b> del repositorio.</p>' + NAV + '</header>'))
        print("Sin partidos todavía")
        return
    for i, g in enumerate(sorted(games, key=date_key), 1):
        if not g.get("round"):
            g["round"] = str(i)
    build_site(games, out, competition="de nuestro equipo", extra_nav=NAV,
               footer="Generado a partir del play-by-play anotado con la app Banquillo.")
    print(f"Informes: {len(games)} partidos")


if __name__ == "__main__":
    main()
