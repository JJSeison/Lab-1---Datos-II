from __future__ import annotations
import math, statistics as stats
from typing import List, Optional

import pandas as pd

from src.data import load_dataset, YEARS, CountryRec
from src.tree.avl import AVLTree
from src.vis import export_tree_png
from src.ui import titulo, kv, bullets, yesno, panel, hr

CSV = "data/dataset_climate_change.csv"

# ---------- MÉTRICA DEL ÁRBOL ----------
# "mean"  -> key = temperatura media del país (1961–2022)
# "year"  -> key = valor del año METRIC_YEAR (columna F{METRIC_YEAR})
METRIC = "mean"        # "mean" | "year"
METRIC_YEAR = 2005     # solo aplica si METRIC == "year"

def key_of(rec: CountryRec) -> float:
    if METRIC == "year":
        return float(rec.yearly.get(METRIC_YEAR, math.nan))
    return float(rec.mean_temp)

def _key_label() -> str:
    return "mean" if METRIC == "mean" else f"F{METRIC_YEAR}"

# ---------- CONSULTAS PEDIDAS ----------
def nodo_mayor_promedio_anual(records: List[CountryRec], year: int, df: pd.DataFrame) -> List[CountryRec]:
    media_y = float(df[f"F{year}"].mean(skipna=True))
    return [r for r in records if r.yearly.get(year) is not None and r.yearly[year] > media_y]

def nodo_menor_promedio_global(records: List[CountryRec], year: int, df: pd.DataFrame) -> List[CountryRec]:
    vals = df[[c for c in df.columns if c.startswith("F")]].to_numpy().flatten()
    vals = [v for v in vals if not pd.isna(v)]
    grand_mean = float(stats.mean(vals))
    return [r for r in records if r.yearly.get(year) is not None and r.yearly[year] < grand_mean]

def media_mayor_igual_umbral(records: List[CountryRec], umbral: float) -> List[CountryRec]:
    return [r for r in records if not pd.isna(r.mean_temp) and r.mean_temp >= umbral]

# ---------- CONSTRUCCIÓN DEL ÁRBOL ----------
def build_tree(records: List[CountryRec]) -> AVLTree:
    tree = AVLTree()
    for r in records:
        k = key_of(r)
        if not pd.isna(k):
            tree.insert(k, r)
    return tree

# ---------- UTILIDADES DE MENÚ ----------
def show_levels(tree: AVLTree):
    niveles = tree.levels_iso3()
    titulo("Recorrido por niveles (solo ISO3)")
    for i, lvl in enumerate(niveles):
        print(f"Nivel {i}: " + ", ".join(lvl))

def select_from_list(items: List[CountryRec], prompt: str = "   Índice: ") -> Optional[CountryRec]:
    if not items:
        print("   No hay elementos.")
        return None
    for i, r in enumerate(items):
        mt = "NA" if pd.isna(r.mean_temp) else f"{r.mean_temp:.3f}"
        print(f"   [{i}] {r.country} ({r.iso3})  mean={mt}")
    try:
        raw = input(prompt).strip()
        if raw == "":
            return None
        idx = int(raw)
        return items[idx]
    except Exception:
        print("   Selección inválida.")
        return None

# ================ MENÚ =================
last_selection: list = []  # guarda el último nodo seleccionado (para opción 6)

