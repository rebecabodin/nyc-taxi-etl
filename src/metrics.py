from pathlib import Path

import pandas as pd

from transform import transform_data


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "output"


def list_csv_files() -> list[Path]:
    """
    Lista os arquivos CSV disponíveis na camada raw.
    """
    return sorted(RAW_DIR.glob("*.csv"))


def read_and_transform_files(nrows_per_file: int = 10000) -> pd.DataFrame:
    """
    Lê uma amostra dos CSVs, aplica as transformações e une tudo em um único DataFrame.
    """
    csv_files = list_csv_files()

    if not csv_files:
        raise FileNotFoundError("Nenhum arquivo CSV encontrado em data/raw/")

    dataframes = []

    for file in csv_files:
        print(f"Lendo e transformando: {file.name}")

        df = pd.read_csv(file, nrows=nrows_per_file)
        df = transform_data(df)
        df["source_file"] = file.name

        dataframes.append(df)

    final_df = pd.concat(dataframes, ignore_index=True)

    return final_df


def prepare_metric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria colunas auxiliares para cálculo das métricas.
    """
    df = df.copy()

    df["tip_percentage"] = (
        df["tip_amount"] / df["total_amount"].replace(0, pd.NA)
    ) * 100

    df["tip_percentage"] = (
        df["tip_percentage"]
        .replace([float("inf"), -float("inf")], pd.NA)
        .fillna(0)
        .round(2)
    )

    df["pickup_week"] = pd.to_datetime(df["pickup_date"]).dt.to_period("W").astype(str)

    df["pickup_location"] = (
        df["pickup_latitude"].round(2).astype(str)
        + ","
        + df["pickup_longitude"].round(2).astype(str)
    )

    df["dropoff_location"] = (
        df["dropoff_latitude"].round(2).astype(str)
        + ","
        + df["dropoff_longitude"].round(2).astype(str)
    )

    df["route"] = df["pickup_location"] + " -> " + df["dropoff_location"]

    return df


def create_general_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria métricas gerais do dataset.
    """
    total_trips = len(df)

    metrics = {
        "total_trips": total_trips,
        "total_revenue": round(df["total_amount"].sum(), 2),
        "avg_distance": round(df["trip_distance"].mean(), 2),
        "avg_fare": round(df["fare_amount"].mean(), 2),
        "avg_duration": round(df["trip_duration_minutes"].mean(), 2),
        "avg_speed": round(df["avg_speed_mph"].mean(), 2),
        "avg_tip_pct": round(df["tip_percentage"].mean(), 2),
        "pct_trips": 100.00,
    }

    return pd.DataFrame([metrics])


