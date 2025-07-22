import psycopg2
import csv
import pandas as pd
import os

#Credenciales de conexión
DB_HOST = 'localhost'
DB_NAME = 'ecommerce_db'
DB_USER = 'postgres'
DB_PASSWORD = 'ecommerceproject'
DB_PORT = '5432'

def conectar_db():
    """Conecta el script a la database.
    
        Utiliza el método connect de psycopg2. Modificar parámteros de conexión desde variables globales."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

def cargar_datos(path_carpeta : str):
    """Ingesta datos de un csv a una tabla en PostgreSQL
    
        Parámetros: path de carpeta con los csv.
        Requiere: las tablas tienen el mismo nombre que los csv"""
    for nombre_tabla in path_carpeta: #REVISAR
        #Conectar db y csv
        archivo = open(nombre_tabla, 'r')
        conex = conectar_db()
        cursor = conex.cursor()

        #Abre y lee el csv
        data_reader = pd.read_csv(archivo)
        next(data_reader) #Saltea def de columnas
        for fila in data_reader:
            cursor.execute("INSERT INTO"+nombre_tabla+"VALUES (%s, %s, %s)", fila) #REVISAR %s

        #Commitear y cerrar conexión
        conex.commit()
        cursor.close()
        conex.close()
        archivo.close()
        print('Se completó la carga de datos para la tabla'+nombre_tabla+'.')

if __name__ == "__main__":
    cargar_datos()