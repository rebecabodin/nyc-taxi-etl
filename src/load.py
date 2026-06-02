from pathlib import Path

import pandas as pd

from transform import transform_data


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

NROWS_PER_FILE = 10000


def list_csv_files() -> list[Path]:
    """
    Lista os arquivos CSV disponíveis na pasta data/raw.
    """
    return sorted(RAW_DIR.glob("*.csv"))


def read_csv_sample(file_path: Path, nrows: int = NROWS_PER_FILE) -> pd.DataFrame:
    """
    Lê uma amostra do CSV.

    Usamos amostra porque os arquivos originais são grandes.
    """
    return pd.read_csv(file_path, nrows=nrows)


def remove_original_timestamp_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove as colunas originais de timestamp textual no dataset final.

    Mantemos as colunas já padronizadas:
    - pickup_datetime
    - dropoff_datetime

    Removemos, caso existam:
    - tpep_pickup_datetime
    - tpep_dropoff_datetime
    """
    df = df.copy()

    columns_to_drop = [
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
    ]

    existing_columns_to_drop = [
        column for column in columns_to_drop if column in df.columns
    ]

    df = df.drop(columns=existing_columns_to_drop)

    return df


def build_parquet_output_path(file_path: Path) -> Path:
    """
    Cria o caminho final do arquivo Parquet.

    Exemplo:
    yellow_tripdata_2016-01.csv
    vira:
    yellow_tripdata_2016-01.parquet
    """
    output_file_name = f"{file_path.stem}.parquet"
    return PROCESSED_DIR / output_file_name


def save_to_parquet(df: pd.DataFrame, output_path: Path) -> None:
    """
    Salva o DataFrame em formato Parquet usando pyarrow.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df.to_parquet(
        output_path,
        index=False,
        engine="pyarrow",
        compression="snappy",
    )


def load_csv_to_parquet(file_path: Path) -> Path:
    """
    Executa o fluxo de carga:
    CSV bruto -> Transformações -> Remoção de colunas antigas -> Parquet
    """
    print(f"\nProcessando arquivo: {file_path.name}")
    print("-" * 80)

    df = read_csv_sample(file_path)

    print(f"Linhas lidas do CSV: {len(df)}")
    print(f"Colunas lidas do CSV: {len(df.columns)}")

    transformed_df = transform_data(df)
    final_df = remove_original_timestamp_columns(transformed_df)

    print(f"Linhas no dataset final: {len(final_df)}")
    print(f"Colunas no dataset final: {len(final_df.columns)}")

    output_path = build_parquet_output_path(file_path)

    save_to_parquet(final_df, output_path)

    print(f"Arquivo Parquet salvo em: {output_path}")

    return output_path


def validate_parquet_file(parquet_path: Path) -> None:
    """
    Lê o arquivo Parquet salvo para confirmar que ele foi criado corretamente.
    """
    df = pd.read_parquet(parquet_path, engine="pyarrow")

    print("\nValidação do arquivo Parquet:")
    print(f"Arquivo: {parquet_path.name}")
    print(f"Linhas: {len(df)}")
    print(f"Colunas: {len(df.columns)}")

    print("\nPrimeiras linhas:")
    print(df.head())


def main() -> None:
    csv_files = list_csv_files()

    if not csv_files:
        print("Nenhum arquivo CSV encontrado em data/raw/")
        return

    print("Iniciando persistência em Parquet...")
    print(f"Quantidade de arquivos CSV encontrados: {len(csv_files)}")
    print(f"Linhas lidas por arquivo nesta carga de teste: {NROWS_PER_FILE}")

    parquet_files = []

    for file in csv_files:
        parquet_path = load_csv_to_parquet(file)
        parquet_files.append(parquet_path)

    print("\nArquivos Parquet gerados:")
    print("-" * 80)

    for parquet_file in parquet_files:
        print(parquet_file)

    print("\nValidando o primeiro arquivo Parquet gerado...")
    validate_parquet_file(parquet_files[0])

    print("-" * 80)
    print("Persistência em Parquet concluída com sucesso!")


if __name__ == "__main__":
    main()
