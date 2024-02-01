from flask import Flask, request, jsonify
import numpy as np

def predecir_y(x, a, b):
    return a * x + b

def calcular_sumatorias(datosx, datosy):
    sumatoriaX = sum(datosx)
    sumatoriay = sum(datosy)
    sumatoriaxy = sum(x * y for x, y in zip(datosx, datosy))
    sumatoriaxcuadrado = sum(x ** 2 for x in datosx)
    return sumatoriaX, sumatoriay, sumatoriaxy, sumatoriaxcuadrado

def calcularA(sumatoriaXY, sumatoriaX, sumatoriaY, sumatoriaxcuadra, num_elementos):
    a = (num_elementos * sumatoriaXY - sumatoriaX * sumatoriaY) / (num_elementos * sumatoriaxcuadra - sumatoriaX**2)
    return a

def calcularB(sumatoriaY, sumatoriaxcuadra, sumatoriaX, sumatoriaXY, num_elementos):
    b = (sumatoriaY * sumatoriaxcuadra - sumatoriaX * sumatoriaXY) / (num_elementos * sumatoriaxcuadra - sumatoriaX**2)
    return b


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
