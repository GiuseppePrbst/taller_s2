import requests
import pandas as pd
import streamlit as st
import json

class REM20Client:
    """
    Cliente API para interactuar con la plataforma CKAN de Datos Abiertos (datos.gob.cl).
    Responsable de la extracción de datos del reporte de indicadores hospitalarios REM 20.
    """
    # Endpoint base para consultas al datastore de CKAN
    BASE_URL = "https://datos.gob.cl/api/3/action/datastore_search"
    # ID único del recurso (dataset) en el portal de datos
    RESOURCE_ID = "657cc933-eac8-4bfc-b004-c4d6dcd988a8"

    def __init__(self):
        self.resource_id = self.RESOURCE_ID

    @st.cache_data(show_spinner="Obteniendo datos desde la API...")
    def fetch_data(_self, periods=None, limit=50000, timeout=30):
        """
        Extrae datos desde la API de Gobierno con paginación automática y control de errores.
        
        Args:
            periods (tuple/list): Años a consultar (ej. (2024, 2025)).
            limit (int): Registros por página (default 50.000).
            timeout (int): Segundos máximos de espera por petición.
        
        Returns:
            pd.DataFrame: DataFrame consolidado con todos los registros.
        """
        all_dfs = []
        fetch_list = periods if periods else [None]

        headers = {"User-Agent": "HospitHealth-REM20-Streamlit/1.0"}

        for period in fetch_list:
            offset = 0
            total = None

            while True:
                params = {
                    "resource_id": _self.resource_id,
                    "limit": limit,
                    "offset": offset
                }

                if period is not None:
                    # Filtro por año (PERIODO)
                    params["filters"] = json.dumps({"PERIODO": str(period)})

                try:
                    response = requests.get(_self.BASE_URL, params=params, headers=headers, timeout=timeout)
                    response.raise_for_status()
                    data = response.json()

                    if not data.get("success"):
                        break

                    result = data.get("result", {})
                    records = result.get("records", [])
                    total = result.get("total", total)

                    if records:
                        all_dfs.append(pd.DataFrame(records))

                    # Si no hay registros, salimos del loop
                    if not records:
                        break

                    # Actualizamos offset para la siguiente página
                    offset += len(records)

                    # Si ya trajimos todo el total reportado, terminamos
                    if total is not None and offset >= total:
                        break

                except requests.exceptions.RequestException as e:
                    st.error(f"Error al conectar con la API para el periodo {period}: {e}")
                    break

        if all_dfs:
            return pd.concat(all_dfs, ignore_index=True)

        return pd.DataFrame()

if __name__ == "__main__":
    # Prueba rápida de ejecución directa
    client = REM20Client()
    test_df = client.fetch_data(periods=[2025], limit=10)
    print(test_df.head())
