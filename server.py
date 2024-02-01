import os
from flask import Flask, send_from_directory, render_template, redirect,  request, jsonify
import math
from flask_cors import CORS 
import numpy as np
from regresion import calcular_regresion_lineal, calcular_sumatorias, calcularA, calcularB, predecir_y

app = Flask(__name__)
CORS(app, origins="*")
port = int(os.environ.get("PORT", 8080))

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/')
def home():
   return render_template('index.html')
@app.route('/hola')
def backend():
    return ('hola mundo')
@app.route('/<path:path>')
def all_routes(path):
    return redirect('/')

class Masa:
    def __init__(self, unidad, medidas, medida_maxima_instrumento):
        self.unidad = unidad
        self.medidas = medidas
        self.medida_maxima_instrumento = medida_maxima_instrumento

    def masa_promedio(self):
        if not self.medidas:
            return 0
        medidas_numeros = [float(medida) for medida in self.medidas]
        promedio = sum(medidas_numeros) / len(medidas_numeros)
        return promedio

    def calcular_lectura_minima(self):
        # Por ejemplo, la lectura mínima es el 1% de la medida máxima
        return 0.01 * self.medida_maxima_instrumento

    def error_instrumental(self):
        lectura_minima = self.calcular_lectura_minima()
        return lectura_minima / 2

    def error_estadistico(self):
        promedio = self.masa_promedio()
        error_cuadrado = sum((float(medida) - promedio) ** 2 for medida in self.medidas)
        return math.sqrt(error_cuadrado / len(self.medidas))

    def error_absoluto(self):
        error_instr = self.error_instrumental()
        error_estad = self.error_estadistico()
        return round(math.sqrt(error_instr ** 2 + error_estad ** 2), 4)

class Longitud:
    def __init__(self, unidad, medidas, medida_maxima_instrumento):
        self.unidad = unidad
        self.medidas = medidas
        self.medida_maxima_instrumento = medida_maxima_instrumento

    def longitud_promedio(self):
        if not self.medidas:
            return 0

        medidas_numeros = [float(medida) for medida in self.medidas]
        promedio = sum(medidas_numeros) / len(medidas_numeros)
        return promedio

    def calcular_lectura_minima(self):
        # Por ejemplo, la lectura mínima es el 1% de la medida máxima
        return 0.01 * self.medida_maxima_instrumento

    def error_instrumental(self):
        lectura_minima = self.calcular_lectura_minima()
        return lectura_minima / 2

    def error_estadistico(self):
        promedio = self.longitud_promedio()
        error_cuadrado = sum((float(medida) - promedio) ** 2 for medida in self.medidas)
        return math.sqrt(error_cuadrado / len(self.medidas))

    def error_absoluto(self):
        error_instr = self.error_instrumental()
        error_estad = self.error_estadistico()
        return round(math.sqrt(error_instr ** 2 + error_estad ** 2), 4)

class MedidasIndirectasVolumenArea:
    def __init__(self, medidas_ancho, medidas_alto, medidas_largo):
        self.medidas_ancho = medidas_ancho
        self.medidas_alto = medidas_alto
        self.medidas_largo = medidas_largo

    def calcular_area(self):
        # Calcular errores automáticamente
        error_ancho = self.calcular_error(self.medidas_ancho)
        error_largo = self.calcular_error(self.medidas_largo)

        area_promedio = self.longitud_promedio(self.medidas_ancho) * self.longitud_promedio(self.medidas_largo)
        error_absoluto_area = math.sqrt((error_ancho * self.longitud_promedio(self.medidas_largo))**2 +
                                        (self.longitud_promedio(self.medidas_ancho) * error_largo)**2)

        return round(area_promedio, 4), round(error_absoluto_area, 4)

    def calcular_volumen(self):
        # Calcular errores automáticamente
        error_ancho = self.calcular_error(self.medidas_ancho)
        error_alto = self.calcular_error(self.medidas_alto)
        error_largo = self.calcular_error(self.medidas_largo)

        volumen_promedio = (self.longitud_promedio(self.medidas_ancho) *
                            self.longitud_promedio(self.medidas_alto) *
                            self.longitud_promedio(self.medidas_largo))

        dv_da = self.longitud_promedio(self.medidas_alto) * self.longitud_promedio(self.medidas_largo)
        dv_dh = self.longitud_promedio(self.medidas_ancho) * self.longitud_promedio(self.medidas_largo)
        dv_dl = self.longitud_promedio(self.medidas_ancho) * self.longitud_promedio(self.medidas_alto)

        error_absoluto_volumen = math.sqrt((dv_da * error_ancho)**2 + (dv_dh * error_alto)**2 + (dv_dl * error_largo)**2)

        return round(volumen_promedio, 4), round(error_absoluto_volumen, 4)

    def longitud_promedio(self, medidas):
        if not medidas:
            return 0

        medidas_numeros = [float(medida) for medida in medidas]
        promedio = sum(medidas_numeros) / len(medidas_numeros)
        return promedio

    def calcular_error(self, medidas):
        if not medidas:
            return 0

        promedio = self.longitud_promedio(medidas)
        error_cuadrado = sum((medida - promedio)**2 for medida in medidas)
        return math.sqrt(error_cuadrado / len(medidas))


