from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"


st.set_page_config(
    page_title="NYC Taxi Analytics",
    page_icon="🚕",
    layout="wide",
)


CUSTOM_CSS = """
<style>
    
    html, body, [class*="css"] {
        font-size: 20px;
    }
    

    .stApp {
        background: linear-gradient(180deg, #080D1A 0%, #050812 100%);
        color: #F8FAFC;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0F172A 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] * {
        font-size: 0.98rem;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 95%;
    }

    .main-title {
        font-size: 2.7rem;
        font-weight: 850;
        color: #F8FAFC;
        margin-bottom: 0.25rem;
        letter-spacing: -0.8px;
    }

    .subtitle {
        color: #CBD5E1;
        font-size: 1.12rem;
        margin-bottom: 1rem;
    }

    .sample-warning {
        background: linear-gradient(90deg, rgba(124,58,237,0.24), rgba(56,189,248,0.16));
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin-bottom: 1.2rem;
        color: #E2E8F0;
        font-size: 1rem;
        box-shadow: 0 8px 28px rgba(0,0,0,0.22);
    }

    .section-note {
        background: rgba(15, 23, 42, 0.88);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin-bottom: 1.2rem;
        color: #DDE7F3;
        font-size: 1.02rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.20);
    }

    .kpi-card {
        background: linear-gradient(180deg, rgba(30,41,59,0.98) 0%, rgba(15,23,42,0.98) 100%);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 20px;
        padding: 1.1rem 1.15rem;
        box-shadow: 0 14px 34px rgba(0,0,0,0.28);
        min-height: 120px;
        margin-bottom: 0.8rem;
    }

    .kpi-label {
        color: #AFC0D4;
        font-size: 1rem;
        margin-bottom: 0.4rem;
        font-weight: 600;
    }

    .kpi-value {
        color: #F8FAFC;
        font-size: 2rem;
        font-weight: 850;
        line-height: 1.15;
    }

    .kpi-accent {
        width: 48px;
        height: 5px;
        border-radius: 999px;
        background: linear-gradient(90deg, #7C3AED 0%, #38BDF8 100%);
        margin-bottom: 0.9rem;
    }

    .insight-card {
        background: rgba(15, 23, 42, 0.92);
        border: 1px solid rgba(148, 163, 184, 0.20);
        border-left: 5px solid #38BDF8;
        border-radius: 18px;
        padding: 1rem 1.1rem;
        color: #E2E8F0;
        box-shadow: 0 10px 26px rgba(0,0,0,0.24);
        min-height: 105px;
        margin-bottom: 0.8rem;
    }

    .insight-label {
        color: #AFC0D4;
        font-size: 0.95rem;
        margin-bottom: 0.38rem;
        font-weight: 600;
    }

    .insight-value {
        color: #F8FAFC;
        font-size: 1.35rem;
        font-weight: 850;
    }

    h1, h2, h3 {
        color: #F8FAFC !important;
    }

    div[data-testid="stTabs"] button {
        font-size: 1rem;
        font-weight: 700;
        border-radius: 10px 10px 0 0;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(148,163,184,0.14);
        border-radius: 16px;
        overflow: hidden;
        font-size: 1rem;
    }

    hr {
        border-color: rgba(255,255,255,0.10);
    }

    /* Ajustes globais de leitura */
    p, label, span, div {
        letter-spacing: 0.01rem;
    }

    div[data-testid="stTabs"] button {
        font-size: 1.05rem !important;
        font-weight: 750 !important;
        padding: 0.65rem 0.9rem !important;
    }

    div[data-testid="stDataFrame"] {
        font-size: 1.05rem !important;
    }

    div[data-testid="stDataFrame"] div {
        font-size: 1.02rem !important;
    }

    .stMarkdown {
        font-size: 1.05rem;
    }

    .section-note {
        line-height: 1.6;
    }

    .kpi-label {
        font-size: 1.02rem;
    }

    .kpi-value {
        font-size: 2.1rem;
    }

    .insight-label {
        font-size: 1rem;
    }

    .insight-value {
        font-size: 1.42rem;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        font-size: 1.35rem !important;
    }

    section[data-testid="stSidebar"] label {
        font-size: 1rem !important;
        font-weight: 650 !important;
    }


    /* =========================
       ABAS / MENUS DO DASHBOARD
       ========================= */

    div[data-testid="stTabs"] {
        margin-top: 1rem;
        margin-bottom: 1.4rem;
    }

    div[data-testid="stTabs"] [role="tablist"] {
        gap: 0.6rem;
        flex-wrap: wrap;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.20);
    }

    div[data-testid="stTabs"] [role="tab"] {
        background: rgba(15, 23, 42, 0.92);
        color: #E2E8F0 !important;
        border: 1px solid rgba(124, 58, 237, 0.25);
        border-radius: 16px;
        padding: 0.78rem 1.15rem;
        min-height: 54px;
        font-size: 1.05rem !important;
        font-weight: 750 !important;
        transition: all 0.25s ease;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.025);
    }

    div[data-testid="stTabs"] [role="tab"]:hover {
        background: linear-gradient(
            135deg,
            rgba(30, 41, 59, 0.98),
            rgba(49, 46, 129, 0.94)
        );
        color: #FFFFFF !important;
        border-color: rgba(56, 189, 248, 0.60);
        transform: translateY(-1px);
        box-shadow: 0 0 18px rgba(56, 189, 248, 0.12);
    }

    div[data-testid="stTabs"] [aria-selected="true"] {
        background: linear-gradient(
            135deg,
            rgba(79, 70, 229, 0.98),
            rgba(14, 165, 233, 0.94)
        );
        color: #FFFFFF !important;
        border: 1px solid rgba(125, 211, 252, 0.90);
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.05),
            0 10px 24px rgba(14, 165, 233, 0.18);
    }

    div[data-testid="stTabs"] [role="tab"] p {
        font-size: 1.05rem !important;
        font-weight: 750 !important;
        margin: 0;
        white-space: nowrap;
    }

    div[data-testid="stTabs"] [role="tab"]:focus {
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.45) !important;
    }

    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background-color: transparent !important;
    }


    /* =========================
       STORYTELLING EXECUTIVO
       ========================= */

    .story-box {
        background: linear-gradient(135deg, rgba(15,23,42,0.96), rgba(30,41,59,0.90));
        border: 1px solid rgba(56, 189, 248, 0.22);
        border-left: 5px solid #38BDF8;
        border-radius: 18px;
        padding: 1.05rem 1.25rem;
        margin: 1rem 0 1.2rem 0;
        box-shadow: 0 12px 30px rgba(0,0,0,0.24);
        color: #E2E8F0;
    }

    .story-title {
        color: #F8FAFC;
        font-size: 1.22rem;
        font-weight: 850;
        margin-bottom: 0.55rem;
    }

    .story-box ul {
        margin-bottom: 0;
        padding-left: 1.25rem;
    }

    .story-box li {
        margin-bottom: 0.38rem;
        line-height: 1.55;
        font-size: 1rem;
        color: #DDE7F3;
    }

</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data
def load_parquet_data() -> tuple[pd.DataFrame, list[str]]:
    parquet_files = sorted(PROCESSED_DIR.glob("*.parquet"))

    if not parquet_files:
        return pd.DataFrame(), []

    dataframes = []

    for file in parquet_files:
        df = pd.read_parquet(file, engine="pyarrow")
        df["source_file"] = file.name
        dataframes.append(df)

    df = pd.concat(dataframes, ignore_index=True)

    df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
    df["dropoff_datetime"] = pd.to_datetime(df["dropoff_datetime"], errors="coerce")

    df["pickup_date"] = pd.to_datetime(
        df["pickup_date"],
        errors="coerce",
    ).dt.date

    payment_map = {
        1: "Cartão",
        2: "Dinheiro",
        3: "Sem cobrança",
        4: "Disputa",
        5: "Desconhecido",
        6: "Viagem anulada",
    }

    day_period_map = {
        "madrugada": "madrugada",
        "manha": "manhã",
        "tarde": "tarde",
        "noite": "noite",
    }

    distance_category_map = {
        "curta": "curta",
        "media": "média",
        "longa": "longa",
        "desconhecida": "desconhecida",
    }

    duration_category_map = {
        "muito_curta": "muito curta",
        "normal": "normal",
        "longa": "longa",
        "desconhecida": "desconhecida",
    }

    weekday_map = {
        "Monday": "segunda-feira",
        "Tuesday": "terça-feira",
        "Wednesday": "quarta-feira",
        "Thursday": "quinta-feira",
        "Friday": "sexta-feira",
        "Saturday": "sábado",
        "Sunday": "domingo",
    }

    df["payment_type_label"] = (
        df["payment_type"]
        .map(payment_map)
        .fillna(df["payment_type"].astype(str))
    )

    df["fornecedor_label"] = "Fornecedor " + df["vendor_id"].astype("Int64").astype(str)
    df["vendor_label"] = df["fornecedor_label"]

    df["day_period_label"] = (
        df["day_period"]
        .map(day_period_map)
        .fillna(df["day_period"].astype(str))
    )

    df["distance_category_label"] = (
        df["distance_category"]
        .map(distance_category_map)
        .fillna(df["distance_category"].astype(str))
    )

    df["duration_category_label"] = (
        df["duration_category"]
        .map(duration_category_map)
        .fillna(df["duration_category"].astype(str))
    )

    if "pickup_weekday" in df.columns:
        df["pickup_weekday_label"] = (
            df["pickup_weekday"]
            .map(weekday_map)
            .fillna(df["pickup_weekday"])
        )
    else:
        df["pickup_weekday_label"] = (
            df["pickup_datetime"]
            .dt.day_name()
            .map(weekday_map)
        )

    return df, [file.name for file in parquet_files]


def format_number_br(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def format_decimal_br(value: float, decimals: int = 2) -> str:
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def format_money_us_br(value: float) -> str:
    formatted = f"{value:,.2f}"
    br_value = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"US$ {br_value}"


def format_percent_br(value: float) -> str:
    return f"{format_decimal_br(value, 2)}%"


def render_kpi_card(label: str, value: str) -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-accent"></div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """


def render_insight_card(label: str, value: str) -> str:
    return f"""
    <div class="insight-card">
        <div class="insight-label">{label}</div>
        <div class="insight-value">{value}</div>
    </div>
    """

def render_story_box(title: str, bullets: list[str]) -> str:
    items = "".join(f"<li>{item}</li>" for item in bullets)

    return f"""
    <div class="story-box">
        <div class="story-title">{title}</div>
        <ul>{items}</ul>
    </div>
    """


def show_insight_row(insights: list[tuple[str, str]]) -> None:
    columns = st.columns(len(insights))

    for column, (label, value) in zip(columns, insights):
        with column:
            st.markdown(
                render_insight_card(label, value),
                unsafe_allow_html=True,
            )


def top_count_with_pct(df: pd.DataFrame, column: str) -> tuple[str, float]:
    result = df.groupby(column).size().sort_values(ascending=False)

    if result.empty:
        return "N/A", 0.0

    label = result.index[0]
    pct = (result.iloc[0] / len(df)) * 100 if len(df) > 0 else 0.0

    return str(label), pct


def top_sum_with_value(df: pd.DataFrame, group_column: str, value_column: str) -> tuple[str, float]:
    result = (
        df.groupby(group_column)
        .agg(total=(value_column, "sum"))
        .sort_values("total", ascending=False)
    )

    if result.empty:
        return "N/A", 0.0

    return str(result.index[0]), float(result.iloc[0]["total"])


def top_mean_with_value(df: pd.DataFrame, group_column: str, value_column: str) -> tuple[str, float]:
    result = (
        df.groupby(group_column)
        .agg(media=(value_column, "mean"))
        .sort_values("media", ascending=False)
    )

    if result.empty:
        return "N/A", 0.0

    return str(result.index[0]), float(result.iloc[0]["media"])


def show_executive_story(df: pd.DataFrame) -> None:
    period_label, period_pct = top_count_with_pct(df, "day_period_label")
    payment_label, payment_pct = top_count_with_pct(df, "payment_type_label")
    vendor_label, vendor_revenue = top_sum_with_value(df, "vendor_label", "total_amount")

    suspicious_pct = (
        df["is_suspicious_trip"].sum() / len(df) * 100
        if len(df) > 0
        else 0
    )

    st.markdown(
        render_story_box(
            "Resumo executivo",
            [
                f"A análise considera <strong>{format_number_br(len(df))}</strong> corridas consolidadas, com dados tratados e indicadores prontos para tomada de decisão.",
                f"O turno com maior concentração de corridas foi <strong>{period_label}</strong>, representando <strong>{format_percent_br(period_pct)}</strong> do volume filtrado.",
                f"A forma de pagamento mais utilizada foi <strong>{payment_label}</strong>, com participação de <strong>{format_percent_br(payment_pct)}</strong>.",
                f"O <strong>{vendor_label}</strong> concentrou a maior receita, somando <strong>{format_money_us_br(vendor_revenue)}</strong>.",
                f"A taxa de corridas suspeitas ficou em <strong>{format_percent_br(suspicious_pct)}</strong>, indicando boa qualidade geral da base analisada.",
            ],
        ),
        unsafe_allow_html=True,
    )


def format_chart_value(value: float, value_format: str) -> str:
    if value_format == "money":
        return format_money_us_br(value)

    if value_format == "decimal":
        return format_decimal_br(value, 2)

    if value_format == "percent":
        return format_percent_br(value)

    return format_number_br(value)


def create_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    labels: dict,
    value_format: str = "number",
):
    chart_df = df.copy()
    chart_df["valor_formatado"] = chart_df[y].apply(
        lambda value: format_chart_value(value, value_format)
    )

    fig = px.bar(
        chart_df,
        x=x,
        y=y,
        title=title,
        text="valor_formatado",
        template="plotly_dark",
        labels=labels,
        color_discrete_sequence=["#7C3AED"],
        hover_data={"valor_formatado": False},
    )

    fig.update_traces(
        marker_line_color="rgba(255,255,255,0.10)",
        marker_line_width=1.2,
        opacity=0.94,
        textposition="inside",
        textfont_size=17,
        textfont_color="#FFFFFF",
    )

    fig.update_layout(
        title_font_size=24,
        title_font_color="#F8FAFC",
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(l=20, r=20, t=70, b=30),
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.58)",
        font=dict(color="#E2E8F0", size=17),
        xaxis=dict(
            type="category",
            showgrid=False,
            zeroline=False,
            tickfont=dict(color="#E2E8F0", size=17),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(148,163,184,0.14)",
            zeroline=False,
            tickfont=dict(color="#CBD5E1", size=15),
        ),
    )

    return fig


