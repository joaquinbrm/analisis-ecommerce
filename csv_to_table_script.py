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

def cargar_datos(path_carpeta : str):
    """ Ingresa datos desde archivos csv a tablas en PostgreSQL.

    Parámetros:
        path_carpeta (str): Ruta a la carpeta con los csv.

    Requiere:
        - Las tablas en PostgreSQL deben existir previamente.
        - Las tablas tienen el mismo nombre que sus archivos (que no tienen la extensión ".csv")

    Notas:
        - Si se ejecuta desde main se usa la carpeta actual (el parámetro path_carpeta es ".").
        - Se realiza un commit al finalizar la carga de cada archivo. """
    
    #Conexión
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        print("Conexión establecida.")
    except:
        print("Conexión fallida.")
    
    #Recorrer directorio parámetro
    for root, directorios, archivos in os.walk(path_carpeta):
        for archivo in archivos:
            #Abrir archivo
            nombre_tabla = os.path.splitext(archivo)[0]
            path_archivo = os.path.join(root, archivo)
            data_reader = pd.read_csv(path_archivo)

            #Monitoreo
            num_filas = len(data_reader)
            inicio_cronometro = time.time() 

            #Generación de query
            valores = [tuple(fila_valores) for fila_valores in data_reader.values] #Hace tupla (para psycopg2) cada fila de valores (arrays) en el dataset.
            columnas = ', '.join(data_reader.columns)
            placeholders = ', '.join(['%s'] * len(data_reader.columns)) #Pasa tantos valores como columnas
            query = f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({placeholders})"

            cursor.executemany(query, valores)

            fin_cronometro = time.time()

            conexion.commit()
            print(f"Se completó la carga de {num_filas} filas para la tabla {nombre_tabla}, tardando {(fin_cronometro-inicio_cronometro)} segundos.")
                
    #Cierre
    cursor.close()
    conexion.close()
    print("Conexión cerrada. Fin del proceso.")

if __name__ == "__main__":
    cargar_datos(".")