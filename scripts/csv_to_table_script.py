import psycopg2
import pandas as pd
import os
import time
import dotenv

#Credenciales de conexión
dotenv.load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

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
    
        #Recorrer directorio parámetro
        for root, directorios, archivos in os.walk(path_carpeta):
            for archivo in archivos:
                #Abrir archivo
                nombre_tabla = os.path.splitext(archivo)[0]
                path_archivo = os.path.join(root, archivo)

                try:
                    data_reader = pd.read_csv(path_archivo)
                except Exception as e:
                    print(f"Error al intentar leer el archivo {archivo}: {e}.")
                    continue
                
                #Conversión de tipo
                if nombre_tabla in columnas_timestamp:
                    print(f"Corrigiendo tipos para la tabla: {nombre_tabla}")
                    for columna in columnas_timestamp[nombre_tabla]:
                        if columna in data_reader.columns:
                            data_reader[columna] = pd.to_datetime(data_reader[columna])
                        else:
                            print(f" La columna '{columna}' no se encontró en '{archivo}'.")

                #Monitoreo
                num_filas = len(data_reader)
                inicio_cronometro = time.time() 

                #Generación de query
                valores = [tuple(fila_valores) for fila_valores in data_reader.values] #Hace tupla (para psycopg2) cada fila de valores (arrays) en el dataset.
                columnas = ', '.join(data_reader.columns)
                placeholders = ', '.join(['%s'] * len(data_reader.columns)) #Pasa tantos valores como columnas
                query = f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({placeholders})"

                #Inserción
                try:
                    cursor.executemany(query, valores)
                    fin_cronometro = time.time()
                    conexion.commit()
                    print(f"Se completó la carga de {num_filas} filas para la tabla {nombre_tabla}, tardando {(fin_cronometro-inicio_cronometro)} segundos.")
                except Exception as e:
                    conexion.rollback()
                    print(f"Error al cargar datos para la tabla {nombre_tabla} desde {archivo}: {e}. Cambios revertidos")
                
    except Exception as e:
        print(f"Error: {e}")  

    finally:
        #Cierre
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
        print("Conexión cerrada. Fin del proceso.")

if __name__ == "__main__":
    cargar_datos(".")