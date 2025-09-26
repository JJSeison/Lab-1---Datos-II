from __future__ import annotations

import math
import pandas as pd

from src.data import load_dataset, YEARS, CountryRec
from src.tree.avl import AVLTree, AVLNode
from src.ui import titulo, hr, panel  # kv/yesno NO son necesarios aquí
from src.vis import export_tree_png

# ===================== Config de la métrica =====================
# "mean" = promedio del período; "year" = un año específico (METRIC_YEAR)
METRIC = "mean"          # "mean" | "year"
METRIC_YEAR = 2005


def _key_label() -> str:
    return "mean" if METRIC == "mean" else f"F{METRIC_YEAR}"


def key_of(rec: CountryRec) -> float:
    if METRIC == "mean":
        return rec.mean_temp
    return rec.yearly.get(METRIC_YEAR, math.nan)


# ===================== Utils de negocio =====================
def build_tree(records: list[CountryRec]) -> AVLTree:
    t = AVLTree()
    for r in records:
        k = key_of(r)
        if pd.isna(k):  # salta países sin dato en la métrica
            continue
        t.insert(k, r)
    return t


def find_node_by_iso3(tree: AVLTree, iso3: str) -> AVLNode | None:
    """Búsqueda por ISO3 recorriendo el árbol (BFS)."""
    if not tree.root:
        return None
    q: list[AVLNode] = [tree.root]
    iso3 = iso3.upper()
    while q:
        n = q.pop(0)
        if getattr(n.payload, "iso3", "").upper() == iso3:
            return n
        if n.left:
            q.append(n.left)
        if n.right:
            q.append(n.right)
    return None


def show_levels(tree: AVLTree) -> None:
    titulo("Recorrido por niveles (solo ISO3)")
    for i, lvl in enumerate(tree.levels_iso3()):
        print(f"Nivel {i}: {', '.join(lvl)}")
    hr()


# ===================== Criterios del enunciado =====================
def criterio_a(records: list[CountryRec], year: int, df: pd.DataFrame) -> list[CountryRec]:
    """a) valor del país en 'year' > promedio de todos los países en ese 'year'"""
    col = f"F{year}"
    media = df[col].mean(skipna=True)
    return [r for r in records if r.yearly.get(year) is not None and r.yearly[year] > media]


def criterio_b(records: list[CountryRec], year: int, df: pd.DataFrame) -> list[CountryRec]:
    """b) valor del país en 'year' < promedio global de todos los países en todos los años"""
    media_global = df[[f"F{y}" for y in YEARS]].stack().mean(skipna=True)
    return [r for r in records if r.yearly.get(year) is not None and r.yearly[year] < media_global]


def criterio_c(records: list[CountryRec], umbral: float) -> list[CountryRec]:
    """c) mean >= umbral"""
    return [r for r in records if r.mean_temp is not None and r.mean_temp >= umbral]


