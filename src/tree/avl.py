from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Any, Callable

@dataclass
class AVLNode:
    key: float
    iso3: str
    payload: Any
    left: Optional["AVLNode"] = None
    right: Optional["AVLNode"] = None
    height: int = 1
    parent: Optional["AVLNode"] = field(default=None, repr=False)

    def level(self) -> int:
        lvl, p = 0, self.parent
        while p:
            lvl += 1
            p = p.parent
        return lvl

    def balance_factor(self) -> int:
        lh = self.left.height if self.left else 0
        rh = self.right.height if self.right else 0
        return lh - rh

    def grandparent(self) -> Optional["AVLNode"]:
        return self.parent.parent if self.parent else None

    def uncle(self) -> Optional["AVLNode"]:
        g = self.grandparent()
        if not g:
            return None
        return g.right if g.left is self.parent else g.left

def _h(n: Optional[AVLNode]) -> int: return n.height if n else 0
def _upd(n: AVLNode) -> None: n.height = max(_h(n.left), _h(n.right)) + 1

def _rotate_right(y: AVLNode) -> AVLNode:
    x = y.left; T2 = x.right if x else None
    x.right = y; y.left = T2
    if T2: T2.parent = y
    x.parent, y.parent = y.parent, x
    _upd(y); _upd(x)
    return x

def _rotate_left(x: AVLNode) -> AVLNode:
    y = x.right; T2 = y.left if y else None
    y.left = x; x.right = T2
    if T2: T2.parent = x
    y.parent, x.parent = x.parent, y
    _upd(x); _upd(y)
    return y

def _rebalance(n: AVLNode) -> AVLNode:
    _upd(n)
    bf = n.balance_factor()
    if bf > 1:
        if n.left and n.left.balance_factor() < 0:
            n.left = _rotate_left(n.left); n.left.parent = n
        return _rotate_right(n)
    if bf < -1:
        if n.right and n.right.balance_factor() > 0:
            n.right = _rotate_right(n.right); n.right.parent = n
        return _rotate_left(n)
    return n

class AVLTree:
    def __init__(self, cmp: Callable[[float, float], int] | None = None):
        self.root: Optional[AVLNode] = None
        self.cmp = cmp or (lambda a, b: (a > b) - (a < b))

    def _insert(self, node: Optional[AVLNode], key: float, iso3: str, payload: Any, parent=None) -> AVLNode:
        if node is None:
            return AVLNode(key, iso3, payload, parent=parent)
        if self.cmp(key, node.key) < 0:
            node.left = self._insert(node.left, key, iso3, payload, node)
        else:
            node.right = self._insert(node.right, key, iso3, payload, node)
        return _rebalance(node)

    def insert(self, key: float, iso3: str, payload: Any) -> None:
        self.root = self._insert(self.root, key, iso3, payload)

    def search(self, key: float) -> Optional[AVLNode]:
        cur = self.root
        while cur:
            c = self.cmp(key, cur.key)
            if c == 0:
                return cur
            cur = cur.left if c < 0 else cur.right
        return None

    def _min(self, n: AVLNode) -> AVLNode:
        while n.left: n = n.left
        return n

    def _delete(self, node: Optional[AVLNode], key: float) -> Optional[AVLNode]:
        if node is None:
            return None
        c = self.cmp(key, node.key)
        if c < 0:
            node.left = self._delete(node.left, key)
            if node.left: node.left.parent = node
        elif c > 0:
            node.right = self._delete(node.right, key)
            if node.right: node.right.parent = node
        else:
            if not node.left or not node.right:
                child = node.left or node.right
                if child: child.parent = node.parent
                return child
            s = self._min(node.right)
            node.key, node.iso3, node.payload = s.key, s.iso3, s.payload
            node.right = self._delete(node.right, s.key)
            if node.right: node.right.parent = node
        return _rebalance(node)

    def delete(self, key: float) -> None:
        if self.root:
            self.root = self._delete(self.root, key)
            if self.root: self.root.parent = None

    def bfs_levels(self) -> list[list[str]]:
        if not self.root: return []
        q = [self.root]; out: list[list[str]] = []
        while q:
            out.append([n.iso3 for n in q])
            q = [c for n in q for c in (n.left, n.right) if c]
        return out