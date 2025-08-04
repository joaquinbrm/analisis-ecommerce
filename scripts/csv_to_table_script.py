import psycopg2
import pandas as pd
import os
import time
import dotenv
import numpy as np

# Credenciales de conexión
dotenv.load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

# Diccionario de columnas de timestamp por tabla
columnas_timestamp = {
    'order_all': [ 
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ],
    'order_items': [
        'shipping_limit_date'
    ],
    'order_reviews': [
        'review_creation_date',
        'review_answer_timestamp'
    ]
}

prioridad_carga_tablas = [
    'customers',
    'sellers',
    'products',
    'order_all',
    'order_items',
    'order_payments',
    'order_reviews', 
    'translations',  
    'geolocation'      
]


def conectar_db():
    """Conecta el script a la database.
        
        Notas: 
            - Utiliza el método connect de psycopg2. 
            - Modificar parámteros de conexión desde variables globales."""
    
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT)

#Pandas lee como float las columnas que son timestamp. Se agrega el diccionario para evitar error de tipo.
columnas_timestamp = { 'order': [
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'],
                        'order_items': [
        'shipping_limit_date'],
                        'order_reviews' : [
        'review_creation_date',
        'review_answer_timestamp']}

def cargar_datos(path_carpeta : str):
    """ Ingresa datos desde archivos csv a tablas en PostgreSQL.

    Parámetros:
        path_carpeta (str): Ruta a la carpeta con los csv.

    Requiere:
        - Las tablas en PostgreSQL deben existir previamente.
        - Las tablas tienen el mismo nombre que sus archivos.

    Notas:
        - Si se ejecuta desde main se usa la carpeta actual (el parámetro path_carpeta es ".").
        - Se realiza un commit al finalizar la carga de cada archivo. """
    
    #Conexión
    conexion = None
    cursor = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        print("Conexión establecida.")
    
        # Listar csvs
        archivos_en_carpeta = [f for f in os.listdir(path_carpeta) if f.endswith('.csv')]
        print(f"Archivos CSV detectados en '{path_carpeta}': {archivos_en_carpeta}")
        
        # Diccionario de paths
        archivos_por_nombre_tabla = {os.path.splitext(f)[0]: os.path.join(path_carpeta, f) for f in archivos_en_carpeta}

        # Recorrer según prioridad
        for nombre_tabla in prioridad_carga_tablas:
            if nombre_tabla not in archivos_por_nombre_tabla:
                print(f"El archivo {nombre_tabla}.csv no se encontró en la carpeta. Salteando.")
                continue

            path_archivo = archivos_por_nombre_tabla[nombre_tabla]
            archivo = os.path.basename(path_archivo) # Solo el nombre

            try:
                #Lectura
                data_reader = pd.read_csv(path_archivo)
                
                #Conversión de tipos
                if nombre_tabla in columnas_timestamp:
                    print(f"Pre-procesando columnas de timestamp para la tabla: {nombre_tabla}")
                    for col_timestamp in columnas_timestamp[nombre_tabla]:
                        if col_timestamp in data_reader.columns:
                            data_reader[col_timestamp] = pd.to_datetime(data_reader[col_timestamp], errors='coerce')
                            data_reader[col_timestamp] = data_reader[col_timestamp].replace({pd.NaT: None})

            except Exception as e:
                print(f"Error al intentar leer el archivo {archivo}: {e}.")
                continue 

            # Monitoreo
            num_filas = len(data_reader)
            inicio_cronometro = time.time() 

            # Generación de query
            valores = [tuple(fila_valores) for fila_valores in data_reader.values] 
            columnas = ', '.join(data_reader.columns)
            placeholders = ', '.join(['%s'] * len(data_reader.columns)) 
            query = f"INSERT INTO {nombre_tabla}({columnas}) VALUES ({placeholders})"

            try:
                #Carga
                cursor.executemany(query, valores)
                fin_cronometro = time.time()
                print(f"Se completó la carga de {num_filas} filas para la tabla {nombre_tabla}, tardando {(fin_cronometro-inicio_cronometro)} segundos.")

            except Exception as e:
                print(f"Error al cargar datos para la tabla {nombre_tabla} desde {archivo}: {e}.")
                raise 
        
        conexion.commit()

    except Exception as e:
        print(f"Error: {e}.")
        conexion.rollback()
        print("Cambios revertidos.")

    finally:
        # Cierre
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
        print("Conexión cerrada. Fin del proceso.")

if __name__ == "__main__":
    cargar_datos(".")