# ===================== App =====================
def main():
    CSV = "data/dataset_climate_change.csv"
    records, df = load_dataset(CSV)
    tree = build_tree(records)
    selected: AVLNode | None = None

    while True:
        titulo("OPERACIONES")
        print("1) Insertar un nodo (por ISO3)")
        print("2) Eliminar un nodo (por key o ISO3)")
        print("3) Buscar un nodo (por key o ISO3)")
        print("4) Buscar nodos por criterios (a/b/c)")
        print("5) Recorrido por niveles (ISO3)")
        print("6) Nivel / BF / padre / abuelo / tío (del nodo seleccionado)")
        print("7) Exportar imagen del árbol (Graphviz)")
        print("0) Salir")
        op = input(">> ").strip()

        # ------------- 1) Insertar (evita duplicados por ISO3) -------------
        if op == "1":
            iso = input("ISO3 a insertar: ").upper().strip()
            rec = next((r for r in records if r.iso3.upper() == iso), None)
            if not rec:
                print("ISO3 no encontrado en el dataset.")
                hr(); continue

            # evitar duplicado por ISO3
            existing = find_node_by_iso3(tree, iso)
            if existing:
                print(f"{iso} ya existe en el árbol con key={existing.key:.3f}. No se inserta duplicado.")
                hr(); continue

            k = key_of(rec)
            if pd.isna(k):
                print("La métrica es NaN para ese país; no se puede insertar.")
                hr(); continue

            tree.insert(k, rec)
            print(f"Insertado {rec.country} ({iso}) con key={k:.3f} ({_key_label()}).")
            try:
                export_tree_png(tree, "out/tree_after_insert.png", key_name=_key_label(), key_unit="°C")
                print("Imagen generada: out/tree_after_insert.png")
            except Exception as e:
                print("(Aviso) No se pudo exportar la imagen:", e)
            hr()

        # ------------- 2) Eliminar (por key o ISO3) -------------
        elif op == "2":
            s = input("Key a eliminar (o ISO3): ").strip().upper()
            node: AVLNode | None = None
            # ¿es número?
            try:
                k = float(s)
                node = tree.search_key(k)
            except ValueError:
                node = find_node_by_iso3(tree, s)

            if not node:
                print("No encontrado.")
                hr(); continue

            tree.delete(node.key)
            iso = getattr(node.payload, "iso3", "?")
            print(f"Eliminado {iso} (key={node.key:.3f}).")
            try:
                export_tree_png(tree, "out/tree_after_delete.png", key_name=_key_label(), key_unit="°C")
                print("Imagen generada: out/tree_after_delete.png")
            except Exception as e:
                print("(Aviso) No se pudo exportar la imagen:", e)

            if selected is node:
                selected = None
            hr()

        # ------------- 3) Buscar (por key o ISO3) -------------
        elif op == "3":
            s = input("Key o ISO3 a buscar: ").strip().upper()
            node: AVLNode | None = None
            try:
                k = float(s)
                node = tree.search_key(k)
            except ValueError:
                node = find_node_by_iso3(tree, s)

            if not node:
                print("No encontrado.")
            else:
                selected = node
                r: CountryRec = node.payload
                body = (
                    f"País: {r.country} ({r.iso3})\n"
                    f"Key: {node.key:.3f} ({_key_label()})\n"
                    f"BF: {node.balance_factor()}"
                )
                panel("Nodo seleccionado", body)
            hr()

        # ------------- 4) Criterios a/b/c -------------
        elif op == "4":
            print("a) año dado > promedio de ese año")
            print("b) año dado < promedio global de todos los años")
            print("c) media >= umbral")
            sub = input("Opción (a/b/c): ").strip().lower()

            if sub == "a":
                y = int(input(f"Año {YEARS[0]}..{YEARS[-1]}: "))
                lst = criterio_a(records, y, df)
            elif sub == "b":
                y = int(input(f"Año {YEARS[0]}..{YEARS[-1]}: "))
                lst = criterio_b(records, y, df)
            elif sub == "c":
                um = float(input("Umbral (°C): "))
                lst = criterio_c(records, um)
            else:
                print("Opción inválida.")
                hr(); continue

            if not lst:
                print("No hay resultados.")
                hr(); continue

            # listar (muestra índice para poder seleccionar uno)
            for i, r in enumerate(lst):
                print(f"[{i:02d}] {r.country} ({r.iso3})  mean={r.mean_temp:.3f}")
            s = input("Índice para seleccionar (enter para omitir): ").strip()
            if s != "":
                try:
                    idx = int(s)
                    rec = lst[idx]
                    node = find_node_by_iso3(tree, rec.iso3)
                    if node:
                        selected = node
                        print(f"Seleccionado {rec.country} ({rec.iso3}).")
                    else:
                        print("Ese país no está en el árbol.")
                except Exception:
                    print("Selección inválida.")
            hr()

        # ------------- 5) Niveles -------------
        elif op == "5":
            show_levels(tree)

        # ------------- 6) Info del nodo seleccionado -------------
        elif op == "6":
            if not selected:
                print("No hay nodo seleccionado (usa la opción 3 o 4).")
                hr(); continue

            r: CountryRec = selected.payload
            print(f"ISO3:  {r.iso3} - {r.country}")
            print(f"Nivel: {tree.level_of(selected)}")
            print(f"BF:    {selected.balance_factor()}")

            p = selected.parent
            g = selected.grandparent()
            u = selected.uncle()
            if p:
                print(f"Padre:  {getattr(p.payload, 'iso3', '?')}")
            if g:
                print(f"Abuelo: {getattr(g.payload, 'iso3', '?')}")
            if u:
                print(f"Tío:    {getattr(u.payload, 'iso3', '?')}")
            hr()

        # ------------- 7) Exportar PNG -------------
        elif op == "7":
            try:
                export_tree_png(tree, "out/tree.png", key_name=_key_label(), key_unit="°C")
                print("Imagen generada: out/tree.png")
            except Exception as e:
                print("(Aviso) No se pudo exportar la imagen:", e)
            hr()

        elif op == "0":
            break
        else:
            print("Opción inválida.")
            hr()


if __name__ == "__main__":
    main()