@app.route('/calcular', methods=['POST'])

def calcular():
  
    data = request.json

    tipo_medicion = data.get('tipo_medicion')
    unidad = data.get('unidad')
    medida_maxima_instrumento = data.get('medida_maxima_instrumento')
    medidas = data.get('medidas')

    if tipo_medicion.lower() == "masa":
        instancia_medicion = Masa(unidad=unidad, medidas=medidas, medida_maxima_instrumento=medida_maxima_instrumento)
        promedio = instancia_medicion.masa_promedio()
        error_absoluto = instancia_medicion.error_absoluto()

        results = {
            'promedio': f'{promedio:.4f} {instancia_medicion.unidad}',
            'error_absoluto': f'{error_absoluto:.4f} {instancia_medicion.unidad}',
        }
    elif tipo_medicion.lower() == "longitud":
        instancia_medicion = Longitud(unidad=unidad, medidas=medidas, medida_maxima_instrumento=medida_maxima_instrumento)
        promedio = instancia_medicion.longitud_promedio()
        error_absoluto = instancia_medicion.error_absoluto()

        results = {
            'promedio': f'{promedio:.4f} {instancia_medicion.unidad}',
            'error_absoluto': f'{error_absoluto:.4f} {instancia_medicion.unidad}',
        }
    else:
        return jsonify({'error': 'Tipo de medición no reconocido'})

    return jsonify(results)


@app.route('/medidas_indirectas', methods=['POST'])
def medir():
    data = request.json

    tipo_medicion = data.get('tipo_medicion')
    medidas_indirectas = data.get('medidas_indirectas', False)

    if tipo_medicion.lower() == "longitud":
        if medidas_indirectas:
            tipo_medida_indirecta = data.get('tipo')
            medidas_ancho = data.get('medidas_ancho', [])
            medidas_alto = data.get('medidas_alto', [])
            medidas_largo = data.get('medidas_largo', [])

            medidas_indirectas_instancia = MedidasIndirectasVolumenArea(medidas_ancho, medidas_alto, medidas_largo)

            if tipo_medida_indirecta.lower() == "area":
                area, error_area = medidas_indirectas_instancia.calcular_area()
                results = {'area_promedio': f'{area:.4f} cm^2', 'error_absoluto_area': f'{error_area:.4f} cm^2'}
            elif tipo_medida_indirecta.lower() == "volumen":
                volumen, error_volumen = medidas_indirectas_instancia.calcular_volumen()
                results = {'volumen_promedio': f'{volumen:.4f} cm^3', 'error_absoluto_volumen': f'{error_volumen:.4f} cm^3'}
            else:
                return jsonify({'error': 'Tipo de medición indirecta no reconocido'})
        else:
            return jsonify({'error': 'Medición de longitud indirecta requiere medidas adicionales'})
    elif tipo_medicion.lower() == "masa":
        medidas_list = data.get('medidas_list', '')
        try:
            medidas_list = [float(medida) for medida in medidas_list.split()]
        except ValueError:
            return jsonify({'error': 'Invalid input format'})

        masa_instancia = Masa(unidad=data.get('unidad'), medidas=medidas_list)
        promedio_masa = masa_instancia.masa_promedio()
        error_absoluto_masa = masa_instancia.error_absoluto()

        results = {
            'promedio_masa': f'{promedio_masa:.4f} {masa_instancia.unidad}',
            'error_absoluto_masa': f'{error_absoluto_masa:.4f} {masa_instancia.unidad}',
        }
    else:
        return jsonify({'error': 'Tipo de medición no reconocido'})

    return jsonify(results)
@app.route('/regresion-lineal', methods=['POST'])

def calcular_regresion_lineal():
    data = request.get_json()

    datosx = data.get('datosx', [])
    datosy = data.get('datosy', [])

    sumatoriaX, sumatoriay, sumatoriaxy, sumatoriaxcuadrado = calcular_sumatorias(datosx, datosy)
    a = calcularA(sumatoriaxy, sumatoriaX, sumatoriay, sumatoriaxcuadrado, len(datosx))
    b = calcularB(sumatoriay, sumatoriaxcuadrado, sumatoriaX, sumatoriaxy, len(datosx))

    x_pred = np.linspace(min(datosx), max(datosx), 100)
    y_pred = predecir_y(x_pred, a, b)

    resultados = {
        'a': a,
        'b': b,
        'x_pred': x_pred.tolist(),
        'y_pred': y_pred.tolist()
    }

    return jsonify(resultados)
if __name__ == "__main__":
    app.run(port=port)
