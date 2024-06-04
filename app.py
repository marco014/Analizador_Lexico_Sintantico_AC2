import os
import re
from flask import Flask, request, render_template

app = Flask(__name__)
TAQUERIA = 'taqueria/'
if not os.path.exists(TAQUERIA):
    os.makedirs(TAQUERIA)
app.config['TAQUERIA'] = TAQUERIA

def analizar_tacos(code):
    resultado = []
    ingredientes = {'int', 'for', 'if', 'else', 'while', 'return', 'system.out.println'}  # Puedes agregar más palabras reservadas aquí
    lineas = code.split('\n')
    for numero_taco, tacos in enumerate(lineas, start=1):
        indice = 0
        while indice < len(tacos):
            ingrediente_detectado = False
            for ingrediente in ingredientes:
                if tacos[indice:].startswith(ingrediente) and (indice + len(ingrediente) == len(tacos) or not tacos[indice + len(ingrediente)].isalnum()):
                    resultado.append((numero_taco, indice, 'Palabra reservada', ingrediente))
                    indice += len(ingrediente)
                    ingrediente_detectado = True
                    break
            if ingrediente_detectado:
                continue

            char = tacos[indice]
            if char in [';', '{', '}', '(', ')']:
                tipo = 'Punto y coma' if char == ';' else 'Llave' if char in ['{', '}'] else 'Paréntesis'
                resultado.append((numero_taco, indice, tipo, char))
                indice += 1
            elif char.isdigit():
                resultado.append((numero_taco, indice, 'Número', char))
                indice += 1
            else:
                indice += 1
    return resultado

def analizar_machetes(code):
    resultado = []
    correct_keyword = 'system.out.println'
    lineas = code.split('\n')
    for numero_machete, machete in enumerate(lineas, start=1):
        stripped_line = machete.strip()
        if stripped_line.startswith('system.out.'):
            if stripped_line.startswith(correct_keyword):
                resultado.append((numero_machete, correct_keyword, True))
            else:
                resultado.append((numero_machete, stripped_line.split('(')[0], False))
        elif 'system' in stripped_line or '.out' in stripped_line:
            resultado.append((numero_machete, stripped_line.split('(')[0], False))
        else:
            if 'for' in stripped_line:
                match = re.match(r'\s*for\s*\(\s*int\s+\w+\s*=\s*\d+\s*;\s*\w+\s*(<|>|<=|>=)\s*\d+\s*;\s*\w+(\+\+|--)\s*\)\s*{', stripped_line)
                if not match:
                    resultado.append((numero_machete, 'For', False))
                else:
                    resultado.append((numero_machete, 'For', True))
    return resultado

@app.route('/', methods=['GET', 'POST'])
def index():
    codigo = ""
    resultado_tacos = []
    resultado_machetes = []
    if request.method == 'POST':
        if 'file' in request.files and request.files['file'].filename != '':
            archivo = request.files['file']
            ruta_archivo = os.path.join(app.config['TAQUERIA'], archivo.filename)
            archivo.save(ruta_archivo)
            with open(ruta_archivo, 'r') as f:
                codigo = f.read()
        elif 'code' in request.form and request.form['code'].strip() != '':
            codigo = request.form['code']
        else:
            return "No file selected or code provided"
        
        resultado_tacos = analizar_tacos(codigo)
        resultado_machetes = analizar_machetes(codigo)
        
    return render_template('index.html', code=codigo, lexical_result=resultado_tacos, syntactic_result=resultado_machetes)

if __name__ == '__main__':
    app.run(debug=True)
