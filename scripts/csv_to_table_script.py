import psycopg2
import csv

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

path_csv = ''

def ingestar_datos():
    #Conectarse a db
    archivo_csv = open(path_csv, 'r')
    conex = conectar_db()
    cursor = conex.cursor()

    #Abre y lee el CSV
    data_reader = csv.reader(archivo_csv)
    next(data_reader) #Saltea def de columnas
    for fila in data_reader:
        cursor.execute("INSERT INTO ... VALUES (%s, %s, %s)", fila) #REVISAR: crear función para el string de la querie.

    #Commitear y cerrar conexión
    conex.commit()
    cursor.close()
    conex.close()
    archivo_csv.close()
    print('Los datos se ingestaron correctamente')

if __name__ == "__main__":
    ingestar_datos()