def create_line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    labels: dict,
    value_format: str = "number",
):
    chart_df = df.copy()
    chart_df["valor_formatado"] = chart_df[y].apply(
        lambda value: format_chart_value(value, value_format)
    )

    fig = px.line(
        chart_df,
        x=x,
        y=y,
        title=title,
        markers=True,
        template="plotly_dark",
        labels=labels,
        hover_data={"valor_formatado": True},
    )

    fig.update_traces(
        line=dict(color="#38BDF8", width=3.5),
        marker=dict(size=8, color="#7C3AED"),
    )

    fig.update_layout(
        title_font_size=24,
        title_font_color="#F8FAFC",
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(l=20, r=20, t=70, b=30),
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.58)",
        font=dict(color="#E2E8F0", size=17),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(color="#E2E8F0", size=17),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(148,163,184,0.14)",
            zeroline=False,
            tickfont=dict(color="#CBD5E1", size=15),
        ),
    )

    return fig


def format_table(
    df: pd.DataFrame,
    column_labels: dict,
    integer_columns: list[str] | None = None,
    decimal_columns: list[str] | None = None,
    money_columns: list[str] | None = None,
    percent_columns: list[str] | None = None,
    boolean_columns: list[str] | None = None,
) -> pd.DataFrame:
    integer_columns = integer_columns or []
    decimal_columns = decimal_columns or []
    money_columns = money_columns or []
    percent_columns = percent_columns or []
    boolean_columns = boolean_columns or []

    display_df = df.copy()

    for column in integer_columns:
        if column in display_df.columns:
            display_df[column] = display_df[column].apply(format_number_br)

    for column in decimal_columns:
        if column in display_df.columns:
            display_df[column] = display_df[column].apply(
                lambda value: format_decimal_br(value, 2)
            )

    for column in money_columns:
        if column in display_df.columns:
            display_df[column] = display_df[column].apply(format_money_us_br)

    for column in percent_columns:
        if column in display_df.columns:
            display_df[column] = display_df[column].apply(format_percent_br)

    for column in boolean_columns:
        if column in display_df.columns:
            display_df[column] = display_df[column].map(
                {True: "Sim", False: "Não"}
            )

    display_df = display_df.rename(columns=column_labels)

    return display_df


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.title("Filtros")

    min_date = df["pickup_date"].min()
    max_date = df["pickup_date"].max()

    selected_date_range = st.sidebar.date_input(
        "Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    filtered_df = df.copy()

    if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
        start_date, end_date = selected_date_range

        filtered_df = filtered_df[
            (filtered_df["pickup_date"] >= start_date)
            & (filtered_df["pickup_date"] <= end_date)
        ]

    day_period_options = sorted(filtered_df["day_period_label"].dropna().unique())

    selected_periods = st.sidebar.multiselect(
        "Turno do dia",
        options=day_period_options,
        default=day_period_options,
    )

    if selected_periods:
        filtered_df = filtered_df[
            filtered_df["day_period_label"].isin(selected_periods)
        ]

    payment_options = sorted(filtered_df["payment_type_label"].dropna().unique())

    selected_payments = st.sidebar.multiselect(
        "Forma de pagamento",
        options=payment_options,
        default=payment_options,
    )

    if selected_payments:
        filtered_df = filtered_df[
            filtered_df["payment_type_label"].isin(selected_payments)
        ]

    fornecedor_options = sorted(filtered_df["fornecedor_label"].dropna().unique())

    selected_fornecedors = st.sidebar.multiselect(
        "Fornecedor",
        options=fornecedor_options,
        default=fornecedor_options,
    )

    if selected_fornecedors:
        filtered_df = filtered_df[
            filtered_df["fornecedor_label"].isin(selected_fornecedors)
        ]

    remove_suspicious = st.sidebar.checkbox(
        "Remover corridas suspeitas",
        value=False,
    )

    if remove_suspicious and "is_suspicious_trip" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["is_suspicious_trip"] == False
        ]

    st.sidebar.divider()

    st.sidebar.caption(
        "Dashboard baseado em uma amostra tratada pelo pipeline ETL."
    )

    return filtered_df


