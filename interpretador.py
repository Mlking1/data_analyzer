import pyreadstat
import pandas as pd

# Ruta del archivo SPSS (.sav)
file_path = "BBDD Respuesta - Encuesta Jóvenes.sav"  # Asegúrate de tenerlo en el mismo directorio o usa la ruta completa

# Cargar datos y metadatos
df, meta = pyreadstat.read_sav(file_path)

# Extraer nombres de variables y sus etiquetas (descripciones)
variable_labels = meta.column_labels  # Descripción de cada variable
variable_names = meta.column_names  # Nombres originales de las variables

# Crear un DataFrame con los nombres y descripciones de las variables
variables_info = pd.DataFrame({"Variable": variable_names, "Descripción": variable_labels})

# Guardar el análisis en un archivo CSV para revisarlo
variables_info.to_csv("variables_info.csv", index=False)

# Mostrar las primeras filas
print(variables_info.head())
