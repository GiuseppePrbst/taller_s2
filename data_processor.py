import pandas as pd
import numpy as np

class REM20Processor:
    """
    Controlador encargado de la limpieza, transformación y enriquecimiento 
    de los datos de indicadores hospitalarios (REM 20).
    """
    
    @staticmethod
    def clean_data(df):
        """
        Realiza la limpieza inicial de los datos crudos provenientes de la API.
        
        Acciones:
        1. Convierte columnas numéricas a tipos apropiados.
        2. Normaliza códigos (añade ceros a la izquierda) para mantener integridad referencial.
        3. Maneja valores nulos (convirtiéndolos a 0 en métricas numéricas).
        
        Args:
            df (pd.DataFrame): DataFrame con datos crudos.
            
        Returns:
            pd.DataFrame: DataFrame limpio y tipificado.
        """
        if df.empty:
            return df
            
        cleaned_df = df.copy()
        
        # Lista de columnas que contienen métricas numéricas
        numeric_cols = [
            'DIAS_CAMAS_DISPONIBLES', 'DIAS_CAMAS_OCUPADAS', 'DIAS_ESTADA', 
            'NUMERO_EGRESOS', 'EGRESOS_FALLECIDOS', 'TRASLADOS',
            'PROMEDIO_CAMAS_DISPONIBLE', 'INDICE_OCUPACIONAL', 
            'PROMEDIO_DIAS_ESTADA', 'LETALIDAD', 'INDICE_ROTACION'
        ]
        
        # Conversión segura a numérico, forzando 0 en errores o nulos
        for col in numeric_cols:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce').fillna(0)
        
        # Normalización de Códigos: Asegurar formato string y ceros a la izquierda
        # SSS y Áreas suelen ser de 2 dígitos; Establecimientos de 6.
        code_cols = ['COD_SSS', 'CODIGO_ESTABLECIMIENTO', 'COD_AREA_FUNCIONAL']
        for col in code_cols:
            if col in cleaned_df.columns:
                padding = 2 if ('SSS' in col or 'AREA' in col) else 6
                cleaned_df[col] = cleaned_df[col].astype(str).str.zfill(padding)
        
        # Conversión de dimensiones temporales
        cleaned_df['PERIODO'] = pd.to_numeric(cleaned_df['PERIODO'], errors='coerce')
        cleaned_df['MES'] = pd.to_numeric(cleaned_df['MES'], errors='coerce')
        
        return cleaned_df

    @staticmethod
    def calculate_indicators(df):
        """
        Recalcula o verifica indicadores clave basándose en las métricas base.
        Esto asegura consistencia incluso si el cálculo origen tiene desviaciones.
        
        Args:
            df (pd.DataFrame): DataFrame con métricas base limpias.
            
        Returns:
            pd.DataFrame: DataFrame enriquecido con columnas de verificación.
        """
        df = df.copy()
        
        # Cálculo: Índice Ocupacional = (Días Ocupados / Días Disponibles) * 100
        # Se usa np.where para evitar división por cero.
        df['VERIF_INDICE_OCUPACIONAL'] = np.where(
            df['DIAS_CAMAS_DISPONIBLES'] > 0,
            (df['DIAS_CAMAS_OCUPADAS'] / df['DIAS_CAMAS_DISPONIBLES']) * 100,
            0
        )
        
        # Cálculo: Letalidad = (Fallecidos / Egresos Totales) * 100
        df['VERIF_LETALIDAD'] = np.where(
            df['NUMERO_EGRESOS'] > 0,
            (df['EGRESOS_FALLECIDOS'] / df['NUMERO_EGRESOS']) * 100,
            0
        )
        
        return df

if __name__ == "__main__":
    # Bloque para pruebas unitarias rápidas del procesador
    pass