def show_header(parquet_files: list[str]) -> None:
    st.markdown(
        '<div class="main-title">🚕 NYC Yellow Taxi Trips Analytics</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">Painel executivo das corridas Yellow Taxi, com foco em demanda, receita, operação e qualidade dos dados.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sample-warning">
            <strong>Base analisada:</strong> amostra de 30.000 registros,
            considerando 10.000 linhas de cada arquivo mensal.
            Os arquivos brutos completos permanecem preservados na camada <code>data/raw</code>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Arquivos processados carregados"):
        for file in parquet_files:
            st.write(file)


def show_kpis(df: pd.DataFrame) -> None:
    total_trips = len(df)
    total_revenue = df["total_amount"].sum()
    avg_ticket = df["total_amount"].mean()
    avg_distance = df["trip_distance"].mean()
    avg_duration = df["trip_duration_minutes"].mean()
    suspicious_trips = int(df["is_suspicious_trip"].sum())

    suspicious_pct = (suspicious_trips / total_trips) * 100 if total_trips else 0

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    with col1:
        st.markdown(
            render_kpi_card("Corridas", format_number_br(total_trips)),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            render_kpi_card("Receita", format_money_us_br(total_revenue)),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            render_kpi_card("Ticket médio", format_money_us_br(avg_ticket)),
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            render_kpi_card(
                "Distância média (milhas)",
                f"{format_decimal_br(avg_distance)} mi",
            ),
            unsafe_allow_html=True,
        )

    with col5:
        st.markdown(
            render_kpi_card(
                "Duração média",
                f"{format_decimal_br(avg_duration)} min",
            ),
            unsafe_allow_html=True,
        )

    with col6:
        st.markdown(
            render_kpi_card(
                "Corridas suspeitas",
                format_percent_br(suspicious_pct),
            ),
            unsafe_allow_html=True,
        )


def show_executive_insights(df: pd.DataFrame) -> None:
    st.subheader("Insights executivos")

    best_period = (
        df.groupby("day_period_label")
        .size()
        .sort_values(ascending=False)
        .index[0]
    )

    best_payment = (
        df.groupby("payment_type_label")
        .size()
        .sort_values(ascending=False)
        .index[0]
    )

    best_fornecedor = (
        df.groupby("fornecedor_label")
        .agg(total_revenue=("total_amount", "sum"))
        .sort_values("total_revenue", ascending=False)
        .index[0]
    )

    suspicious_pct = (
        df["is_suspicious_trip"].sum() / len(df) * 100
        if len(df) > 0
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            render_insight_card("Turno com maior volume", best_period),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            render_insight_card("Pagamento mais usado", best_payment),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            render_insight_card("Fornecedor com maior receita", best_fornecedor),
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            render_insight_card("Taxa de suspeitas", format_percent_br(suspicious_pct)),
            unsafe_allow_html=True,
        )


def view_executive(df: pd.DataFrame) -> None:
    st.subheader("Resumo Executivo")

    st.markdown(
        """
        <div class="section-note">
        Síntese dos principais indicadores para leitura executiva: demanda, receita, operação e qualidade dos dados.
        </div>
        """,
        unsafe_allow_html=True,
    )

    show_kpis(df)
    show_executive_insights(df)
    show_executive_story(df)

    col1, col2 = st.columns(2)

    trips_by_day = (
        df.groupby("pickup_date")
        .size()
        .reset_index(name="total_trips")
        .sort_values("pickup_date")
    )

    revenue_by_day = (
        df.groupby("pickup_date")
        .agg(total_revenue=("total_amount", "sum"))
        .reset_index()
        .sort_values("pickup_date")
    )

    with col1:
        fig = create_line_chart(
            trips_by_day,
            x="pickup_date",
            y="total_trips",
            title="Corridas por dia",
            labels={"pickup_date": "Data", "total_trips": "Corridas"},
            value_format="number",
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = create_line_chart(
            revenue_by_day,
            x="pickup_date",
            y="total_revenue",
            title="Receita por dia",
            labels={"pickup_date": "Data", "total_revenue": "Receita"},
            value_format="money",
        )
        st.plotly_chart(fig, width="stretch")

    col3, col4 = st.columns(2)

    with col3:
        period_summary = (
            df.groupby("day_period_label")
            .size()
            .reset_index(name="total_trips")
            .sort_values("total_trips", ascending=False)
        )

        fig = create_bar_chart(
            period_summary,
            x="day_period_label",
            y="total_trips",
            title="Corridas por turno",
            labels={"day_period_label": "Turno", "total_trips": "Corridas"},
            value_format="number",
        )
        st.plotly_chart(fig, width="stretch")

    with col4:
        quality_summary = pd.DataFrame(
            {
                "status": ["Válidas", "Suspeitas"],
                "total": [
                    int((df["is_suspicious_trip"] == False).sum()),
                    int((df["is_suspicious_trip"] == True).sum()),
                ],
            }
        )

        fig = create_bar_chart(
            quality_summary,
            x="status",
            y="total",
            title="Qualidade geral das corridas",
            labels={"status": "Status", "total": "Total"},
            value_format="number",
        )
        st.plotly_chart(fig, width="stretch")


def view_by_hour(df: pd.DataFrame) -> None:
    st.subheader("Visão por Hora")

    st.markdown(
        """
        <div class="section-note">
        Identifica os horários de maior demanda e a variação de tarifa ao longo do dia.
        </div>
        """,
        unsafe_allow_html=True,
    )

    hourly = (
        df.groupby("pickup_hour")
        .agg(
            total_trips=("pickup_hour", "count"),
            avg_fare=("fare_amount", "mean"),
            avg_duration=("trip_duration_minutes", "mean"),
            avg_speed=("avg_speed_mph", "mean"),
        )
        .reset_index()
        .round(2)
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = create_bar_chart(
            hourly,
            x="pickup_hour",
            y="total_trips",
            title="Volume de corridas por hora",
            labels={"pickup_hour": "Hora", "total_trips": "Corridas"},
            value_format="number",
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = create_line_chart(
            hourly,
            x="pickup_hour",
            y="avg_fare",
            title="Tarifa média por hora",
            labels={"pickup_hour": "Hora", "avg_fare": "Tarifa média"},
            value_format="money",
        )
        st.plotly_chart(fig, width="stretch")

    display_df = format_table(
        hourly,
        column_labels={
            "pickup_hour": "Hora",
            "total_trips": "Total de corridas",
            "avg_fare": "Tarifa média",
            "avg_duration": "Duração média (min)",
            "avg_speed": "Velocidade média (mph)",
        },
        integer_columns=["total_trips"],
        money_columns=["avg_fare"],
        decimal_columns=["avg_duration", "avg_speed"],
    )

    st.dataframe(display_df, width="stretch", hide_index=True, height=420)


def view_fornecedor(df: pd.DataFrame) -> None:
    st.subheader("Visão por Fornecedor")

    st.markdown(
        """
        <div class="section-note">
        Compara o desempenho dos fornecedores por volume, receita, ticket médio e eficiência operacional.
        </div>
        """,
        unsafe_allow_html=True,
    )

    fornecedor = (
        df.groupby("fornecedor_label")
        .agg(
            total_trips=("fornecedor_label", "count"),
            total_revenue=("total_amount", "sum"),
            avg_ticket=("total_amount", "mean"),
            avg_distance=("trip_distance", "mean"),
            avg_duration=("trip_duration_minutes", "mean"),
            avg_speed=("avg_speed_mph", "mean"),
        )
        .reset_index()
        .round(2)
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = create_bar_chart(
            fornecedor,
            x="fornecedor_label",
            y="total_trips",
            title="Corridas por fornecedor",
            labels={"fornecedor_label": "Fornecedor", "total_trips": "Corridas"},
            value_format="number",
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = create_bar_chart(
            fornecedor,
            x="fornecedor_label",
            y="total_revenue",
            title="Receita por fornecedor",
            labels={"fornecedor_label": "Fornecedor", "total_revenue": "Receita"},
            value_format="money",
        )
        st.plotly_chart(fig, width="stretch")

    display_df = format_table(
        fornecedor,
        column_labels={
            "fornecedor_label": "Fornecedor",
            "total_trips": "Total de corridas",
            "total_revenue": "Receita total",
            "avg_ticket": "Ticket médio",
            "avg_distance": "Distância média (mi)",
            "avg_duration": "Duração média (min)",
            "avg_speed": "Velocidade média (mph)",
        },
        integer_columns=["total_trips"],
        money_columns=["total_revenue", "avg_ticket"],
        decimal_columns=["avg_distance", "avg_duration", "avg_speed"],
    )

    st.dataframe(display_df, width="stretch", hide_index=True, height=360)


def view_payment(df: pd.DataFrame) -> None:
    st.subheader("Visão por Pagamento")

    st.markdown(
        """
        <div class="section-note">
        Analisa a participação das formas de pagamento e seu impacto na receita e nas gorjetas.
        </div>
        """,
        unsafe_allow_html=True,
    )

    payment = (
        df.groupby("payment_type_label")
        .agg(
            total_trips=("payment_type_label", "count"),
            total_revenue=("total_amount", "sum"),
            avg_ticket=("total_amount", "mean"),
            avg_tip=("tip_amount", "mean"),
        )
        .reset_index()
        .round(2)
    )

    payment["pct_trips"] = (
        payment["total_trips"] / payment["total_trips"].sum() * 100
    ).round(2)


    top_payment_volume = payment.sort_values("total_trips", ascending=False).iloc[0]
    top_payment_revenue = payment.sort_values("total_revenue", ascending=False).iloc[0]
    top_payment_tip = payment.sort_values("avg_tip", ascending=False).iloc[0]

    show_insight_row(
        [
            (
                "Forma mais usada",
                f"{top_payment_volume['payment_type_label']} · {format_percent_br(top_payment_volume['pct_trips'])}",
            ),
            (
                "Maior receita",
                f"{top_payment_revenue['payment_type_label']} · {format_money_us_br(top_payment_revenue['total_revenue'])}",
            ),
            (
                "Maior gorjeta média",
                f"{top_payment_tip['payment_type_label']} · {format_money_us_br(top_payment_tip['avg_tip'])}",
            ),
        ]
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = create_bar_chart(
            payment.sort_values("total_trips", ascending=False),
            x="payment_type_label",
            y="total_trips",
            title="Corridas por forma de pagamento",
            labels={
                "payment_type_label": "Forma de pagamento",
                "total_trips": "Corridas",
            },
            value_format="number",
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = create_bar_chart(
            payment.sort_values("total_revenue", ascending=False),
            x="payment_type_label",
            y="total_revenue",
            title="Receita por forma de pagamento",
            labels={
                "payment_type_label": "Forma de pagamento",
                "total_revenue": "Receita",
            },
            value_format="money",
        )
        st.plotly_chart(fig, width="stretch")

    display_df = format_table(
        payment,
        column_labels={
            "payment_type_label": "Forma de pagamento",
            "total_trips": "Total de corridas",
            "total_revenue": "Receita total",
            "avg_ticket": "Ticket médio",
            "avg_tip": "Gorjeta média",
            "pct_trips": "Participação (%)",
        },
        integer_columns=["total_trips"],
        money_columns=["total_revenue", "avg_ticket", "avg_tip"],
        percent_columns=["pct_trips"],
    )

    st.dataframe(display_df, width="stretch", hide_index=True, height=360)


def view_weekday(df: pd.DataFrame) -> None:
    st.subheader("Visão por Dia da Semana")

    st.markdown(
        """
        <div class="section-note">
        Mostra padrões semanais observados na amostra analisada, considerando volume, receita e ticket médio.
        </div>
        """,
        unsafe_allow_html=True,
    )

    weekday_order = [
        "segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo",
    ]

    weekday = (
        df.groupby("pickup_weekday_label")
        .agg(
            total_trips=("pickup_weekday_label", "count"),
            total_revenue=("total_amount", "sum"),
            avg_ticket=("total_amount", "mean"),
            avg_distance=("trip_distance", "mean"),
            avg_duration=("trip_duration_minutes", "mean"),
        )
        .reset_index()
        .round(2)
    )

    weekday["weekday_order"] = weekday["pickup_weekday_label"].apply(
        lambda value: weekday_order.index(value)
        if value in weekday_order
        else 99
    )

    weekday = weekday.sort_values("weekday_order")


    top_weekday_volume = weekday.sort_values("total_trips", ascending=False).iloc[0]
    top_weekday_revenue = weekday.sort_values("total_revenue", ascending=False).iloc[0]
    top_weekday_ticket = weekday.sort_values("avg_ticket", ascending=False).iloc[0]

    show_insight_row(
        [
            (
                "Dia com maior volume",
                f"{top_weekday_volume['pickup_weekday_label']} · {format_number_br(top_weekday_volume['total_trips'])} corridas",
            ),
            (
                "Dia com maior receita",
                f"{top_weekday_revenue['pickup_weekday_label']} · {format_money_us_br(top_weekday_revenue['total_revenue'])}",
            ),
            (
                "Maior ticket médio",
                f"{top_weekday_ticket['pickup_weekday_label']} · {format_money_us_br(top_weekday_ticket['avg_ticket'])}",
            ),
        ]
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = create_bar_chart(
            weekday,
            x="pickup_weekday_label",
            y="total_trips",
            title="Corridas por dia da semana",
            labels={
                "pickup_weekday_label": "Dia da semana",
                "total_trips": "Corridas",
            },
            value_format="number",
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = create_bar_chart(
            weekday,
            x="pickup_weekday_label",
            y="total_revenue",
            title="Receita por dia da semana",
            labels={
                "pickup_weekday_label": "Dia da semana",
                "total_revenue": "Receita",
            },
            value_format="money",
        )
        st.plotly_chart(fig, width="stretch")

    display_df = format_table(
        weekday.drop(columns=["weekday_order"]),
        column_labels={
            "pickup_weekday_label": "Dia da semana",
            "total_trips": "Total de corridas",
            "total_revenue": "Receita total",
            "avg_ticket": "Ticket médio",
            "avg_distance": "Distância média (mi)",
            "avg_duration": "Duração média (min)",
        },
        integer_columns=["total_trips"],
        money_columns=["total_revenue", "avg_ticket"],
        decimal_columns=["avg_distance", "avg_duration"],
    )

    st.dataframe(display_df, width="stretch", hide_index=True, height=360)


def view_financial(df: pd.DataFrame) -> None:
    st.subheader("Visão Financeira")

    st.markdown(
        """
        <div class="section-note">
        Resume os principais indicadores financeiros por turno, incluindo receita, ticket médio e eficiência por milha.
        </div>
        """,
        unsafe_allow_html=True,
    )

    financial_by_period = (
        df.groupby("day_period_label")
        .agg(
            total_revenue=("total_amount", "sum"),
            avg_ticket=("total_amount", "mean"),
            avg_tip=("tip_amount", "mean"),
            revenue_per_minute=("revenue_per_minute", "mean"),
            revenue_per_mile=("revenue_per_mile", "mean"),
        )
        .reset_index()
        .round(2)
    )


    top_financial_revenue = financial_by_period.sort_values("total_revenue", ascending=False).iloc[0]
    top_financial_ticket = financial_by_period.sort_values("avg_ticket", ascending=False).iloc[0]
    top_financial_mile = financial_by_period.sort_values("revenue_per_mile", ascending=False).iloc[0]

    show_insight_row(
        [
            (
                "Turno com maior receita",
                f"{top_financial_revenue['day_period_label']} · {format_money_us_br(top_financial_revenue['total_revenue'])}",
            ),
            (
                "Maior ticket médio",
                f"{top_financial_ticket['day_period_label']} · {format_money_us_br(top_financial_ticket['avg_ticket'])}",
            ),
            (
                "Maior receita por milha",
                f"{top_financial_mile['day_period_label']} · {format_money_us_br(top_financial_mile['revenue_per_mile'])}",
            ),
        ]
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = create_bar_chart(
            financial_by_period,
            x="day_period_label",
            y="total_revenue",
            title="Receita por turno",
            labels={"day_period_label": "Turno", "total_revenue": "Receita"},
            value_format="money",
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = create_bar_chart(
            financial_by_period,
            x="day_period_label",
            y="avg_ticket",
            title="Ticket médio por turno",
            labels={"day_period_label": "Turno", "avg_ticket": "Ticket médio"},
            value_format="money",
        )
        st.plotly_chart(fig, width="stretch")

    display_df = format_table(
        financial_by_period,
        column_labels={
            "day_period_label": "Turno",
            "total_revenue": "Receita total",
            "avg_ticket": "Ticket médio",
            "avg_tip": "Gorjeta média",
            "revenue_per_minute": "Receita por minuto",
            "revenue_per_mile": "Receita por milha",
        },
        money_columns=[
            "total_revenue",
            "avg_ticket",
            "avg_tip",
            "revenue_per_minute",
            "revenue_per_mile",
        ],
    )

    st.dataframe(display_df, width="stretch", hide_index=True, height=360)


def view_operational(df: pd.DataFrame) -> None:
    st.subheader("Visão Operacional")

    st.markdown(
        """
        <div class="section-note">
        Analisa o perfil operacional das corridas por distância, duração e velocidade média.
        </div>
        """,
        unsafe_allow_html=True,
    )

    distance_category = (
        df.groupby("distance_category_label")
        .size()
        .reset_index(name="total_trips")
        .sort_values("total_trips", ascending=False)
    )

    duration_category = (
        df.groupby("duration_category_label")
        .size()
        .reset_index(name="total_trips")
        .sort_values("total_trips", ascending=False)
    )


    top_distance_category = distance_category.sort_values("total_trips", ascending=False).iloc[0]
    top_duration_category = duration_category.sort_values("total_trips", ascending=False).iloc[0]

    show_insight_row(
        [
            (
                "Faixa de distância dominante",
                f"{top_distance_category['distance_category_label']} · {format_number_br(top_distance_category['total_trips'])} corridas",
            ),
            (
                "Faixa de duração dominante",
                f"{top_duration_category['duration_category_label']} · {format_number_br(top_duration_category['total_trips'])} corridas",
            ),
            (
                "Leitura operacional",
                "corridas curtas e normais concentram a maior parte da amostra",
            ),
        ]
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = create_bar_chart(
            distance_category,
            x="distance_category_label",
            y="total_trips",
            title="Corridas por faixa de distância",
            labels={
                "distance_category_label": "Faixa de distância",
                "total_trips": "Corridas",
            },
            value_format="number",
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = create_bar_chart(
            duration_category,
            x="duration_category_label",
            y="total_trips",
            title="Corridas por faixa de duração",
            labels={
                "duration_category_label": "Faixa de duração",
                "total_trips": "Corridas",
            },
            value_format="number",
        )
        st.plotly_chart(fig, width="stretch")

    operational_summary = (
        df.groupby("day_period_label")
        .agg(
            avg_distance=("trip_distance", "mean"),
            avg_duration=("trip_duration_minutes", "mean"),
            avg_speed=("avg_speed_mph", "mean"),
            total_trips=("day_period_label", "count"),
        )
        .reset_index()
        .round(2)
    )

    display_df = format_table(
        operational_summary,
        column_labels={
            "day_period_label": "Turno",
            "avg_distance": "Distância média (mi)",
            "avg_duration": "Duração média (min)",
            "avg_speed": "Velocidade média (mph)",
            "total_trips": "Total de corridas",
        },
        integer_columns=["total_trips"],
        decimal_columns=["avg_distance", "avg_duration", "avg_speed"],
    )

    st.dataframe(display_df, width="stretch", hide_index=True, height=360)


def view_quality(df: pd.DataFrame) -> None:
    st.subheader("Visão de Qualidade e Anomalias")

    st.markdown(
        """
        <div class="section-note">
        Monitora a qualidade da base analisada, destacando registros suspeitos e principais regras de validação.
        </div>
        """,
        unsafe_allow_html=True,
    )

    total_rows = len(df)
    suspicious_count = int(df["is_suspicious_trip"].sum())
    suspicious_pct = (suspicious_count / total_rows) * 100 if total_rows else 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            render_kpi_card("Registros analisados", format_number_br(total_rows)),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            render_kpi_card("Corridas suspeitas", format_number_br(suspicious_count)),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            render_kpi_card("Taxa de suspeitas", format_percent_br(suspicious_pct)),
            unsafe_allow_html=True,
        )

    quality_rules = {
        "Distância zero ou negativa": df["trip_distance"] <= 0,
        "Duração zero ou negativa": df["trip_duration_minutes"] <= 0,
        "Valor total zero ou negativo": df["total_amount"] <= 0,
        "Velocidade acima de 80 mph": df["avg_speed_mph"] > 80,
        "Flag geral de suspeita": df["is_suspicious_trip"] == True,
    }

    quality_table = []

    for rule_name, mask in quality_rules.items():
        failures = int(mask.sum())
        failure_pct = (failures / total_rows) * 100 if total_rows else 0

        quality_table.append(
            {
                "rule": rule_name,
                "failures": failures,
                "failure_pct": round(failure_pct, 2),
            }
        )

    quality_df = pd.DataFrame(quality_table)


    main_quality_issue = quality_df.sort_values("failures", ascending=False).iloc[0]

    show_insight_row(
        [
            (
                "Principal regra acionada",
                f"{main_quality_issue['rule']} · {format_number_br(main_quality_issue['failures'])} falhas",
            ),
            (
                "Taxa geral de suspeitas",
                format_percent_br(suspicious_pct),
            ),
            (
                "Leitura de qualidade",
                "baixo percentual de anomalias na base analisada",
            ),
        ]
    )

    fig = create_bar_chart(
        quality_df,
        x="rule",
        y="failures",
        title="Falhas por regra de qualidade",
        labels={"rule": "Regra", "failures": "Falhas"},
        value_format="number",
    )

    st.plotly_chart(fig, width="stretch")

    display_quality_df = format_table(
        quality_df,
        column_labels={
            "rule": "Regra",
            "failures": "Falhas",
            "failure_pct": "Percentual de falhas",
        },
        integer_columns=["failures"],
        percent_columns=["failure_pct"],
    )

    st.dataframe(display_quality_df, width="stretch", hide_index=True, height=300)

    suspicious_df = df[df["is_suspicious_trip"] == True].copy()

    st.subheader("Amostra de corridas suspeitas")

    columns = [
        "fornecedor_label",
        "pickup_datetime",
        "dropoff_datetime",
        "day_period_label",
        "trip_distance",
        "trip_duration_minutes",
        "avg_speed_mph",
        "fare_amount",
        "total_amount",
        "payment_type_label",
        "distance_category_label",
        "duration_category_label",
        "is_suspicious_trip",
    ]

    existing_columns = [
        column for column in columns if column in suspicious_df.columns
    ]

    display_df = format_table(
        suspicious_df[existing_columns].head(100),
        column_labels={
            "fornecedor_label": "Fornecedor",
            "pickup_datetime": "Início da corrida",
            "dropoff_datetime": "Fim da corrida",
            "day_period_label": "Turno",
            "trip_distance": "Distância (mi)",
            "trip_duration_minutes": "Duração (min)",
            "avg_speed_mph": "Velocidade média (mph)",
            "fare_amount": "Tarifa",
            "total_amount": "Valor total",
            "payment_type_label": "Forma de pagamento",
            "distance_category_label": "Faixa de distância",
            "duration_category_label": "Faixa de duração",
            "is_suspicious_trip": "Corrida suspeita",
        },
        decimal_columns=[
            "trip_distance",
            "trip_duration_minutes",
            "avg_speed_mph",
        ],
        money_columns=["fare_amount", "total_amount"],
        boolean_columns=["is_suspicious_trip"],
    )

    st.dataframe(display_df, width="stretch", hide_index=True, height=360)
def get_approx_area(lat: float, lon: float) -> str:
    """
    Classifica coordenadas em áreas aproximadas de NYC.
    Não substitui o zoneamento oficial da TLC, mas melhora a leitura executiva.
    """
    if pd.isna(lat) or pd.isna(lon):
        return "Coordenada inválida"

    # Aeroportos
    if 40.62 <= lat <= 40.67 and -73.84 <= lon <= -73.74:
        return "Queens - JFK Airport"

    if 40.76 <= lat <= 40.79 and -73.90 <= lon <= -73.85:
        return "Queens - LaGuardia"

    # Manhattan
    if 40.70 <= lat <= 40.89 and -74.03 <= lon <= -73.90:
        if lat >= 40.83:
            return "Manhattan - Upper Manhattan"
        if lat >= 40.77:
            return "Manhattan - Upper East/West Side"
        if lat >= 40.74:
            return "Manhattan - Midtown"
        return "Manhattan - Downtown"

    # Brooklyn
    if 40.56 <= lat <= 40.74 and -74.05 <= lon <= -73.83:
        if lat >= 40.68:
            return "Brooklyn - North/Downtown"
        if lat >= 40.63:
            return "Brooklyn - Central"
        return "Brooklyn - South"

    # Queens
    if 40.54 <= lat <= 40.82 and -73.96 <= lon <= -73.70:
        if lon <= -73.90:
            return "Queens - LIC/Astoria"
        if lat <= 40.66:
            return "Queens - South"
        return "Queens - Central/East"

    # Bronx
    if 40.79 <= lat <= 40.92 and -73.93 <= lon <= -73.75:
        return "Bronx"

    # Staten Island
    if 40.48 <= lat <= 40.65 and -74.25 <= lon <= -74.05:
        return "Staten Island"

    # Região próxima de NJ
    if 40.65 <= lat <= 40.85 and -74.25 <= lon <= -74.02:
        return "New Jersey / Newark-Jersey City"

    return "Outra área da região metropolitana"



def get_borough_from_area(area: str) -> str:
    if area.startswith("Manhattan"):
        return "Manhattan"

    if area.startswith("Brooklyn"):
        return "Brooklyn"

    if area.startswith("Queens"):
        return "Queens"

    if area.startswith("Bronx"):
        return "Bronx"

    if area.startswith("Staten Island"):
        return "Staten Island"

    if area.startswith("New Jersey"):
        return "New Jersey"

    return "Região Metropolitana"


def scale_marker_sizes(values: pd.Series, min_size: int = 12, max_size: int = 34) -> list[float]:
    min_value = values.min()
    max_value = values.max()

    if min_value == max_value:
        return [22 for _ in values]

    return (
        min_size
        + ((values - min_value) / (max_value - min_value)) * (max_size - min_size)
    ).tolist()


def build_area_summary(
    df: pd.DataFrame,
    area_column: str,
    borough_column: str,
    lat_column: str,
    lon_column: str,
) -> pd.DataFrame:
    summary = (
        df.groupby([area_column, borough_column])
        .agg(
            total_corridas=(area_column, "count"),
            latitude=(lat_column, "mean"),
            longitude=(lon_column, "mean"),
            receita_total=("total_amount", "sum"),
            ticket_medio=("total_amount", "mean"),
        )
        .reset_index()
        .rename(
            columns={
                area_column: "area",
                borough_column: "macro_area",
            }
        )
        .sort_values("total_corridas", ascending=False)
    )

    total = summary["total_corridas"].sum()
    summary["participacao"] = (
        summary["total_corridas"] / total * 100 if total else 0
    )

    summary["total_formatado"] = summary["total_corridas"].apply(format_number_br)
    summary["participacao_formatada"] = summary["participacao"].apply(format_percent_br)
    summary["receita_formatada"] = summary["receita_total"].apply(format_money_us_br)
    summary["ticket_formatado"] = summary["ticket_medio"].apply(format_money_us_br)

    return summary


def build_layered_geo_map(
    points_df: pd.DataFrame,
    area_summary: pd.DataFrame,
    lat_column: str,
    lon_column: str,
    title: str,
    event_label: str,
):
    center_lat = points_df[lat_column].mean()
    center_lon = points_df[lon_column].mean()

    fig = go.Figure()

    fig.add_trace(
        go.Densitymapbox(
            lat=points_df[lat_column],
            lon=points_df[lon_column],
            radius=15,
            colorscale=[
                [0.00, "#2D1EAA"],
                [0.45, "#9333EA"],
                [0.75, "#F97316"],
                [1.00, "#FDE047"],
            ],
            showscale=True,
            colorbar=dict(
                title="Densidade",
                tickfont=dict(color="#E2E8F0"),
            ),
            hoverinfo="skip",
            name="Mapa de calor",
        )
    )

    if not area_summary.empty:
        marker_sizes = scale_marker_sizes(area_summary["total_corridas"])

        fig.add_trace(
            go.Scattermapbox(
                lat=area_summary["latitude"],
                lon=area_summary["longitude"],
                mode="markers",
                marker=dict(
                    size=marker_sizes,
                    color="#38BDF8",
                    opacity=0.72,
                    sizemode="diameter",
                ),
                customdata=area_summary[
                    [
                        "area",
                        "macro_area",
                        "total_formatado",
                        "participacao_formatada",
                        "receita_formatada",
                        "ticket_formatado",
                    ]
                ],
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Macroárea: %{customdata[1]}<br>"
                    "Tipo: " + event_label + "<br>"
                    "Corridas: %{customdata[2]}<br>"
                    "Participação: %{customdata[3]}<br>"
                    "Receita: %{customdata[4]}<br>"
                    "Ticket médio: %{customdata[5]}"
                    "<extra></extra>"
                ),
                name="Áreas",
            )
        )

    fig.update_layout(
        title=title,
        title_font_size=22,
        title_font_color="#F8FAFC",
        height=560,
        margin=dict(l=10, r=10, t=60, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0", size=15),
        hovermode="closest",
        dragmode="pan",
        uirevision="geo-map",
        mapbox=dict(
            style="carto-darkmatter",
            center={"lat": center_lat, "lon": center_lon},
            zoom=10,
        ),
        showlegend=False,
    )

    return fig


def view_geographic(df: pd.DataFrame) -> None:
    st.subheader("Visão Geográfica")

    st.markdown(
        """
        <div class="section-note">
        Analisa a distribuição espacial das corridas, destacando áreas com maior
        concentração de embarques e desembarques para apoiar leitura operacional
        e tomada de decisão.
        </div>
        """,
        unsafe_allow_html=True,
    )

    required_columns = [
        "pickup_latitude",
        "pickup_longitude",
        "dropoff_latitude",
        "dropoff_longitude",
    ]

    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]

    if missing_columns:
        st.warning(
            "As colunas de latitude e longitude não estão disponíveis nos dados tratados."
        )
        return

    geo_df = df.copy()

    geo_df = geo_df[
        geo_df["pickup_latitude"].between(40.45, 41.05)
        & geo_df["pickup_longitude"].between(-74.30, -73.65)
        & geo_df["dropoff_latitude"].between(40.45, 41.05)
        & geo_df["dropoff_longitude"].between(-74.30, -73.65)
    ].copy()

    if geo_df.empty:
        st.warning("Nenhuma coordenada válida encontrada para exibição no mapa.")
        return

    geo_df["pickup_area"] = geo_df.apply(
        lambda row: get_approx_area(
            row["pickup_latitude"],
            row["pickup_longitude"],
        ),
        axis=1,
    )

    geo_df["dropoff_area"] = geo_df.apply(
        lambda row: get_approx_area(
            row["dropoff_latitude"],
            row["dropoff_longitude"],
        ),
        axis=1,
    )

    geo_df["pickup_macro_area"] = geo_df["pickup_area"].apply(get_borough_from_area)
    geo_df["dropoff_macro_area"] = geo_df["dropoff_area"].apply(get_borough_from_area)

    max_points = 7000

    if len(geo_df) > max_points:
        map_df = geo_df.sample(max_points, random_state=42)
    else:
        map_df = geo_df.copy()

    pickup_summary = build_area_summary(
        geo_df,
        area_column="pickup_area",
        borough_column="pickup_macro_area",
        lat_column="pickup_latitude",
        lon_column="pickup_longitude",
    )

    dropoff_summary = build_area_summary(
        geo_df,
        area_column="dropoff_area",
        borough_column="dropoff_macro_area",
        lat_column="dropoff_latitude",
        lon_column="dropoff_longitude",
    )

    top_pickup = pickup_summary.iloc[0]
    top_dropoff = dropoff_summary.iloc[0]

    valid_pct = (len(geo_df) / len(df)) * 100 if len(df) > 0 else 0

    show_insight_row(
        [
            (
                "Coordenadas válidas",
                f"{format_number_br(len(geo_df))} registros · {format_percent_br(valid_pct)}",
            ),
            (
                "Principal área de embarque",
                f"{top_pickup['area']} · {format_number_br(top_pickup['total_corridas'])} corridas",
            ),
            (
                "Principal área de desembarque",
                f"{top_dropoff['area']} · {format_number_br(top_dropoff['total_corridas'])} corridas",
            ),
        ]
    )

    st.caption(
        "Dica: use o scroll do mouse para aproximar/afastar o mapa e arraste para navegar pelas regiões."
    )

    col1, col2 = st.columns(2)

    map_config = {
        "scrollZoom": True,
        "displayModeBar": True,
        "responsive": True,
    }

    with col1:
        pickup_map = build_layered_geo_map(
            points_df=map_df,
            area_summary=pickup_summary,
            lat_column="pickup_latitude",
            lon_column="pickup_longitude",
            title="Mapa de concentração de embarques",
            event_label="Embarque",
        )

        st.plotly_chart(pickup_map, width="stretch", config=map_config)

    with col2:
        dropoff_map = build_layered_geo_map(
            points_df=map_df,
            area_summary=dropoff_summary,
            lat_column="dropoff_latitude",
            lon_column="dropoff_longitude",
            title="Mapa de concentração de desembarques",
            event_label="Desembarque",
        )

        st.plotly_chart(dropoff_map, width="stretch", config=map_config)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Top áreas de embarque")

        display_pickups = format_table(
            pickup_summary[
                [
                    "area",
                    "macro_area",
                    "total_corridas",
                    "participacao",
                    "receita_total",
                    "ticket_medio",
                ]
            ].head(10),
            column_labels={
                "area": "Área",
                "macro_area": "Macroárea",
                "total_corridas": "Total de embarques",
                "participacao": "Participação",
                "receita_total": "Receita total",
                "ticket_medio": "Ticket médio",
            },
            integer_columns=["total_corridas"],
            percent_columns=["participacao"],
            money_columns=["receita_total", "ticket_medio"],
        )

        st.dataframe(display_pickups, width="stretch", hide_index=True, height=360)

    with col4:
        st.subheader("Top áreas de desembarque")

        display_dropoffs = format_table(
            dropoff_summary[
                [
                    "area",
                    "macro_area",
                    "total_corridas",
                    "participacao",
                    "receita_total",
                    "ticket_medio",
                ]
            ].head(10),
            column_labels={
                "area": "Área",
                "macro_area": "Macroárea",
                "total_corridas": "Total de desembarques",
                "participacao": "Participação",
                "receita_total": "Receita total",
                "ticket_medio": "Ticket médio",
            },
            integer_columns=["total_corridas"],
            percent_columns=["participacao"],
            money_columns=["receita_total", "ticket_medio"],
        )

        st.dataframe(display_dropoffs, width="stretch", hide_index=True, height=360)


def view_data(df: pd.DataFrame) -> None:
    st.subheader("Dados Detalhados")

    st.markdown(
        """
        <div class="section-note">
        Amostra dos registros utilizados nos indicadores do dashboard.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write(f"Linhas após filtros: **{format_number_br(len(df))}**")
    st.write(f"Colunas disponíveis: **{format_number_br(len(df.columns))}**")


    st.markdown(
        render_story_box(
            "Como usar esta aba",
            [
                "Esta visão permite auditar os registros utilizados nos indicadores do dashboard.",
                "Ela permite conferir os dados que passaram pelas etapas de leitura, validação e transformação do pipeline.",
                "Em uma apresentação executiva, esta aba funciona como apoio técnico e camada de rastreabilidade.",
            ],
        ),
        unsafe_allow_html=True,
    )

    columns_to_show = [
        "fornecedor_label",
        "pickup_datetime",
        "dropoff_datetime",
        "pickup_date",
        "pickup_hour",
        "pickup_weekday_label",
        "day_period_label",
        "payment_type_label",
        "trip_distance",
        "trip_duration_minutes",
        "avg_speed_mph",
        "fare_amount",
        "tip_amount",
        "total_amount",
        "revenue_per_minute",
        "revenue_per_mile",
        "distance_category_label",
        "duration_category_label",
        "is_weekend",
        "is_holiday",
        "is_suspicious_trip",
        "source_file",
    ]

    existing_columns = [
        column for column in columns_to_show if column in df.columns
    ]

    display_df = format_table(
        df[existing_columns].head(500),
        column_labels={
            "fornecedor_label": "Fornecedor",
            "pickup_datetime": "Início da corrida",
            "dropoff_datetime": "Fim da corrida",
            "pickup_date": "Data",
            "pickup_hour": "Hora",
            "pickup_weekday_label": "Dia da semana",
            "day_period_label": "Turno",
            "payment_type_label": "Forma de pagamento",
            "trip_distance": "Distância (mi)",
            "trip_duration_minutes": "Duração (min)",
            "avg_speed_mph": "Velocidade média (mph)",
            "fare_amount": "Tarifa",
            "tip_amount": "Gorjeta",
            "total_amount": "Valor total",
            "revenue_per_minute": "Receita por minuto",
            "revenue_per_mile": "Receita por milha",
            "distance_category_label": "Faixa de distância",
            "duration_category_label": "Faixa de duração",
            "is_weekend": "Fim de semana",
            "is_holiday": "Feriado",
            "is_suspicious_trip": "Corrida suspeita",
            "source_file": "Arquivo de origem",
        },
        decimal_columns=[
            "trip_distance",
            "trip_duration_minutes",
            "avg_speed_mph",
        ],
        money_columns=[
            "fare_amount",
            "tip_amount",
            "total_amount",
            "revenue_per_minute",
            "revenue_per_mile",
        ],
        boolean_columns=[
            "is_weekend",
            "is_holiday",
            "is_suspicious_trip",
        ],
    )

    st.dataframe(display_df, width="stretch", hide_index=True, height=360)


def main() -> None:
    df, parquet_files = load_parquet_data()

    if df.empty:
        st.error(
            "Nenhum arquivo Parquet encontrado em data/processed/. "
            "Execute primeiro: python src/load.py"
        )
        return

    show_header(parquet_files)

    filtered_df = apply_filters(df)

    if filtered_df.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
        return

    tabs = st.tabs(
        [
            "📊 Resumo Executivo",
            "🕒 Hora",
            "🚕 Fornecedor",
            "💳 Pagamento",
            "📅 Semana",
            "💰 Financeiro",
            "⚙️ Operacional",
            "🚨 Qualidade",
            "🗺️ Geografia",
            "📁 Detalhes",
        ]
    )

    with tabs[0]:
        view_executive(filtered_df)

    with tabs[1]:
        view_by_hour(filtered_df)

    with tabs[2]:
        view_fornecedor(filtered_df)

    with tabs[3]:
        view_payment(filtered_df)

    with tabs[4]:
        view_weekday(filtered_df)

    with tabs[5]:
        view_financial(filtered_df)

    with tabs[6]:
        view_operational(filtered_df)

    with tabs[7]:
        view_quality(filtered_df)

    with tabs[8]:
        view_geographic(filtered_df)

    with tabs[9]:
        view_data(filtered_df)


if __name__ == "__main__":
    main()
