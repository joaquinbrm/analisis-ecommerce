import psycopg2
import pandas as pd
import os
import time

#Credenciales de conexión
DB_HOST = 'localhost'
DB_NAME = 'ecommerce_db'
DB_USER = 'postgres'
DB_PASSWORD = 'ecommerceproject'
DB_PORT = '5432'

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
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    #Iterar archivos del directorio parámetro
    for root, directorios, archivos in os.walk(path_carpeta):
        for archivo in archivos:
            #Abrir archivo
            path_archivo = os.path.join(root, archivo)
            data_reader = pd.read_csv(path_archivo)

            #Rendimiento
            inicio_cronometro = time.time() 
            filas_cargadas = 0

            #Carga fila por fila y generación de query
            for index, fila in data_reader.iterrows():
                placeholders = ', '.join(['%s'] * len(fila)) #Tantos valores como columnas
                columnas = ', '.join(fila.index)
                query = f"INSERT INTO {archivo} ({columnas}) VALUES ({placeholders})"

                cursor.execute(query, tuple(fila)) #Fila es una serie de pandas y el cursor requiere tuplas

                filas_cargadas += 1

            fin_cronometro = time.time()

            conexion.commit()
            print(f"Se completó la carga de {filas_cargadas} filas para la tabla {archivo}, tardando {(fin_cronometro-inicio_cronometro)} segundos.")

    #Cierre
    cursor.close()
    conexion.close()
    print("Fin del proceso. Conexión cerrada.")

if __name__ == "__main__":
    cargar_datos(".")