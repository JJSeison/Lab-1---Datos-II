import pandas as pd

from src.data import load_dataset

CSV = "data/dataset_climate_change.csv"

def main():
    records, df = load_dataset(CSV)
    print(f"Registros: {len(records)}  DataFrame: {df.shape}")
    print("Ejemplo:", records[0].iso3, f"mean={records[0].mean_temp:.3f}")

if __name__ == "__main__":
    main()