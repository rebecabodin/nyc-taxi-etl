from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"


def list_csv_files() -> list[Path]:
    """
    Lista todos os arquivos CSV disponíveis na pasta data/raw.
    """
    return sorted(RAW_DIR.glob("*.csv"))


def read_csv_sample(file_path: Path, nrows: int = 10000) -> pd.DataFrame:
    """
    Lê uma amostra do CSV.
    """
    return pd.read_csv(file_path, nrows=nrows)


def convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte as colunas de data/hora para datetime.
    """
    df = df.copy()

    df["tpep_pickup_datetime"] = pd.to_datetime(
        df["tpep_pickup_datetime"],
        errors="coerce",
    )

    df["tpep_dropoff_datetime"] = pd.to_datetime(
        df["tpep_dropoff_datetime"],
        errors="coerce",
    )

    return df


def create_duration_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria a coluna de duração da corrida em minutos.
    """
    df = df.copy()

    df["trip_duration_minutes"] = (
        df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60

    return df


def validate_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Aplica regras de qualidade e separa registros válidos e inválidos.
    """
    df = df.copy()

    null_mask = df.isna().any(axis=1)

    invalid_distance = df["trip_distance"] <= 0

    invalid_passenger_count = (
        (df["passenger_count"] <= 0)
        | (df["passenger_count"] > 6)
    )

    invalid_fare_amount = df["fare_amount"] <= 0

    invalid_total_amount = df["total_amount"] <= 0

    invalid_duration = (
        (df["trip_duration_minutes"] <= 0)
        | (df["trip_duration_minutes"] > 24 * 60)
    )

    invalid_pickup_coordinates = (
        (df["pickup_latitude"] < 40.4)
        | (df["pickup_latitude"] > 41.0)
        | (df["pickup_longitude"] < -74.3)
        | (df["pickup_longitude"] > -73.6)
    )

    invalid_dropoff_coordinates = (
        (df["dropoff_latitude"] < 40.4)
        | (df["dropoff_latitude"] > 41.0)
        | (df["dropoff_longitude"] < -74.3)
        | (df["dropoff_longitude"] > -73.6)
    )

    invalid_mask = (
        null_mask
        | invalid_distance
        | invalid_passenger_count
        | invalid_fare_amount
        | invalid_total_amount
        | invalid_duration
        | invalid_pickup_coordinates
        | invalid_dropoff_coordinates
    )

    valid_df = df[~invalid_mask].copy()
    invalid_df = df[invalid_mask].copy()

    return valid_df, invalid_df


def main() -> None:
    csv_files = list_csv_files()

    if not csv_files:
        print("Nenhum arquivo CSV encontrado em data/raw/")
        return

    for file in csv_files:
        print(f"\nValidando arquivo: {file.name}")
        print("-" * 60)

        df = read_csv_sample(file, nrows=10000)

        print(f"Linhas antes da validação: {len(df)}")
        print(f"Colunas antes da validação: {len(df.columns)}")

        print("\nValores nulos por coluna:")
        print(df.isna().sum())

        df = convert_datetime_columns(df)
        df = create_duration_column(df)

        valid_df, invalid_df = validate_data(df)

        print("\nResultado da validação:")
        print(f"Registros válidos: {len(valid_df)}")
        print(f"Registros inválidos: {len(invalid_df)}")

        valid_percent = (len(valid_df) / len(df)) * 100
        invalid_percent = (len(invalid_df) / len(df)) * 100

        print(f"Percentual válido: {valid_percent:.2f}%")
        print(f"Percentual inválido: {invalid_percent:.2f}%")

        print("\nExemplo de registros válidos:")
        print(valid_df.head())

        print("-" * 60)


if __name__ == "__main__":
    main()
