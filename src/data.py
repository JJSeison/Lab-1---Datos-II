from __future__ import annotations
import pandas as pd
from dataclasses import dataclass

YEARS = list(range(1961, 2023))  # F1961..F2022

@dataclass
class CountryRec:
    object_id: int
    country: str
    iso3: str
    mean_temp: float
    yearly: dict  # {1961: val, ..., 2022: val}

def load_dataset(path: str):
    df = pd.read_csv(path)
    year_cols = [f"F{y}" for y in YEARS]
    if not set(year_cols).issubset(df.columns):
        raise ValueError("Faltan columnas F1961..F2022 en el CSV")

    # --- LIMPIEZA: forzar ObjectId a numérico y descartar filas inválidas ---
    df["ObjectId"] = pd.to_numeric(df["ObjectId"], errors="coerce")
    df = df.dropna(subset=["ObjectId"]).copy()
    df["ObjectId"] = df["ObjectId"].astype(int)
    # ------------------------------------------------------------------------

    # media por país
    df["mean_temp"] = df[year_cols].mean(axis=1, skipna=True)

    records: list[CountryRec] = []
    for _, r in df.iterrows():
        yearly = {y: r.get(f"F{y}") for y in YEARS}
        records.append(CountryRec(
            object_id=int(r["ObjectId"]),
            country=str(r["Country"]),
            iso3=str(r["ISO3"]),
            mean_temp=float(r["mean_temp"]),
            yearly=yearly
        ))
    return records, df