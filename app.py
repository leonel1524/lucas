import streamlit as st
import pandas as pd
import re
import sqlite3
from datetime import datetime
from database import crear_base_de_datos
# Configuración inicial
crear_base_de_datos()
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
st.title("Lucas 🏦 Control de Finanzas Personales Para todos")

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

# ... (mantén tus funciones de conexión y guardado)

if st.button("🔍 Analizar Texto"):
    if texto_input:
        # Tu patrón de RegEx actual
        patron = r"(\d{2}-\d{2}-\d{4} \d{2}:\d{2})(\d{10,})(\D+)(DEBITO|CREDITO)([\d.,-]+)\s*Bs\.([\d.,]+)\s*Bs\."
        movimientos = re.findall(patron, texto_input)
        
        if movimientos:
            lista = []
            for mov in movimientos:
                fecha, ref, desc, tipo, monto, saldo = mov
                m_limpio = float(monto.replace('.', '').replace(',', '.'))
                # Guardamos la descripción original pero permitiremos editarla
                lista.append({
                    "Fecha": fecha, 
                    "Referencia": ref, 
                    "Descripción": desc.strip(), # Aquí es donde editarás
                    "Monto": m_limpio
                })
            
            # Guardamos en session_state para que no se borre al editar
            st.session_state['df_temp'] = pd.DataFrame(lista)
        else:
            st.error("No se detectó el formato.")

# Si hay datos analizados, mostramos el editor
if 'df_temp' in st.session_state:
    st.subheader("📝 Edita las descripciones antes de guardar...")
    st.info("Haz doble clic en la columna 'Descripción' para poner el nombre real del gasto (ej: 'Mercado Farmatodo').")
    
    # El data_editor permite modificar el DataFrame directamente
    df_editado = st.data_editor(
        st.session_state['df_temp'],
        column_config={
            "Fecha": st.column_config.TextColumn(disabled=True),
            "Referencia": st.column_config.TextColumn(disabled=True),
            "Monto": st.column_config.NumberColumn(disabled=True, format="%.2f Bs."),
            "Descripción": st.column_config.TextColumn(help="Escribe qué compraste realmente", width="large")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Botón para confirmar guardado usando los datos EDITADOS
    if st.button(f"💾 Guardar Movimientos con Descripciones Reales."):
        id_cat = cat_opciones[categoria_sel]
        # Pasamos df_editado en lugar de df_temp
        ok, ups = guardar_movimientos_db(df_editado, tasa_dia, id_cat)
        
        st.success(f"¡Listo! {ok} movimientos guardados.")
        if ups > 0:
            st.warning(f"{ups} ya existían.")
        
        del st.session_state['df_temp']
        st.rerun() # Refrescamos para ver los cambios abajo

st.divider()
st.subheader("Últimos movimientos registrados")
conn = conectar_db()
# Mostramos los últimos 10
df_recientes = pd.read_sql_query("SELECT fecha, descripcion, monto_original as 'Bs', monto_usd as '$', tasa_cambio FROM movimientos ORDER BY id DESC LIMIT 10", conn)
st.dataframe(df_recientes, use_container_width=True)
conn.close()