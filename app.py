import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="Extractor Bancario", page_icon="💰")

st.title("🏦 Procesador de Movimientos")
st.write("Pega el texto de tu banco aquí abajo para generar tu Excel.")

# Área de entrada de texto
texto_input = st.text_area("Datos del banco:", height=200, placeholder="29-04-2026...")

if st.button("Transformar datos"):
    if texto_input:
        # Reutilizamos tu lógica de extracción (RegEx)
        patron = r"(\d{2}-\d{2}-\d{4} \d{2}:\d{2})(\d{10,})(\D+)(DEBITO|CREDITO)([\d.,-]+)\s*Bs\.([\d.,]+)\s*Bs\."
        movimientos = re.findall(patron, texto_input)
        
        if movimientos:
            lista_final = []
            for mov in movimientos:
                fecha, ref, desc, tipo, monto, saldo = mov
                # Limpieza de números
                m_limpio = float(monto.replace('.', '').replace(',', '.'))
                s_limpio = float(saldo.replace('.', '').replace(',', '.'))
                
                lista_final.append({
                    "Fecha": fecha, "Referencia": ref, 
                    "Descripción": desc.strip(), "Tipo": tipo, 
                    "Monto": m_limpio, "Saldo": s_limpio
                })
            
            df = pd.DataFrame(lista_final)
            
            # Mostrar vista previa en la web
            st.subheader("Vista Previa")
            st.dataframe(df)
            
            # Crear el archivo Excel en memoria para descarga
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Movimientos')
            
            st.download_button(
                label="📥 Descargar Excel",
                data=output.getvalue(),
                file_name="movimientos_procesados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("No se encontraron movimientos. Revisa el formato del texto.")
    else:
        st.warning("Por favor, pega algún texto primero.")