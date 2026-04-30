import streamlit as st
import pandas as pd
import re
import sqlite3
from datetime import datetime

# Configuración inicial
st.set_page_config(page_title="Finanzas Lucas", page_icon="🇻🇪", layout="wide")

# Función para conectar a la DB (Ruta absoluta para Docker)
def conectar_db():
    return sqlite3.connect('/app/data/finanzas.db')

# Obtener categorías para el formulario
def obtener_categorias():
    conn = conectar_db()
    df_cat = pd.read_sql_query("SELECT id, nombre FROM categorias", conn)
    conn.close()
    return df_cat

# Guardar en la DB
def guardar_movimientos_db(df, tasa, categoria_id):
    conn = conectar_db()
    cursor = conn.cursor()
    exitos = 0
    duplicados = 0
    
    for _, row in df.iterrows():
        monto_bs = row['Monto']
        monto_usd = round(abs(monto_bs) / tasa, 2)
        tipo = 'DEBITO' if monto_bs < 0 else 'CREDITO'
        
        try:
            cursor.execute('''
                INSERT INTO movimientos 
                (fecha, referencia, descripcion, monto_original, moneda, tasa_cambio, monto_usd, tipo, categoria_id)
                VALUES (?, ?, ?, ?, 'VES', ?, ?, ?, ?)
            ''', (row['Fecha'], row['Referencia'], row['Descripción'], monto_bs, tasa, monto_usd, tipo, categoria_id))
            exitos += 1
        except sqlite3.IntegrityError:
            duplicados += 1
            
    conn.commit()
    conn.close()
    return exitos, duplicados

# --- INTERFAZ ---
st.title("🏦 Control de Finanzas Personales")

# Sidebar para configuración global
st.sidebar.header("Configuración del Día")
tasa_dia = st.sidebar.number_input("Tasa BCV / Cambio:", min_value=1.0, value=36.5, step=0.01)

# Selección de categoría
df_cat = obtener_categorias()
cat_opciones = {row['nombre']: row['id'] for _, row in df_cat.iterrows()}
categoria_sel = st.sidebar.selectbox("Categoría predeterminada:", options=list(cat_opciones.keys()))

st.divider()

# Área de entrada
texto_input = st.text_area("Pega aquí el texto del banco:", height=150)

if st.button("🔍 Analizar Texto"):
    if texto_input:
        patron = r"(\d{2}-\d{2}-\d{4} \d{2}:\d{2})(\d{10,})(\D+)(DEBITO|CREDITO)([\d.,-]+)\s*Bs\.([\d.,]+)\s*Bs\."
        movimientos = re.findall(patron, texto_input)
        
        if movimientos:
            lista = []
            for mov in movimientos:
                fecha, ref, desc, tipo, monto, saldo = mov
                m_limpio = float(monto.replace('.', '').replace(',', '.'))
                lista.append({"Fecha": fecha, "Referencia": ref, "Descripción": desc.strip(), "Monto": m_limpio})
            
            df_temp = pd.DataFrame(lista)
            st.session_state['df_temp'] = df_temp # Guardamos en sesión
            st.write(f"Se encontraron **{len(df_temp)}** movimientos:")
            st.table(df_temp)
        else:
            st.error("No se detectó el formato. Verifica el texto.")

# Botón para confirmar guardado
if 'df_temp' in st.session_state:
    if st.button(f"💾 Guardar en Base de Datos (Tasa: {tasa_dia})"):
        id_cat = cat_opciones[categoria_sel]
        ok, ups = guardar_movimientos_db(st.session_state['df_temp'], tasa_dia, id_cat)
        
        st.success(f"Proceso terminado: {ok} guardados correctamente.")
        if ups > 0:
            st.warning(f"{ups} movimientos fueron ignorados por estar duplicados (misma referencia).")
        
        # Limpiar la sesión para evitar guardar dos veces
        del st.session_state['df_temp']

st.divider()
st.subheader("Últimos movimientos registrados")
conn = conectar_db()
# Mostramos los últimos 10
df_recientes = pd.read_sql_query("SELECT fecha, descripcion, monto_original as 'Bs', monto_usd as '$', tasa_cambio FROM movimientos ORDER BY id DESC LIMIT 10", conn)
st.dataframe(df_recientes, use_container_width=True)
conn.close()