def main():
    records, df = load_dataset(CSV)
    tree = build_tree(records)

    while True:
        hr("="); print("OPERACIONES"); hr("=")
        print("1) Insertar un nodo (por ISO3)")
        print("2) Eliminar un nodo (por key de la métrica)")
        print("3) Buscar un nodo (por key de la métrica)")
        print("4) Buscar nodos por criterios (a/b/c)")
        print("5) Recorrido por niveles (ISO3)")
        print("6) Nivel / BF / padre / abuelo / tío (del nodo seleccionado)")
        print("7) Exportar imagen del árbol (Graphviz)")
        print("0) Salir")
        op = input(">> ").strip()

        if op == "0":
            print("Hasta luego.")
            break

        elif op == "1":
            iso = input("ISO3 a insertar: ").upper().strip()
            rec = next((r for r in records if r.iso3 == iso), None)
            if not rec:
                print("ISO3 no encontrado en el dataset.")
                continue
            key = key_of(rec)
            if pd.isna(key):
                print("La métrica es NaN para ese país; no se puede insertar.")
                continue
            tree.insert(key, rec)
            print(f"Insertado {rec.country} ({iso}) con key={key:.3f} ({_key_label()}).")
            try:
                export_tree_png(tree, "out/tree_after_insert.png", key_name=_key_label(), key_unit="°C")
                print("Imagen generada: out/tree_after_insert.png")
            except Exception as e:
                print("(Aviso) No se pudo exportar la imagen:", e)

        elif op == "2":
            try:
                key = float(input(f"Key a eliminar (métrica {_key_label()}): "))
                tree.delete(key)
                print("Eliminado por key.")
                try:
                    export_tree_png(tree, "out/tree_after_delete.png", key_name=_key_label(), key_unit="°C")
                    print("Imagen generada: out/tree_after_delete.png")
                except Exception as e:
                    print("(Aviso) No se pudo exportar la imagen:", e)
            except Exception:
                print("Key inválida.")

        elif op == "3":
            try:
                key = float(input(f"Key a buscar (métrica {_key_label()}): "))
                node = tree.search_key(key)
                if node:
                    r = node.payload
                    print(f"Encontrado: {r.country} ({r.iso3})  key={node.key:.3f}")
                    last_selection[:] = [node]
                else:
                    print("No encontrado.")
            except Exception:
                print("Key inválida.")

        elif op == "4":
            print("   Criterios:")
            print("   a) Valor de un año > promedio del año")
            print("   b) Valor de un año < promedio global (todos los años)")
            print("   c) Media del país ≥ umbral")
            sub = input("   Elige (a/b/c): ").lower().strip()

            res: List[CountryRec] = []
            if sub == "a":
                y = int(input("   Año (p.ej. 2005): "))
                res = nodo_mayor_promedio_anual(records, y, df)
            elif sub == "b":
                y = int(input("   Año (p.ej. 2005): "))
                res = nodo_menor_promedio_global(records, y, df)
            elif sub == "c":
                u = float(input("   Umbral (°C): "))
                res = media_mayor_igual_umbral(records, u)
            else:
                print("   Opción inválida."); continue

            print(f"   Se encontraron {len(res)} países.")
            sel = select_from_list(res, prompt="   Índice para seleccionar (enter para omitir): ")
            if sel:
                node = tree.search_key(key_of(sel))
                if node:
                    last_selection[:] = [node]
                    print(f"   Seleccionado: {sel.country} ({sel.iso3}). Usa opción 6 para ver nivel/BF/familia.")

        elif op == "5":
            show_levels(tree)

        elif op == "6":
            if not last_selection:
                print("Primero usa la opción 3 o 4 para seleccionar un nodo.")
                continue
            node = last_selection[0]
            lvl = tree.level_of(node)
            bf = node.balance_factor()
            padre = node.parent.payload.iso3 if node.parent else "—"
            abuelo = node.grandparent().payload.iso3 if node.grandparent() else "—"
            tio = node.uncle().payload.iso3 if node.uncle() else "—"
            panel(
                f"País: {node.payload.country} ({node.payload.iso3})\n"
                f"Key[{_key_label()}]: {node.key:.3f} °C\n"
                f"Nivel: {lvl}\n"
                f"BF: {bf}\n"
                f"Padre: {padre}\n"
                f"Abuelo: {abuelo}\n"
                f"Tío: {tio}",
                title="Nodo seleccionado"
            )

        elif op == "7":
            try:
                export_tree_png(tree, "out/tree.png", key_name=_key_label(), key_unit="°C")
                print("Imagen generada: out/tree.png")
            except Exception as e:
                print("(Aviso) No se pudo exportar la imagen:", e)

        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()