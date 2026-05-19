from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"


def list_csv_files() -> list[Path]:
    """
    Lista todos os arquivos CSV disponíveis na pasta data/raw.
    """
    return sorted(RAW_DIR.glob("*.csv"))


def read_csv_sample(file_path: Path, nrows: int = 1000) -> pd.DataFrame:
    """
    Lê uma amostra do CSV e retorna um DataFrame.

    Como os arquivos são grandes, começamos com poucas linhas.
    """
    return pd.read_csv(file_path, nrows=nrows)


def main() -> None:
    csv_files = list_csv_files()

    print("Arquivos CSV encontrados:")
    print("-" * 50)

    if not csv_files:
        print("Nenhum arquivo CSV encontrado em data/raw/")
        return

    for file in csv_files:
        print(file.name)

    print("\nLeitura dos arquivos:")
    print("-" * 50)

    for file in csv_files:
        print(f"\nLendo amostra de: {file.name}")

        df = read_csv_sample(file, nrows=1000)

        print(f"Linhas e colunas: {df.shape}")

        print("\nPrimeiras linhas:")
        print(df.head())

        print("\nColunas:")
        print(df.columns.tolist())

        print("\nTipos de dados:")
        print(df.dtypes)

        print("\nValores nulos:")
        print(df.isna().sum())

        print("-" * 50)


if __name__ == "__main__":
    main()
