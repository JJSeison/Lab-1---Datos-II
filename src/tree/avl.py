from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any, List, Tuple

@dataclass
class AVLNode:
    key: Any
    payload: Any          # por ejemplo CountryRec
    left: Optional["AVLNode"] = None
    right: Optional["AVLNode"] = None
    parent: Optional["AVLNode"] = None
    height: int = 1

    def balance_factor(self) -> int:
        return (self.left.height if self.left else 0) - (self.right.height if self.right else 0)

    # utilidades de parentesco (para opción 6 del menú)
    def grandparent(self) -> Optional["AVLNode"]:
        return self.parent.parent if self.parent else None

    def uncle(self) -> Optional["AVLNode"]:
        g = self.grandparent()
        if not g:
            return None
        return g.right if self.parent is g.left else g.left


class AVLTree:
    def __init__(self):
        self.root: Optional[AVLNode] = None
        self._size = 0

    # ---------- helpers internos ----------
    def _h(self, n: Optional[AVLNode]) -> int:
        return n.height if n else 0

    def _upd(self, n: AVLNode) -> None:
        n.height = 1 + max(self._h(n.left), self._h(n.right))

    def _rot_right(self, y: AVLNode) -> AVLNode:
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        if T2:
            T2.parent = y
        x.parent = y.parent
        y.parent = x
        self._upd(y)
        self._upd(x)
        return x

    def _rot_left(self, x: AVLNode) -> AVLNode:
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        if T2:
            T2.parent = x
        y.parent = x.parent
        x.parent = y
        self._upd(x)
        self._upd(y)
        return y

    def _rebalance(self, node: AVLNode) -> AVLNode:
        self._upd(node)
        bf = node.balance_factor()
        if bf > 1:
            if node.left and node.left.balance_factor() < 0:
                node.left = self._rot_left(node.left)
                node.left.parent = node
            return self._rot_right(node)
        if bf < -1:
            if node.right and node.right.balance_factor() > 0:
                node.right = self._rot_right(node.right)
                node.right.parent = node
            return self._rot_left(node)
        return node

    # ---------- API ----------
    def insert(self, key: Any, payload: Any) -> None:
        """Inserta por key; si (key, iso3) ya existe, actualiza payload; desempata por ISO3."""
        def _ins(cur: Optional[AVLNode], key, payload, parent=None) -> AVLNode:
            if not cur:
                self._size += 1
                return AVLNode(key, payload, parent=parent)

            kcur = (cur.key, getattr(cur.payload, "iso3", ""))
            knew = (key,       getattr(payload, "iso3", ""))

            if knew == kcur:
                # mismo nodo: actualiza la info y listo
                cur.payload = payload
                return cur
            elif knew < kcur:
                cur.left = _ins(cur.left, key, payload, cur)
            else:
                cur.right = _ins(cur.right, key, payload, cur)

            cur = self._rebalance(cur)
            return cur

        self.root = _ins(self.root, key, payload, None)

    def search_key(self, key: Any) -> Optional[AVLNode]:
        """Busca por key (SOLO la clave numérica)."""
        cur = self.root
        while cur:
            if key == cur.key:
                return cur
            cur = cur.left if key < cur.key else cur.right
        return None

    def _min_node(self, n: AVLNode) -> AVLNode:
        while n.left:
            n = n.left
        return n

    def delete(self, key: Any) -> None:
        """Elimina por key (SOLO la clave numérica)."""
        def _del(cur: Optional[AVLNode], key) -> Optional[AVLNode]:
            if not cur:
                return None

            if key < cur.key:
                cur.left = _del(cur.left, key)
                if cur.left:
                    cur.left.parent = cur
            elif key > cur.key:
                cur.right = _del(cur.right, key)
                if cur.right:
                    cur.right.parent = cur
            else:
                # encontrado
                self._size -= 1
                if not cur.left or not cur.right:
                    child = cur.left or cur.right
                    if child:
                        child.parent = cur.parent
                    return child
                succ = self._min_node(cur.right)
                cur.key, cur.payload = succ.key, succ.payload
                cur.right = _del(cur.right, succ.key)
                if cur.right:
                    cur.right.parent = cur

            self._upd(cur)
            bf = cur.balance_factor()
            if bf > 1:
                if cur.left and cur.left.balance_factor() < 0:
                    cur.left = self._rot_left(cur.left); cur.left.parent = cur
                return self._rot_right(cur)
            if bf < -1:
                if cur.right and cur.right.balance_factor() > 0:
                    cur.right = self._rot_right(cur.right); cur.right.parent = cur
                return self._rot_left(cur)
            return cur

        self.root = _del(self.root, key)
        if self.root:
            self.root.parent = None

    def size(self) -> int:
        return self._size

    # recorrido por niveles (ISO3)
    def levels_iso3(self) -> List[List[str]]:
        res: List[List[str]] = []
        if not self.root:
            return res
        q: List[Tuple[AVLNode, int]] = [(self.root, 0)]
        while q:
            n, lvl = q.pop(0)
            if len(res) <= lvl:
                res.append([])
            res[lvl].append(getattr(n.payload, "iso3", str(n.key)))
            if n.left:  q.append((n.left,  lvl+1))
            if n.right: q.append((n.right, lvl+1))
        return res

    def level_of(self, node: AVLNode) -> int:
        lvl = 0
        while node.parent:
            lvl += 1
            node = node.parent
        return lvl