def aggregate_by_day(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega métricas por dia.
    """
    result = (
        df.groupby("pickup_date")
        .agg(
            total_trips=("pickup_date", "count"),
            total_revenue=("total_amount", "sum"),
            avg_ticket=("total_amount", "mean"),
            avg_tip=("tip_amount", "mean"),
            avg_distance=("trip_distance", "mean"),
            avg_duration=("trip_duration_minutes", "mean"),
        )
        .reset_index()
    )

    return result.round(2)


def aggregate_by_week(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega métricas por semana.
    """
    result = (
        df.groupby("pickup_week")
        .agg(
            total_trips=("pickup_week", "count"),
            total_revenue=("total_amount", "sum"),
            avg_ticket=("total_amount", "mean"),
            avg_distance=("trip_distance", "mean"),
            avg_duration=("trip_duration_minutes", "mean"),
        )
        .reset_index()
    )

    return result.round(2)


def aggregate_by_day_period_and_payment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega métricas por turno do dia e forma de pagamento.
    """
    total_trips = len(df)

    result = (
        df.groupby(["day_period", "payment_type"])
        .agg(
            total_trips=("payment_type", "count"),
            total_revenue=("total_amount", "sum"),
            avg_ticket=("total_amount", "mean"),
            avg_tip_pct=("tip_percentage", "mean"),
        )
        .reset_index()
    )

    result["pct_trips"] = (result["total_trips"] / total_trips) * 100

    return result.round(2)


def aggregate_by_vendor_and_period(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega métricas por fornecedor/vendor e turno do dia.
    """
    result = (
        df.groupby(["vendor_id", "day_period"])
        .agg(
            total_trips=("vendor_id", "count"),
            total_revenue=("total_amount", "sum"),
            avg_distance=("trip_distance", "mean"),
            avg_duration=("trip_duration_minutes", "mean"),
            avg_speed=("avg_speed_mph", "mean"),
        )
        .reset_index()
    )

    return result.round(2)


def aggregate_top_routes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Lista rotas aproximadas com mais volume e receita.

    Como não temos bairros/zonas neste momento, usamos coordenadas arredondadas.
    """
    result = (
        df.groupby("route")
        .agg(
            total_trips=("route", "count"),
            total_revenue=("total_amount", "sum"),
            avg_ticket=("total_amount", "mean"),
            avg_distance=("trip_distance", "mean"),
        )
        .reset_index()
        .sort_values(["total_trips", "total_revenue"], ascending=False)
        .head(20)
    )

    return result.round(2)


def calculate_percentiles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula percentis P50, P90 e P95 para duração, distância e tarifa.
    """
    metrics = []

    columns = {
        "trip_duration_minutes": "duration",
        "trip_distance": "distance",
        "fare_amount": "fare",
    }

    for column, metric_name in columns.items():
        metrics.append(
            {
                "metric": metric_name,
                "p50": round(df[column].quantile(0.50), 2),
                "p90": round(df[column].quantile(0.90), 2),
                "p95": round(df[column].quantile(0.95), 2),
            }
        )

    return pd.DataFrame(metrics)


def measure_quality_by_rule(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mede qualidade por algumas regras usadas após as transformações.
    """
    total_rows = len(df)

    rules = {
        "distancia_zero_ou_negativa": df["trip_distance"] <= 0,
        "duracao_zero_ou_negativa": df["trip_duration_minutes"] <= 0,
        "valor_total_zero_ou_negativo": df["total_amount"] <= 0,
        "velocidade_muito_alta": df["avg_speed_mph"] > 80,
        "corrida_suspeita": df["is_suspicious_trip"] == True,
    }

    results = []

    for rule_name, rule_mask in rules.items():
        failures = int(rule_mask.sum())
        failure_pct = round((failures / total_rows) * 100, 2)

        results.append(
            {
                "rule": rule_name,
                "failures": failures,
                "failure_pct": failure_pct,
            }
        )

    return pd.DataFrame(results)


def save_outputs(outputs: dict[str, pd.DataFrame]) -> None:
    """
    Salva os resultados em arquivos CSV dentro da pasta data/output.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for name, dataframe in outputs.items():
        output_path = OUTPUT_DIR / f"{name}.csv"
        dataframe.to_csv(output_path, index=False)
        print(f"Arquivo salvo: {output_path}")


def main() -> None:
    print("Iniciando criação de métricas e agregações...")
    print("-" * 80)

    df = read_and_transform_files(nrows_per_file=10000)
    df = prepare_metric_columns(df)

    print(f"Total de linhas analisadas: {len(df)}")
    print(f"Total de colunas disponíveis: {len(df.columns)}")

    outputs = {
        "general_metrics": create_general_metrics(df),
        "metrics_by_day": aggregate_by_day(df),
        "metrics_by_week": aggregate_by_week(df),
        "metrics_by_day_period_payment": aggregate_by_day_period_and_payment(df),
        "metrics_by_vendor_period": aggregate_by_vendor_and_period(df),
        "top_routes": aggregate_top_routes(df),
        "percentiles": calculate_percentiles(df),
        "quality_by_rule": measure_quality_by_rule(df),
    }

    print("\nMétricas gerais:")
    print(outputs["general_metrics"])

    print("\nMétricas por dia:")
    print(outputs["metrics_by_day"].head())

    print("\nMétricas por turno e pagamento:")
    print(outputs["metrics_by_day_period_payment"].head())

    print("\nPercentis:")
    print(outputs["percentiles"])

    print("\nQualidade por regra:")
    print(outputs["quality_by_rule"])

    print("\nSalvando arquivos em data/output...")
    save_outputs(outputs)

    print("-" * 80)
    print("Agregações e métricas criadas com sucesso!")


if __name__ == "__main__":
    main()
