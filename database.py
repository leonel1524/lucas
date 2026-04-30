import sqlite3
import os

def crear_base_de_datos():
    # En Docker, todo vive en /app. 
    # Esta ruta se asegura de usar la carpeta que SÍ está conectada a tu Mac.
    ruta_db = '/app/data/finanzas.db'
    
    # Creamos la carpeta data dentro de /app si no existe
    if not os.path.exists('/app/data'):
        os.makedirs('/app/data')
        
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    # Tabla Categorías
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            tipo TEXT CHECK(tipo IN ('INGRESO', 'EGRESO'))
        )
    ''')

    # Tabla Movimientos Actualizada
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            referencia TEXT UNIQUE,
            descripcion TEXT,
            monto_original REAL,
            moneda TEXT DEFAULT 'VES',
            tasa_cambio REAL,
            monto_usd REAL,
            tipo TEXT,
            categoria_id INTEGER,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        )
    ''')

    # Insertar categorías por defecto si la tabla está vacía
    categorias_default = [
        ('Sueldo', 'INGRESO'),
        ('Alimentación', 'EGRESO'),
        ('Servicios', 'EGRESO'),
        ('Transferencia', 'EGRESO'),
        ('Otros', 'EGRESO')
    ]
    cursor.executemany('INSERT OR IGNORE INTO categorias (nombre, tipo) VALUES (?, ?)', categorias_default)

    conn.commit()
    conn.close()
    print("Base de datos preparada con éxito....")

if __name__ == "__main__":
    crear_base_de_datos()