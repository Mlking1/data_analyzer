import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import openai
import pyreadstat
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QLabel, QListWidget, QAbstractItemView, QDialog, QTextEdit

class DataAnalyzerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.df = None  # DataFrame de datos cargados
        self.variable_descriptions = {}  # Diccionario para almacenar descripciones de variables
        self.name_to_description = {}  # Diccionario de nombres de variables a descripciones

        # 🔹 API Key de OpenAI
        self.api_key = "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" # Reemplázalo con tu API Key
        
        
        self.initUI()

    def initUI(self):
        """ Configuración de la interfaz gráfica """
        self.setWindowTitle("Analizador de Datos con IA")
        self.setGeometry(100, 100, 600, 500)

        layout = QVBoxLayout()

        # Botón para cargar archivo
        self.btnLoad = QPushButton("Cargar Archivo")
        self.btnLoad.clicked.connect(self.load_file)
        layout.addWidget(self.btnLoad)

        # Lista de variables disponibles
        self.labelVars = QLabel("Selecciona Variables:")
        layout.addWidget(self.labelVars)

        self.varList = QListWidget()
        self.varList.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        layout.addWidget(self.varList)

        # Botón para analizar correlaciones
        self.btnAnalyze = QPushButton("Analizar Correlaciones")
        self.btnAnalyze.clicked.connect(self.analyze_data)
        layout.addWidget(self.btnAnalyze)

        self.setLayout(layout)

    def load_file(self):
        """ Cargar un archivo CSV, Excel o SPSS """
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo", "", 
                                                   "CSV Files (*.csv);;Excel Files (*.xlsx);;SPSS Files (*.sav)")

        if file_path:
            try:
                if file_path.endswith(".csv"):
                    self.df = pd.read_csv(file_path)
                    self.variable_descriptions = {col: col for col in self.df.columns}  # Sin descripción en CSV

                elif file_path.endswith(".xlsx"):
                    self.df = pd.read_excel(file_path)
                    self.variable_descriptions = {col: col for col in self.df.columns}  # Sin descripción en Excel

                elif file_path.endswith(".sav"):
                    self.df, meta = pyreadstat.read_sav(file_path)

                    # 🟢 Usamos `column_labels` para mostrar la descripción correcta
                    self.variable_descriptions = dict(zip(meta.column_names, meta.column_labels))
                    self.name_to_description = {meta.column_labels[i]: meta.column_names[i] for i in range(len(meta.column_names))}

                self.varList.clear()
                for description in self.variable_descriptions.values():
                    self.varList.addItem(description)  # Muestra solo la descripción

                print("Archivo cargado:", file_path)

            except Exception as e:
                self.show_text_window("Error", f"No se pudo cargar el archivo: {str(e)}")

    def analyze_data(self):
        """ Analizar las correlaciones entre variables seleccionadas """
        if self.df is None:
            self.show_text_window("Error", "No hay archivo cargado.")
            return

        selected_descriptions = [item.text() for item in self.varList.selectedItems()]
        
        # Convertir descripciones a nombres de variable reales
        selected_vars = [self.name_to_description[desc] for desc in selected_descriptions if desc in self.name_to_description]

        if len(selected_vars) < 2:
            self.show_text_window("Error", "Seleccione al menos dos variables numéricas.")
            return

        try:
            df_selected = self.df[selected_vars].select_dtypes(include=[np.number])

            if df_selected.empty:
                self.show_text_window("Error", "Las variables seleccionadas no son numéricas.")
                return

            # Calcular correlaciones
            correlation_matrix = df_selected.corr()

            # Mostrar gráfico de correlaciones
            plt.figure(figsize=(8, 6))
            sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", linewidths=0.5)
            plt.title("Matriz de Correlación")
            plt.show(block=False)  # No bloquear la ejecución

            # Generar interpretación con IA
            self.interpret_with_ai(correlation_matrix, selected_descriptions)

        except Exception as e:
            self.show_text_window("Error", f"Error al analizar datos: {str(e)}")

    def interpret_with_ai(self, correlation_matrix, selected_descriptions):
        """ Interpretación de correlaciones con IA (GPT-4) """
        try:
            if not self.api_key:
                self.show_text_window("Error en IA", "No se ha configurado la API Key de OpenAI.")
                return
            
            descripcion = correlation_matrix.unstack().sort_values(ascending=False).drop_duplicates().head(10).to_string()

            # Reemplazar nombres de variables por sus descripciones en el texto
            for desc in selected_descriptions:
                var_name = self.name_to_description.get(desc, desc)
                descripcion = descripcion.replace(var_name, desc)

            prompt = f"Analiza las siguientes correlaciones en una encuesta sobre juventudes y ofrece insights clave:\n\n{descripcion}"

            # Nueva forma de llamada en OpenAI >=1.0.0 con API Key
            client = openai.OpenAI(api_key=self.api_key)

            respuesta = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "Eres un experto en análisis de datos."},
                {"role": "user", "content": prompt}]
            )

            resultado_ia = respuesta.choices[0].message.content
            print("\n*** Interpretación IA ***\n", resultado_ia)
            self.show_text_window("Interpretación IA", resultado_ia)

        except Exception as e:
            self.show_text_window("Error en IA", f"No se pudo generar la interpretación con IA: {str(e)}")

    def show_text_window(self, title, content):
        """ Mostrar una ventana con contenido de texto expandible """
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.resize(800, 600)  # Hace la ventana más grande

        layout = QVBoxLayout()

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(content)
        layout.addWidget(text_edit)

        dialog.setLayout(layout)
        dialog.exec()

# Ejecutar la aplicación
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DataAnalyzerApp()
    ex.show()
    sys.exit(app.exec())
