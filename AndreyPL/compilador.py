import re
import tkinter as tk
from tkinter import ttk

# Crear la ventana de la interfaz
window = tk.Tk()
window.title("Analizador Léxico")

variable_pattern = re.compile(r'E3[a-z]')

operators = {'+', '*', '/', '<', '>', '~'}
separators = {',', ';', '=', '}', '{', '(', ')','&&'}
conditional_keywords = {'3if3', '3then3', '3else3'}
keyword_to_type = {'cruz': 'cruz', 'nube': 'nube', 'alfa': 'alfa'}
integer_pattern = re.compile(r'3\d+3')
decimal_pattern = re.compile(r'\d+\.\d+3')
temp_variable_stack = [] 

# Función para analizar el código fuente e identificar tokens
def analyze_code():
    global semantic_errors
    user_code = code_text.get("1.0", "end-1c")
    lines = user_code.strip().split('\n')
    added_tokens = set()
    semantic_errors = []

    for row in result_tree.get_children():
        result_tree.delete(row)
        
    used_variables = set()        

    for line_number, line in enumerate(lines, start=1):
        words = line.split()
        if words:
            keyword = words[0]
            if keyword in keyword_to_type:
                data_type = keyword_to_type[keyword]
                for variable in words[1:]:
                    if variable_pattern.fullmatch(variable):
                        lexeme = variable
                        if lexeme not in added_tokens:
                            result_tree.insert("", "end", values=(line_number, lexeme, data_type))
                            added_tokens.add(lexeme)
                    else:
                        if variable not in added_tokens and variable not in separators:
                            original_type = None
                            for key, value in keyword_to_type.items():
                                if variable in user_code and value == key:
                                    original_type = value
                                    break

                            if original_type:
                                result_tree.insert("", "end", values=(line_number, variable, original_type))
                                added_tokens.add(variable)
                            else:
                                semantic_errors.append((line_number, variable, f"Error de declaración: {variable} no es un identificador válido"))
            else:
                for word in words:
                    if word in keyword_to_type:
                        data_type = keyword_to_type[word]
                        continue
                    elif variable_pattern.fullmatch(word) and word not in separators:  # Evitar que los separadores sean identificados como tokens de tipo cruz, nube o alfa
                        lexeme = word
                        if lexeme not in added_tokens:
                            result_tree.insert("", "end", values=(line_number, lexeme, data_type))
                            added_tokens.add(lexeme)
                    elif word in operators or word in separators:
                        lexeme = word
                        if lexeme not in added_tokens:
                            result_tree.insert("", "end", values=(line_number, lexeme, 'OPERADOR' if lexeme in operators else 'SEPARADOR'))
                            added_tokens.add(lexeme)
                    elif word in conditional_keywords:
                        lexeme = word
                        if lexeme not in added_tokens:
                            result_tree.insert("", "end", values=(line_number, lexeme, 'CONDICIONAL'))
                            added_tokens.add(lexeme)
                    elif word in added_tokens:
                        continue
                    else:
                        if integer_pattern.fullmatch(word):
                            result_tree.insert("", "end", values=(line_number, word, 'ENTERO'))
                            added_tokens.add(word)
                        elif decimal_pattern.fullmatch(word):
                            result_tree.insert("", "end", values=(line_number, word, 'FLOTANTE'))
                            added_tokens.add(word)
                        elif word.startswith('"') and word.endswith('"'):
                            result_tree.insert("", "end", values=(line_number, word, 'CADENA'))
                            added_tokens.add(word)
                        else:
                            error_description = f"Error: '{word}' no es un token válido"
                            semantic_errors.append((line_number, word, error_description))
                            result_tree.insert("", "end", values=(line_number, word, 'ERROR', error_description))
                            
def generate_triplo_postfijo():
    user_code = code_text.get("1.0", tk.END).strip()
    lines = user_code.split('\n')

    dato_objeto = []
    dato_fuente = []
    operador = []

    ignore_elements = {',', ';', ')', '(', '{', '}', '3else3', '3if3', '3then3'}

    first_line = True

    for line in lines:
        elements = line.split()  # Dividir la línea en elementos

        # Comprobar si la línea no comienza con 'cruz', 'nube' o 'alfa'
        if not any(word in elements for word in ['cruz', 'nube', 'alfa']):
            # Comprobar si hay al menos 3 elementos en la línea (dato objeto, operador, dato fuente)
            if len(elements) >= 3:
                # Filtrar elementos no deseados
                elements = [e for e in elements if e not in ignore_elements]

                dato_objeto.append('T1')  # Agregar T1 como dato objeto al principio

                # Verificar si hay suficientes elementos después de filtrar
                if len(elements) >= 3:
                    operador.append(elements[1])  # El operador será el segundo elemento
                    dato_fuente.append(elements[2])  # El dato fuente será el tercer elemento

            # Lógica para cambiar la posición de T1 después de la primera iteración
            if not first_line:
                temp = dato_objeto[0]  # Almacenar el valor de T1
                dato_objeto[0] = dato_fuente[-1]  # Reemplazar el primer elemento con el último dato fuente
                dato_fuente[-1] = temp  # Reemplazar el último dato fuente con el valor almacenado de T1

        first_line = False  # Después de la primera iteración, actualizar el flag

    # Imprimir la tabla del triplo en postfijo
    print("Dato Objeto\tDato Fuente\tOperador")
    for obj, fuente, oper in zip(dato_objeto, dato_fuente, operador):
        print(f"{obj}\t\t{fuente}\t\t{oper}")
# Resto del código de la interfaz gráfica...esto del código de la interfaz gráfica...tón para generar el triplo
triplo_button = tk.Button(window, text="Generar Triplo", command=generate_triplo_postfijo)
triplo_button.pack()

# Panel de texto para ingresar el código fuente
code_text = tk.Text(window, wrap="none", width=40, height=10)
code_text.pack()

# Botón para iniciar el análisis léxico
analyze_button = tk.Button(window, text="Analizar Código", command=analyze_code)
analyze_button.pack()

result_tree = ttk.Treeview(window, columns=("Línea", "Token", "Tipo", "Descripción"))
result_tree.heading("#1", text="Línea")
result_tree.heading("#2", text="Token")
result_tree.heading("#3", text="Tipo")
result_tree.heading("#4", text="Descripción")
result_tree.pack()

window.mainloop()
# Iniciar la interfaz