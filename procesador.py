import re
import pandas as pd

def procesar_texto_bancario(texto_crudo):
    # 1. Definimos el "patrón" de lo que buscamos:
    # Fecha (DD-MM-AAAA HH:mm) + Referencia + Descripción + Tipo + Monto + Saldo
    # Esta expresión regular busca: Fecha, Número largo, Texto, DEBITO/CREDITO, y montos con Bs.
    patron = r"(\d{2}-\d{2}-\d{4} \d{2}:\d{2})(\d{10,})(\D+)(DEBITO|CREDITO)([\d.,-]+)\s*Bs\.([\d.,]+)\s*Bs\."
    
    movimientos = re.findall(patron, texto_crudo)
    
    lista_final = []
    for mov in movimientos:
        fecha, ref, desc, tipo, monto, saldo = mov
        
        # Limpieza de números: Convertimos "23.376,00" a un float de Python 23376.00
        monto_limpio = float(monto.replace('.', '').replace(',', '.'))
        saldo_limpio = float(saldo.replace('.', '').replace(',', '.'))
        
        lista_final.append({
            "Fecha": fecha,
            "Referencia": ref,
            "Descripcion": desc.strip(),
            "Tipo": tipo,
            "Monto": monto_limpio,
            "Saldo": saldo_limpio
        })
    
    return lista_final

# --- PRUEBA DEL PROGRAMA ---
texto_del_banco = """29-04-2026 19:430027256738754COMISION PAGOMOVILBDVDEBITO-23,38 Bs.42.278,08 Bs."""

datos = procesar_texto_bancario(texto_del_banco)

# Convertimos a un DataFrame de Pandas (es como una tabla de base de datos en memoria)
df = pd.DataFrame(datos)

# Exportamos a Excel
df.to_excel("Mis_Movimientos.xlsx", index=False)
print("¡Archivo Excel creado con éxito!")