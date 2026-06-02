from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"


MONEY_COLUMNS = [
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
]


def list_csv_files() -> list[Path]:
    """
    Lista todos os arquivos CSV disponíveis na pasta data/raw.
    """
    return sorted(RAW_DIR.glob("*.csv"))


def read_csv_sample(file_path: Path, nrows: int = 10000) -> pd.DataFrame:
    """
    Lê uma amostra do CSV.

    Usamos amostra porque os arquivos originais são muito grandes.
    """
    return pd.read_csv(file_path, nrows=nrows)


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Padroniza nomes de colunas para facilitar o uso no projeto.

    Mantemos temporariamente as colunas textuais originais de timestamp
    e criamos colunas padronizadas para uso analítico.
    """
    df = df.copy()

    rename_columns = {
        "VendorID": "vendor_id",
        "RatecodeID": "ratecode_id",
    }

    df = df.rename(columns=rename_columns)

    df["pickup_datetime"] = df["tpep_pickup_datetime"]
    df["dropoff_datetime"] = df["tpep_dropoff_datetime"]

    return df


def convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte colunas de data/hora para datetime.
    """
    df = df.copy()

    df["pickup_datetime"] = pd.to_datetime(
        df["pickup_datetime"],
        errors="coerce",
    )

    df["dropoff_datetime"] = pd.to_datetime(
        df["dropoff_datetime"],
        errors="coerce",
    )

    return df


def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria colunas derivadas das datas.
    """
    df = df.copy()

    df["pickup_date"] = df["pickup_datetime"].dt.date.astype(str)
    df["pickup_year"] = df["pickup_datetime"].dt.year
    df["pickup_month"] = df["pickup_datetime"].dt.month
    df["pickup_day"] = df["pickup_datetime"].dt.day
    df["pickup_hour"] = df["pickup_datetime"].dt.hour
    df["pickup_weekday"] = df["pickup_datetime"].dt.day_name()
    df["is_weekend"] = df["pickup_datetime"].dt.dayofweek.isin([5, 6])

    return df


def create_trip_duration(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria a duração da corrida em minutos.
    """
    df = df.copy()

    df["trip_duration_minutes"] = (
        df["dropoff_datetime"] - df["pickup_datetime"]
    ).dt.total_seconds() / 60

    return df


