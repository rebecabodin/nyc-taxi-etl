from pathlib import Path
import re

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

    Usamos amostra porque os arquivos originais são grandes.
    """
    return pd.read_csv(file_path, nrows=nrows)


def get_expected_period(file_path: Path) -> pd.Period | None:
    """
    Extrai o ano e mês esperados a partir do nome do arquivo.

    Exemplo:
    yellow_tripdata_2016-03.csv -> 2016-03
    """
    match = re.search(r"(\d{4})-(\d{2})", file_path.name)

    if not match:
        return None

    year = match.group(1)
    month = match.group(2)

    return pd.Period(f"{year}-{month}", freq="M")


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


def create_speed_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria a coluna de velocidade média em milhas por hora.
    """
    df = df.copy()

    trip_duration_hours = df["trip_duration_minutes"] / 60

    df["avg_speed_mph"] = df["trip_distance"] / trip_duration_hours

    return df


def validate_data(
    df: pd.DataFrame,
    file_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int], float]:
    """
    Aplica regras de qualidade e separa registros válidos e inválidos.
    """
    df = df.copy()

    expected_period = get_expected_period(file_path)

    duplicate_columns = [
        "VendorID",
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "trip_distance",
        "fare_amount",
        "total_amount",
    ]

    null_mask = df.isna().any(axis=1)

    duplicate_mask = df.duplicated(
        subset=duplicate_columns,
        keep=False,
    )

    expected_total_amount = (
        df["fare_amount"]
        + df["extra"]
        + df["mta_tax"]
        + df["tip_amount"]
        + df["tolls_amount"]
        + df["improvement_surcharge"]
    )

    financial_difference = (df["total_amount"] - expected_total_amount).abs()

    invalid_financial_consistency = financial_difference > 0.05

    invalid_distance = (
        (df["trip_distance"] <= 0)
        | (df["trip_distance"] > 100)
    )

    invalid_passenger_count = (
        (df["passenger_count"] <= 0)
        | (df["passenger_count"] > 6)
    )

    invalid_fare_amount = (
        (df["fare_amount"] <= 0)
        | (df["fare_amount"] > 500)
    )

    invalid_total_amount = (
        (df["total_amount"] <= 0)
        | (df["total_amount"] > 1000)
    )

    invalid_duration = (
        (df["trip_duration_minutes"] <= 0)
        | (df["trip_duration_minutes"] > 240)
    )

    invalid_speed = (
        (df["avg_speed_mph"] <= 0)
        | (df["avg_speed_mph"] > 120)
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

    invalid_vendor_id = ~df["VendorID"].isin([1, 2])

    invalid_payment_type = ~df["payment_type"].isin([1, 2, 3, 4, 5, 6])

    invalid_ratecode_id = ~df["RatecodeID"].isin([1, 2, 3, 4, 5, 6, 99])

    invalid_store_and_fwd_flag = ~df["store_and_fwd_flag"].astype(str).str.upper().isin(
        ["Y", "N"]
    )

    invalid_temporal_order = (
        df["tpep_dropoff_datetime"] < df["tpep_pickup_datetime"]
    )

    if expected_period is not None:
        invalid_outside_file_month = (
            (df["tpep_pickup_datetime"].dt.to_period("M") != expected_period)
            | (df["tpep_dropoff_datetime"].dt.to_period("M") != expected_period)
        )
    else:
        invalid_outside_file_month = pd.Series(False, index=df.index)

    validation_rules = {
        "valores_nulos": null_mask,
        "duplicados": duplicate_mask,
        "inconsistencia_financeira": invalid_financial_consistency,
        "distancia_invalida": invalid_distance,
        "passageiros_invalidos": invalid_passenger_count,
        "tarifa_invalida": invalid_fare_amount,
        "valor_total_invalido": invalid_total_amount,
        "duracao_invalida": invalid_duration,
        "velocidade_invalida": invalid_speed,
        "coordenada_pickup_invalida": invalid_pickup_coordinates,
        "coordenada_dropoff_invalida": invalid_dropoff_coordinates,
        "vendor_id_invalido": invalid_vendor_id,
        "payment_type_invalido": invalid_payment_type,
        "ratecode_id_invalido": invalid_ratecode_id,
        "store_and_fwd_flag_invalido": invalid_store_and_fwd_flag,
        "ordem_temporal_invalida": invalid_temporal_order,
        "data_fora_do_mes_do_arquivo": invalid_outside_file_month,
    }

    invalid_mask = pd.Series(False, index=df.index)

    for rule_mask in validation_rules.values():
        invalid_mask = invalid_mask | rule_mask

    valid_df = df[~invalid_mask].copy()
    invalid_df = df[invalid_mask].copy()

    quality_report = {
        rule_name: int(rule_mask.sum())
        for rule_name, rule_mask in validation_rules.items()
    }

    quality_score = round((len(valid_df) / len(df)) * 100, 2)

    return valid_df, invalid_df, quality_report, quality_score


def main() -> None:
    csv_files = list_csv_files()

    if not csv_files:
        print("Nenhum arquivo CSV encontrado em data/raw/")
        return

    for file in csv_files:
        print(f"\nValidando arquivo: {file.name}")
        print("-" * 80)

        df = read_csv_sample(file, nrows=10000)

        print(f"Linhas antes da validação: {len(df)}")
        print(f"Colunas antes da validação: {len(df.columns)}")

        df = convert_datetime_columns(df)
        df = create_duration_column(df)
        df = create_speed_column(df)

        valid_df, invalid_df, quality_report, quality_score = validate_data(
            df=df,
            file_path=file,
        )

        print("\nResumo das regras de Data Quality:")
        for rule_name, total_errors in quality_report.items():
            print(f"{rule_name}: {total_errors}")

        print("\nResultado final da validação:")
        print(f"Registros válidos: {len(valid_df)}")
        print(f"Registros inválidos: {len(invalid_df)}")
        print(f"Score de qualidade: {quality_score}/100")

        print("\nExemplo de registros válidos:")
        print(valid_df.head())

        print("-" * 80)


if __name__ == "__main__":
    main()
