from typing import Iterable, Optional, List, Dict

def hr(char: str = "—", n: int = 60) -> None:
    print(char * n)

def titulo(texto: str) -> None:
    print("\n" + "=" * len(texto))
    print(texto)
    print("=" * len(texto))

def kv(label: str, value) -> None:
    print(f"• {label}: {value}")

def bullets(items: Iterable[str], title: Optional[str] = None, max_items: Optional[int] = None) -> None:
    if title:
        print(title)
    count = 0
    for it in items:
        if max_items is not None and count >= max_items:
            print(f"  … y {max_items}+")
            break
        print(f"  - {it}")
        count += 1

def yesno(flag: bool) -> str:
    return "Sí ✓" if flag else "No ✗"

def panel(texto: str, title: Optional[str] = None) -> None:
    if title:
        print(f"\n[{title}]")
    print(texto)