def create_day_period(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria o turno do dia com base na hora da corrida.
    """
    df = df.copy()

    conditions = [
        df["pickup_hour"].between(0, 5),
        df["pickup_hour"].between(6, 11),
        df["pickup_hour"].between(12, 17),
        df["pickup_hour"].between(18, 23),
    ]

    choices = [
        "madrugada",
        "manha",
        "tarde",
        "noite",
    ]

    df["day_period"] = np.select(
        conditions,
        choices,
        default="desconhecido",
    )

    return df


def create_distance_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria faixas de distância da corrida.
    """
    df = df.copy()

    conditions = [
        df["trip_distance"] <= 2,
        df["trip_distance"].between(2.01, 8),
        df["trip_distance"] > 8,
    ]

    choices = [
        "curta",
        "media",
        "longa",
    ]

    df["distance_category"] = np.select(
        conditions,
        choices,
        default="desconhecida",
    )

    return df


def create_duration_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria faixas de duração da corrida.
    """
    df = df.copy()

    conditions = [
        df["trip_duration_minutes"] <= 5,
        df["trip_duration_minutes"].between(5.01, 30),
        df["trip_duration_minutes"] > 30,
    ]

    choices = [
        "muito_curta",
        "normal",
        "longa",
    ]

    df["duration_category"] = np.select(
        conditions,
        choices,
        default="desconhecida",
    )

    return df


def create_financial_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria métricas financeiras evitando divisão por zero.
    """
    df = df.copy()

    duration_safe = df["trip_duration_minutes"].replace(0, np.nan)
    distance_safe = df["trip_distance"].replace(0, np.nan)

    df["revenue_per_minute"] = df["total_amount"] / duration_safe
    df["revenue_per_mile"] = df["total_amount"] / distance_safe

    df["revenue_per_minute"] = df["revenue_per_minute"].replace(
        [np.inf, -np.inf],
        np.nan,
    ).fillna(0)

    df["revenue_per_mile"] = df["revenue_per_mile"].replace(
        [np.inf, -np.inf],
        np.nan,
    ).fillna(0)

    return df


def create_holiday_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria uma flag simples de feriados para o período usado no projeto.
    """
    df = df.copy()

    holidays = {
        "2016-01-01",
        "2016-01-18",
        "2016-02-15",
    }

    df["is_holiday"] = df["pickup_date"].isin(holidays)

    return df


def create_anomaly_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria uma flag simples para marcar corridas suspeitas.
    """
    df = df.copy()

    df["avg_speed_mph"] = (
        df["trip_distance"] / (df["trip_duration_minutes"] / 60)
    )

    df["avg_speed_mph"] = df["avg_speed_mph"].replace(
        [np.inf, -np.inf],
        np.nan,
    ).fillna(0)

    df["is_suspicious_trip"] = (
        (df["avg_speed_mph"] > 80)
        | (df["trip_distance"] <= 0)
        | (df["trip_duration_minutes"] <= 0)
        | (df["total_amount"] <= 0)
        | ((df["avg_speed_mph"] > 60) & (df["fare_amount"] < 10))
    )

    return df


def standardize_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Padroniza tipos e arredonda valores monetários.
    """
    df = df.copy()

    for column in MONEY_COLUMNS:
        if column in df.columns:
            df[column] = df[column].round(2)

    df["revenue_per_minute"] = df["revenue_per_minute"].round(2)
    df["revenue_per_mile"] = df["revenue_per_mile"].round(2)
    df["avg_speed_mph"] = df["avg_speed_mph"].round(2)
    df["trip_duration_minutes"] = df["trip_duration_minutes"].round(2)

    return df



def prepare_final_dataset_for_load(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove colunas originais de timestamp textual antes da carga final.

    Mantemos apenas:
    - pickup_datetime
    - dropoff_datetime

    Removemos:
    - tpep_pickup_datetime
    - tpep_dropoff_datetime
    """
    df = df.copy()

    original_timestamp_columns = [
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
    ]

    columns_to_drop = [
        column
        for column in original_timestamp_columns
        if column in df.columns
    ]

    df = df.drop(columns=columns_to_drop)

    return df


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Executa todas as transformações do Passo 04.
    """
    df = standardize_column_names(df)
    df = convert_datetime_columns(df)
    df = create_time_features(df)
    df = create_trip_duration(df)
    df = create_day_period(df)
    df = create_distance_category(df)
    df = create_duration_category(df)
    df = create_financial_features(df)
    df = create_holiday_flag(df)
    df = create_anomaly_flag(df)
    df = standardize_data_types(df)
    df = prepare_final_dataset_for_load(df)

    return df


def main() -> None:
    csv_files = list_csv_files()

    if not csv_files:
        print("Nenhum arquivo CSV encontrado em data/raw/")
        return

    for file in csv_files:
        print(f"\nTransformando arquivo: {file.name}")
        print("-" * 80)

        df = read_csv_sample(file, nrows=10000)

        print(f"Linhas antes da transformação: {len(df)}")
        print(f"Colunas antes da transformação: {len(df.columns)}")

        transformed_df = transform_data(df)

        print(f"Linhas depois da transformação: {len(transformed_df)}")
        print(f"Colunas depois da transformação: {len(transformed_df.columns)}")

        print("\nNovas colunas criadas:")
        new_columns = [
            "pickup_date",
            "pickup_year",
            "pickup_month",
            "pickup_day",
            "pickup_hour",
            "pickup_weekday",
            "is_weekend",
            "trip_duration_minutes",
            "day_period",
            "distance_category",
            "duration_category",
            "revenue_per_minute",
            "revenue_per_mile",
            "is_holiday",
            "avg_speed_mph",
            "is_suspicious_trip",
        ]

        for column in new_columns:
            print(f"- {column}")

        print("\nAmostra dos dados transformados:")
        print(
            transformed_df[
                [
                    "vendor_id",
                    "pickup_datetime",
                    "dropoff_datetime",
                    "trip_distance",
                    "trip_duration_minutes",
                    "avg_speed_mph",
                    "total_amount",
                    "revenue_per_minute",
                    "revenue_per_mile",
                    "day_period",
                    "distance_category",
                    "duration_category",
                    "is_weekend",
                    "is_holiday",
                    "is_suspicious_trip",
                ]
            ].head()
        )

        print("-" * 80)


if __name__ == "__main__":
    main()
