import streamlit as st
import pandas as pd
import plotly.express as px
from data_client import REM20Client
from data_processor import REM20Processor

# ==============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
# ==============================================================================
st.set_page_config(
    page_title="HospitHealth | Chile Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar estilos CSS personalizados para efecto Glassmorphism y temas
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ==============================================================================
# 2. ENCABEZADO Y CONTEXTO
# ==============================================================================
st.markdown("""
<div class='glass-card'>
    <h1>Hospital REM 20 Chile | Dashboard Analítico</h1>
    <p style='color: #bdc3c7;'>Monitoreo de indicadores de hospitalización, gestión de camas y resultados asistenciales.</p>
</div>
""", unsafe_allow_html=True)

# Sección de contexto colapsable (Inicio)
with st.expander("ℹ️ Contexto y Origen de los Datos"):
    st.markdown("""
    ## Contexto y propósito del dataset
    El recurso **“Indicadores_REM20”** del portal Datos.gob.cl corresponde a un conjunto de **indicadores mensuales del proceso de hospitalización**, reportados por establecimientos del sistema público.
    Este dataset actúa como una **tabla de hechos** de productividad/uso de camas, con granularidad **mensual**.

    ---
    ## Origen operacional (REM 20)
    REM 20 es un sistema de reporte que se alimenta desde el **censo diario de camas y pacientes**, consolidando la información con **periodicidad mensual**. Esto explica las variables en “días-cama” y los cocientes derivados.
    """)

# ==============================================================================
# 3. BARRA LATERAL (FILTROS)
# ==============================================================================
st.sidebar.header("🏥 Filtros de Análisis")

# Selección de Periodo (Año)
# Se ordenan de forma descendente para mostrar primero los años más recientes.
available_years = sorted(list(range(2014, 2026)), reverse=True)
selected_period = st.sidebar.multiselect(
    "Periodo (Año)", 
    options=available_years, 
    default=[2025] # Por defecto mostramos el año actual/más reciente
)

# ==============================================================================
# 4. CARGA Y PROCESAMIENTO DE DATOS
# ==============================================================================
# Instanciamos el cliente de API y solicitamos los datos solo para los años seleccionados.
client = REM20Client()
raw_df = client.fetch_data(periods=tuple(selected_period))

if not raw_df.empty:
    # Procesamiento: Limpieza y cálculo de indicadores
    processor = REM20Processor()
    df = processor.clean_data(raw_df)
    df = processor.calculate_indicators(df)

    # Filtros adicionales dependientes de los datos cargados
    selected_sss = st.sidebar.selectbox(
        "Servicio de Salud / Seremi", 
        options=["Todos"] + list(df['GLOSA_SSS'].unique())
    )
    selected_area = st.sidebar.selectbox(
        "Área Funcional", 
        options=["Todas"] + list(df['AREA_FUNCIONAL'].unique())
    )

    # Aplicación de filtros al DataFrame
    filtered_df = df.copy()
    if selected_sss != "Todos":
        filtered_df = filtered_df[filtered_df['GLOSA_SSS'] == selected_sss]
    if selected_area != "Todas":
        filtered_df = filtered_df[filtered_df['AREA_FUNCIONAL'] == selected_area]

    # ==============================================================================
    # 5. VISUALIZACIÓN DE KPIs (MÉTRICAS CLAVE)
    # ==============================================================================
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_occupancy = filtered_df['INDICE_OCUPACIONAL'].mean()
        st.metric("Índice Ocupacional", f"{avg_occupancy:.1f}%")
        
    with col2:
        total_egresos = filtered_df['NUMERO_EGRESOS'].sum()
        st.metric("Total Egresos", f"{int(total_egresos):,}")
        
    with col3:
        avg_stay = filtered_df['PROMEDIO_DIAS_ESTADA'].mean()
        st.metric("Promedio Estada", f"{avg_stay:.1f} días")
        
    with col4:
        # Cálculo de letalidad global ponderada
        total_deaths = filtered_df['EGRESOS_FALLECIDOS'].sum()
        letalidad = (total_deaths / total_egresos * 100) if total_egresos > 0 else 0
        st.metric("Tasa Letalidad", f"{letalidad:.2f}%")

    # ==============================================================================
    # 6. SECCIÓN DE GRÁFICOS (FILA 1)
    # ==============================================================================
    st.markdown("### 📊 Análisis de Tendencias y Distribución")
    
    # Mapa de métricas para el selector dinámico
    metrics_map = {
        "Índice Ocupacional (%)": "INDICE_OCUPACIONAL",
        "Promedio Días Estada": "PROMEDIO_DIAS_ESTADA",
        "Tasa de Letalidad (%)": "LETALIDAD",
        "Total Egresos": "NUMERO_EGRESOS",
        "Días Cama Disponibles": "DIAS_CAMAS_DISPONIBLES",
        "Días Cama Ocupadas": "DIAS_CAMAS_OCUPADAS"
    }

    vcol1, vcol2 = st.columns([2, 1])

    # GRÁFICO 1: Tendencias Temporales (Línea)
    with vcol1:
        # Selector de métrica
        selected_metric_label = st.selectbox(
            "Seleccionar Indicador para Tendencia:", 
            options=list(metrics_map.keys())
        )
        selected_metric = metrics_map[selected_metric_label]

        # Agrupación por mes para la serie de tiempo
        trend_df = filtered_df.groupby(['PERIODO', 'MES'])[selected_metric].mean().reset_index()
        # Crear columna de fecha ficticia (día 1) para que plotly entienda el eje X temporal
        trend_df['Fecha'] = pd.to_datetime(trend_df['PERIODO'].astype(str) + '-' + trend_df['MES'].astype(str) + '-01')
        
        fig_trend = px.line(
            trend_df, 
            x='Fecha', 
            y=selected_metric, 
            title=f'Evolución: {selected_metric_label}',
            line_shape='spline',
            color_discrete_sequence=['#7d5fff']
        )
        fig_trend.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=60, b=40),
            yaxis_title=selected_metric_label
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # GRÁFICO 2: Distribución por Área (Donut Chart)
    with vcol2:
        area_dist = filtered_df.groupby('AREA_FUNCIONAL')['NUMERO_EGRESOS'].sum().reset_index()
        area_dist = area_dist.sort_values('NUMERO_EGRESOS', ascending=False)
        
        # Agrupación de categorías menores en "Otros" para limpieza visual
        total_e = area_dist['NUMERO_EGRESOS'].sum()
        threshold = 0.03 * total_e # Umbral del 3%
        mask = area_dist['NUMERO_EGRESOS'] < threshold
        
        if mask.any():
            otros_val = area_dist.loc[mask, 'NUMERO_EGRESOS'].sum()
            area_dist = area_dist.loc[~mask].copy()
            otros_row = pd.DataFrame({'AREA_FUNCIONAL': ['Otros'], 'NUMERO_EGRESOS': [otros_val]})
            area_dist = pd.concat([area_dist, otros_row], ignore_index=True)

        fig_pie = px.pie(
            area_dist, 
            values='NUMERO_EGRESOS', 
            names='AREA_FUNCIONAL', 
            title='Egresos por Área',
            hole=.3, 
            color_discrete_sequence=px.colors.sequential.Electric
        )
        
        fig_pie.update_layout(
            height=550,
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=50, b=150),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.1,
                xanchor="center",
                x=0.5,
                font=dict(size=10)
            )
        )
        fig_pie.update_traces(
            textposition='inside', 
            textinfo='percent',
            insidetextfont=dict(size=12)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ==============================================================================
    # 7. SECCIÓN DE GRÁFICOS (FILA 2)
    # ==============================================================================
    st.markdown("### 🏥 Desempeño por Establecimiento")
    
    # Ranking top 10 por ocupación
    est_df = filtered_df.groupby('ESTABLECIMIENTO')[['INDICE_OCUPACIONAL', 'LETALIDAD']].mean()
    est_df = est_df.sort_values('INDICE_OCUPACIONAL', ascending=True).tail(10).reset_index()
    
    # Gráfico de barras horizontal
    fig_bar = px.bar(
        est_df, 
        y='ESTABLECIMIENTO', 
        x='INDICE_OCUPACIONAL', 
        color='LETALIDAD',
        orientation='h',
        title='Top 10 Establecimientos con Mayor Ocupación',
        labels={'INDICE_OCUPACIONAL': 'Índice Ocupacional (%)', 'ESTABLECIMIENTO': ''},
        color_continuous_scale='Viridis'
    )
    
    fig_bar.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[0, 100]), 
        margin=dict(l=50, r=50, t=50, b=50)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ==============================================================================
    # 8. TABLAS DE DATOS Y DOCUMENTACIÓN
    # ==============================================================================
    
    # Tabla de datos crudos (Muestra)
    with st.expander("🔍 Ver Datos Crudos (Muestra)"):
        st.dataframe(filtered_df.head(100), use_container_width=True)

    # Documentación Técnica (Diccionario)
    with st.expander("📚 Diccionario de Datos y Fórmulas"):
        st.markdown("""
        ## Diccionario de datos operativo (relevante para análisis)
        
        | Campo | Rol | Descripción de negocio |
        | :--- | :--- | :--- |
        | **PERIODO** | Dimensión tiempo | Año del registro. |
        | **MES** | Dimensión tiempo | Mes del registro (1–12). |
        | **COD_SSS / GLOSA_SSS** | Dimensión organizacional | Código y nombre del Servicio de Salud/Seremi. |
        | **ESTABLECIMIENTO** | Dimensión establecimiento | Nombre del establecimiento. |
        | **AREA_FUNCIONAL** | Dimensión funcional | Nombre del área funcional clínica. |
        | **DIAS_CAMAS_DISPONIBLES** | Métrica base | Suma diaria de camas disponibles en el mes. |
        | **DIAS_CAMAS_OCUPADAS** | Métrica base | Suma diaria de camas ocupadas (pacientes-día). |
        | **NUMERO_EGRESOS** | Métrica base | Total de egresos del mes. |
        | **PROMEDIO_DIAS_ESTADA** | Indicador derivado | Promedio de días de estada por paciente egresado. |
        | **INDICE_OCUPACIONAL** | Indicador derivado | Porcentaje de ocupación mensual (uso del recurso cama). |
        | **LETALIDAD** | Indicador derivado | Porcentaje de egresos fallecidos sobre egresos totales. |

        ---

        ## Definiciones y fórmulas recomendadas
        *   **Promedio Camas Disponibles** = Días-cama disponibles / Días del mes.
        *   **Índice Ocupacional** = (Días-cama ocupadas / Días-cama disponibles) * 100.
        *   **Promedio Días Estada** = Días de estada / Egresos.
        *   **Letalidad** = (Egresos fallecidos / Egresos) * 100.
        """)

else:
    # Manejo de error si la API no devuelve datos
    st.warning("No se pudieron cargar los datos de la API. Verifique la conexión o intente con otro periodo.")
