import streamlit as st
import pandas as pd
import difflib
import csv
from pathlib import Path

# Configuración
st.set_page_config(layout="wide", page_title="Traductor Voynich-Español")
st.title("🔠 Traductor Voynich-Español")

@st.cache_data
def load_data():
    try:
        data_path = Path("data/traducciones/traducciones.csv")
        if not data_path.exists():
            st.error("Archivo no encontrado. Usando datos de ejemplo.")
            return pd.DataFrame({
                "simbolo_eva": ["qokaiin", "chedy", "dar"],
                "posible_significado": ["fluir, conectar", "vena, conducto", "dar, administrar"],
                "confianza": [0.85, 0.90, 0.95],
                "ejemplo_uso": ["qokaiin chedy", "okal chedy", "dar s aiin"]
            })
        
        df = pd.read_csv(data_path, quoting=csv.QUOTE_ALL, escapechar="\\")
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return pd.DataFrame()

# Cargar datos
diccionario = load_data()

# Interfaz
col_input, col_results = st.columns([1, 3])

with col_input:
    simbolo = st.text_input("Ingresa un símbolo EVA:", key="busqueda", placeholder="Ej: chedy")
    simbolo_busqueda = simbolo.strip().lower() if simbolo else ""

with col_results:
    if simbolo_busqueda:
        with st.expander("ℹ️ Información de depuración", expanded=False):
            st.write(f"Valor buscado (normalizado): `{repr(simbolo_busqueda)}`")
            st.write(f"Valores en diccionario: {diccionario['simbolo_eva'].str.lower().unique()}")
        
        exact_match = diccionario[diccionario['simbolo_eva'].str.lower() == simbolo_busqueda]
        
        if not exact_match.empty:
            st.success("✅ **Resultado Exacto**")
            resultado = exact_match.iloc[0]
            st.markdown(f"""
            **Símbolo:** `{resultado['simbolo_eva']}`  
            **Significado:** {resultado['posible_significado']}  
            **Confianza:** {resultado['confianza']*100:.0f}%  
            **Ejemplo:** *{resultado.get('ejemplo_uso', 'N/A')}*
            """)
        else:
            st.warning("⚠️ No se encontró coincidencia exacta")
            matches = difflib.get_close_matches(
                simbolo_busqueda, 
                diccionario['simbolo_eva'].str.lower().tolist(), 
                n=3, 
                cutoff=0.6
            )
            
            if matches:
                st.info("🔍 **Coincidencias Aproximadas**")
                for match in matches:
                    match_data = diccionario[diccionario['simbolo_eva'].str.lower() == match].iloc[0]
                    with st.container(border=True):
                        st.markdown(f"""
                        **{match_data['simbolo_eva']}**:  
                        {match_data['posible_significado']}  
                        *Confianza: {match_data['confianza']*100:.0f}%*
                        """)

st.divider()
st.subheader("📚 Diccionario Completo")
st.dataframe(
    diccionario[["simbolo_eva", "posible_significado", "confianza"]],
    hide_index=True,
    use_container_width=True
)