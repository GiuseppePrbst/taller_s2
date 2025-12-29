# Manual de Uso - HospitHealth Dashboard (Solemne II)

Este proyecto consiste en un dashboard interactivo desarrollado en Python y Streamlit para visualizar indicadores hospitalarios del sistema público de Chile (REM 20).

## 📋 Requisitos Previos

*   **Python 3.8** o superior instalado en el sistema.
*   Conexión a Internet (para descargar librerías y consultar la API de Datos Abiertos).

## 🚀 Instalación y Configuración

1.  **Descomprimir el proyecto** en una carpeta local.
2.  **Abrir una terminal** (PowerShell o CMD) en la carpeta del proyecto.
3.  **Crear un entorno virtual** (opcional pero recomendado):
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # En Windows
    # source venv/bin/activate  # En Mac/Linux
    ```
4.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Ejecución de la Aplicación

Para iniciar el dashboard, ejecuta el siguiente comando en la terminal:

```bash
streamlit run app.py
```

El navegador se abrirá automáticamente en `http://localhost:8501`.

## 💡 Guía de Uso del Dashboard

### 1. Barra Lateral de Filtros (Sidebar)
*   **Periodo (Año):** Selecciona uno o más años para analizar (por defecto 2025). La aplicación descargará automáticamente los datos de la API.
*   **Servicio de Salud / Seremi:** Filtra los datos por región administrativa.
*   **Área Funcional:** Filtra por especialidad clínica (ej. Pediatría, Obstetricia).

### 2. Métricas Clave (KPIs)
En la parte superior verás tarjetas con los indicadores generales consolidados según tus filtros:
*   Índice Ocupacional Promedio.
*   Total de Egresos.
*   Promedio de Días de Estada.
*   Tasa de Letalidad.

### 3. Visualizaciones Interactivas
*   **Análisis de Tendencias:** Gráfico de líneas temporal. **Usa el selector** encima del gráfico para cambiar la variable que deseas analizar (Ocupación, Letalidad, etc.).
*   **Egresos por Área:** Gráfico de anillo que muestra la distribución de pacientes por especialidad.
*   **Top 10 Establecimientos:** Ranking horizontal de los hospitales con mayor ocupación. El color indica la tasa de letalidad (colores más claros = mayor letalidad).

### 4. Documentación Integrada
Al final de la página, despliega la sección **"📚 Diccionario de Datos y Fórmulas"** para ver detalles técnicos sobre el origen de los datos, definiciones de variables y fórmulas de cálculo.
