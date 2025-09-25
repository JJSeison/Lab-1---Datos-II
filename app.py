from __future__ import annotations
from src.data import load_dataset, YEARS
from src.tree.avl import AVLTree

CSV = "data/dataset_climate_change.csv"

# --- Consultas "a", "b" y "c" ---

def a(df, year: int, iso3: str) -> bool:
    """¿Temp del país en 'year' > promedio de todos los países ese año?"""
    col = f"F{year}"
    ymean = df[col].mean(skipna=True)
    row = df[df["ISO3"] == iso3]
    return (not row.empty) and (float(row.iloc[0][col]) > float(ymean))

def b(df, year: int, iso3: str) -> bool:
    """¿Temp del país en 'year' < promedio global (todos los países × años)?"""
    cols = [f"F{y}" for y in YEARS]
    global_mean = df[cols].stack().mean(skipna=True)
    row = df[df["ISO3"] == iso3]
    return (not row.empty) and (float(row.iloc[0][f"F{year}"]) < float(global_mean))

def c(mean_temp: float, threshold: float) -> bool:
    """¿Media del país ≥ umbral?"""
    return mean_temp >= threshold

# --- Programa principal ---

def main():
    records, df = load_dataset(CSV)

    # Construir AVL por media
    tree = AVLTree()
    for rec in records:
        tree.insert(rec.mean_temp, rec.iso3, rec)

    # Recorrido por niveles (solo ISO3)
    print("Niveles (primeras 3 capas):", tree.bfs_levels()[:3], "...")

    # Nodo de ejemplo y datos
    k = records[0].mean_temp
    node = tree.search(k)
    if node:
        print("Nodo:", node.iso3, "nivel:", node.level(), "BF:", node.balance_factor())
        if node.parent: print("Padre:", node.parent.iso3)
        if node.grandparent(): print("Abuelo:", node.grandparent().iso3)
        if node.uncle(): print("Tío:", node.uncle().iso3)

    # Consultas a), b), c)
    iso = records[10].iso3
    year = 2005
    print(f"a) {iso} {year} >", a(df, year, iso))
    print(f"b) {iso} {year} <", b(df, year, iso))
    print("c) media ≥ umbral:", c(records[10].mean_temp, 0.5))

    # Probar eliminar / reinsertar
    tmp = records[1]
    tree.delete(tmp.mean_temp)
    tree.insert(tmp.mean_temp, tmp.iso3, tmp)
    print("OK delete/insert")

if __name__ == "__main__":
    main()