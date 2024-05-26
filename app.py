from flask import Flask, render_template, request
from pymongo import MongoClient
import pandas as pd

app = Flask(__name__)

# Conexión a MongoDB Atlas
client = MongoClient("mongodb+srv://beatriz:hola@cluster0.ibx7qtt.mongodb.net/?retryWrites=true&appName=Cluster0")
db = client["calidad_aire"]
collection_estacions = db["estaciones"]
collection_contaminacio = db["contaminantes"]
collection_dades = db["datos"]

# Cargar datos desde CSV
estacions_data = pd.read_csv("qualitat_aire_estacions.csv")
dades_data = pd.read_csv("qualitat_aire_dades.csv")
contaminacio_data = pd.read_csv("qualitat_aire_contaminants.csv")

# Importar datos de CSV a MongoDB Atlas
def import_data_to_mongodb():
    global estacions_data, dades_data, contaminacio_data
    # Importar datos de estaciones
    estacions_data_dict = estacions_data.to_dict(orient="records")
    collection_estacions.insert_many(estacions_data_dict)

    # Importar datos de contaminación
    contaminacion_data_dict = contaminacio_data.to_dict(orient="records")
    collection_contaminacio.insert_many(contaminacion_data_dict)

    # Importar datos de dades
    collection_dades_dict = dades_data.to_dict(orient="records")
    collection_dades.insert_many(collection_dades_dict)

# Ruta para mostrar el formulario de consulta
@app.route('/')
def index():
    # Obtener todos los barrios disponibles
    barrios = collection_estacions.distinct("Nom_barri")
    return render_template('consulta.html', barrios=barrios)

# Ruta para manejar la solicitud del formulario y mostrar los datos de contaminación
@app.route('/resultados', methods=['POST'])
def get_results():
    barrio = request.form['barrio']
    dia = int(request.form['dia'])
    estacion = estacions_data[estacions_data["Nom_barri"] == barrio].iloc[0]
    
    # Filtrar los datos de contaminación para la estación y el día seleccionados
    datos_contaminacion = dades_data[(dades_data["ESTACIO"] == estacion["Estacio"]) & (dades_data["DIA"] == dia)]

    return render_template('resultados.html', datos_contaminacion=datos_contaminacion, dia=dia)

if __name__ == '__main__':
    import_data_to_mongodb()  # Importar datos al iniciar la aplicación
    app.run(debug=True)
