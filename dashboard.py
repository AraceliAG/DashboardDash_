import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from streamlit_echarts import st_echarts
import plotly.express as px

st.set_page_config(page_title="Dashboard de Sensores", layout="wide")

st.title("Dashboard")
st_autorefresh(interval=5000, key="auto_refresh")

base_path = "DATA_BD"
today_folder = datetime.now().strftime('%Y-%m-%d')
data_dir = os.path.join(base_path, today_folder)

def read_csv(sensor_folder):
    folder_path = os.path.join(data_dir, sensor_folder)
    if not os.path.exists(folder_path):
        return None

    archivos = sorted(os.listdir(folder_path))
    if not archivos:
        return None

    last_file = os.path.join(folder_path, archivos[-1])
    try:
        df = pd.read_csv(last_file, header=None, names=["timestamp", "valor"])
        return df
    except Exception as e:
        st.warning(f"No se pudo leer el archivo: {e}")
        return None

# Ejemplo de gráfica grande: Aquí un ejemplo combinando ambas señales (si quieres algo más elaborado, dime)
def read_all_data(sensor_folder):
    folder_path = os.path.join(data_dir, sensor_folder)
    if not os.path.exists(folder_path):
        return None
    archivos = sorted(os.listdir(folder_path))
    if not archivos:
        return None
    # Leer todos los archivos y concatenar
    dfs = []
    for f in archivos:
        try:
            df = pd.read_csv(os.path.join(folder_path, f), header=None, names=["timestamp", "valor"])
            dfs.append(df)
        except:
            continue
    if dfs:
        return pd.concat(dfs)
    return None

# --- 3 Cards arriba ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div style="padding: 10px; border: 1px solid #ddd; border-radius: 8px; text-align:center;">
            <h3>Ultima Factura</h3>
            <h1>05/12/2025</h1>
        </div>
        """, unsafe_allow_html=True)
    
with col2:
    st.markdown("""
        <div style="padding: 10px; border: 1px solid #ddd; border-radius: 8px; text-align:center;">
            <h3>kHw acumulado</h3>
            <h1>469 Kwh</h1>
        </div>
        """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div style="padding: 10px; border: 1px solid #ddd; border-radius: 8px; text-align:center;">
            <h3>Costo previsto</h3>
            <h1>$634.67</h1>
        </div>
        """, unsafe_allow_html=True)

# --- 2 gráficas lado a lado ---
col1, col2 = st.columns(2)


# --- Columna 1: selector de variable y gráfica de línea ---
with col1:
    variable = st.selectbox("Selecciona variable", ["Voltaje Fase 1", "Corriente Línea 1"], index=0)

    st.markdown(f"### {variable}")
    
    if variable == "Voltaje Fase 1":
        df = read_csv("Voltaje_fase_1")
    else:
        df = read_csv("Corriente_linea1")

    if df is not None:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        st.line_chart(df.set_index("timestamp")["valor"])
    else:
        st.write("No hay datos disponibles")

# --- Columna 2: gráfica de barras por día ---
with col2:
    st.markdown("### Total de Corriente por Día (últimos 7 días)")

    corriente_total = read_all_data("Corriente_linea1")
    if corriente_total is not None:
        corriente_total["timestamp"] = pd.to_datetime(corriente_total["timestamp"])
        # Convertir timestamp a fecha sin tiempo (datetime64[ns])
        corriente_total["fecha"] = corriente_total["timestamp"].dt.normalize()

        # Agrupar por día y sumar
        corriente_por_dia = corriente_total.groupby("fecha")["valor"].sum().reset_index()

        # Obtener fechas de los últimos 7 días (datetime64[ns], sin tiempo)
        fechas_ultimos_7 = pd.date_range(end=pd.Timestamp.today().normalize(), periods=7)

        # Crear DataFrame base con fechas completas
        base = pd.DataFrame({"fecha": fechas_ultimos_7})

        # Merge para asegurar que haya fila para cada fecha, rellenar NaN con 0
        corriente_por_dia = base.merge(corriente_por_dia, on="fecha", how="left").fillna(0)

        corriente_por_dia["valor"] = corriente_por_dia["valor"].astype(float)

        fig_total = px.bar(
            corriente_por_dia,
            x="fecha",
            y="valor",
            labels={"valor": "Corriente Total (A)", "fecha": "Fecha"},
            title="Corriente Total Generada por Día (últimos 7 días)"
        )
        st.plotly_chart(fig_total, use_container_width=True)
    else:
        st.write("No hay datos suficientes para calcular corriente por día.")

import plotly.express as px

import numpy as np
import pandas as pd
import plotly.express as px

import plotly.graph_objects as go
import numpy as np

if corriente_total is not None:
    corriente_total["timestamp"] = pd.to_datetime(corriente_total["timestamp"])

    corriente_total["dia_semana"] = corriente_total["timestamp"].dt.day_name()
    corriente_total["hora"] = corriente_total["timestamp"].dt.hour

    dias_orden = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    horas = list(range(24))

    base = pd.MultiIndex.from_product([dias_orden, horas], names=["dia_semana", "hora"]).to_frame(index=False)

    heatmap_data = (
        corriente_total.groupby(["dia_semana", "hora"])["valor"]
        .mean()
        .reset_index()
    )

    heatmap_full = base.merge(heatmap_data, on=["dia_semana", "hora"], how="left").fillna(0)
    heatmap_full["dia_semana"] = pd.Categorical(heatmap_full["dia_semana"], categories=dias_orden, ordered=True)
    heatmap_full = heatmap_full.sort_values(["hora", "dia_semana"])

    heatmap_pivot = heatmap_full.pivot(index="hora", columns="dia_semana", values="valor")

    z = heatmap_pivot.values
    x = heatmap_pivot.columns.tolist()
    y = heatmap_pivot.index.tolist()

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=x,
            y=y,
            colorscale='Reds',
            showscale=True,
            hoverongaps=False,
            # Para hacer bordes se usa la propiedad 'line' dentro de 'go.Heatmap'
            # Sin embargo, Heatmap no soporta 'line' directamente, por eso hacemos workaround con 'xgap' y 'ygap'
        )
    )

    # Esta es la manera para "simular" bordes: usar xgap y ygap para separar celdas
    fig.update_traces(xgap=1, ygap=1)

    fig.update_layout(
        yaxis_autorange='reversed',
        xaxis_title='Día de la Semana',
        yaxis_title='Hora del Día',
        title='Mapa de calor: Corriente por Día de la Semana y Hora'
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.write("No hay suficientes datos para el mapa de calor.")







