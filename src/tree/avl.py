from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple, Any, Iterable, Callable

@dataclass
class AVLNode:
    key: Any
    payload: Any          # CountryRec u otro
    left: Optional["AVLNode"] = None
    right: Optional["AVLNode"] = None
    parent: Optional["AVLNode"] = None
    height: int = 1

    # extras que pide el lab
    def balance_factor(self) -> int:
        return (self.left.height if self.left else 0) - (self.right.height if self.right else 0)

    # utilidades de “familia”
    def parent_of(self) -> Optional["AVLNode"]:
        return self.parent
    def grandparent(self) -> Optional["AVLNode"]:
        return self.parent.parent if self.parent else None
    def uncle(self) -> Optional["AVLNode"]:
        g = self.grandparent()
        if not g: return None
        return g.right if self.parent is g.left else g.left


class AVLTree:
    def __init__(self):
        self.root: Optional[AVLNode] = None
        self._size = 0

    # ------------- utilidades internas -------------
    def _h(self, n: Optional[AVLNode]) -> int: return n.height if n else 0
    def _upd(self, n: AVLNode):
        n.height = 1 + max(self._h(n.left), self._h(n.right))
    def _rot_right(self, y: AVLNode) -> AVLNode:
        x = y.left; T2 = x.right
        x.right = y; y.left = T2
        if T2: T2.parent = y
        x.parent = y.parent; y.parent = x
        self._upd(y); self._upd(x)
        return x
    def _rot_left(self, x: AVLNode) -> AVLNode:
        y = x.right; T2 = y.left
        y.left = x; x.right = T2
        if T2: T2.parent = x
        y.parent = x.parent; x.parent = y
        self._upd(x); self._upd(y)
        return y

    def _rebalance(self, node: AVLNode) -> AVLNode:
        self._upd(node)
        bf = node.balance_factor()
        # left heavy
        if bf > 1:
            if node.left and node.left.balance_factor() < 0:
                node.left = self._rot_left(node.left); node.left.parent = node
            return self._rot_right(node)
        # right heavy
        if bf < -1:
            if node.right and node.right.balance_factor() > 0:
                node.right = self._rot_right(node.right); node.right.parent = node
            return self._rot_left(node)
        return node

    # ------------- API pública -------------
    def insert(self, key: Any, payload: Any):
        """Inserta por key; si hay colisión, desempata con ISO3 del payload"""
        def _ins(cur: Optional[AVLNode], key, payload, parent=None) -> AVLNode:
            if not cur:
                self._size += 1
                n = AVLNode(key, payload, parent=parent)
                return n
            # desempate: (key, iso3)
            kcur = (cur.key, getattr(cur.payload, "iso3", ""))
            knew = (key,  getattr(payload, "iso3", ""))
            if knew < kcur:
                cur.left = _ins(cur.left, key, payload, cur)
            else:
                cur.right = _ins(cur.right, key, payload, cur)
            cur = self._rebalance(cur)
            return cur
        self.root = _ins(self.root, key, payload, None)

    def search_key(self, key: Any) -> Optional[AVLNode]:
        cur = self.root
        while cur:
            kcur = (cur.key, getattr(cur.payload, "iso3", ""))
            knew = (key,  "")
            if knew == kcur: return cur
            if knew < kcur: cur = cur.left
            else:           cur = cur.right
        return None

    def _min_node(self, n: AVLNode) -> AVLNode:
        while n.left: n = n.left
        return n

    def delete(self, key: Any):
        def _del(cur: Optional[AVLNode], key) -> Optional[AVLNode]:
            if not cur: return None
            if (key, "") < (cur.key, getattr(cur.payload, "iso3", "")):
                cur.left = _del(cur.left, key)
                if cur.left: cur.left.parent = cur
            elif (key, "") > (cur.key, getattr(cur.payload, "iso3", "")):
                cur.right = _del(cur.right, key)
                if cur.right: cur.right.parent = cur
            else:
                # encontrado
                if not cur.left or not cur.right:
                    self._size -= 1
                    child = cur.left or cur.right
                    if child: child.parent = cur.parent
                    return child
                # dos hijos
                succ = self._min_node(cur.right)
                cur.key, cur.payload = succ.key, succ.payload
                cur.right = _del(cur.right, succ.key)
                if cur.right: cur.right.parent = cur
            if not cur: return None
            cur = self._rebalance(cur)
            return cur
        self.root = _del(self.root, key)

    def size(self) -> int: return self._size

    # ----- recorrido por niveles (ISO3) -----
    def levels_iso3(self, max_layers: int | None = None) -> List[List[str]]:
        res: List[List[str]] = []
        if not self.root: return res
        q: List[Tuple[AVLNode,int]] = [(self.root,0)]
        while q:
            n, lvl = q.pop(0)
            if len(res) <= lvl: res.append([])
            iso = getattr(n.payload, "iso3", str(n.key))
            res[lvl].append(iso)
            if n.left:  q.append((n.left,  lvl+1))
            if n.right: q.append((n.right, lvl+1))
            if max_layers is not None and lvl+1 >= max_layers and not q: break
        return res

    # ----- info estructural del nodo -----
    def level_of(self, node: AVLNode) -> int:
        lvl = 0; cur = node
        while cur.parent: lvl += 1; cur = cur.parent
        return lvl