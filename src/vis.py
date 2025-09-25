from __future__ import annotations
from graphviz import Digraph
from typing import Optional
from src.tree.avl import AVLTree, AVLNode
import math, os

def _fmt_mean(x) -> str:
    try:
        x = float(x)
        if math.isnan(x):
            return "NA"
        return f"{x:.3f} °C"
    except (TypeError, ValueError):
        return "NA"

def export_tree_png(
    tree: AVLTree,
    path_png: str = "out/tree.png",
    *,
    key_name: str = "key",
    key_unit: str = "°C"
):
    dot = Digraph("AVL", format="png")
    dot.attr("node", shape="circle", fontname="Consolas", fontsize="10")

    def add(n: Optional[AVLNode]):
        if not n:
            return
        iso  = getattr(n.payload, "iso3", "?")
        name = getattr(n.payload, "country", iso)
        mean = _fmt_mean(getattr(n.payload, "mean_temp", None))
        key_val = n.key

        # Etiqueta: Nombre, ISO3, promedio, KEY y BF
        label = (
            f"{name}\n"
            f"({iso})\n"
            f"Promedio: {mean}\n"
            f"Key[{key_name}]: {key_val:.3f} {key_unit}\n"
            f"BF={n.balance_factor()}"
        )

        nid = str(id(n))
        dot.node(nid, label)
        if n.left:
            add(n.left)
            dot.edge(nid, str(id(n.left)))
        if n.right:
            add(n.right)
            dot.edge(nid, str(id(n.right)))

    if tree.root:
        add(tree.root)

    os.makedirs(os.path.dirname(path_png), exist_ok=True)
    dot.render(path_png, cleanup=True)