import re
import tkinter as tk
from tkinter import ttk

variable_pattern = re.compile(r'E3[a-z]')

operators = {'+', '*', '/', '<', '>', '-'}
separators = {',', ';', '=', '}', '{', '(', ')','&&'
              }
keyword_to_type = {'cruz': 'cruz', 'nube': 'nube', 'alfa': 'alfa'}
integer_pattern = re.compile(r'3\d+3')
decimal_pattern = re.compile(r'\d+\.\d+3')

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
                            
def generate_triplo_table():
    user_code = code_text.get("1.0", "end-1c")
    lines = user_code.strip().split('\n')

    triplo_window = tk.Toplevel(window)
    triplo_window.title("Triplo en Postfijo")

    triplo_table = ttk.Treeview(triplo_window, columns=("Dato Objeto", "Dato Fuente", "Operador"))
    triplo_table.heading("#1", text="Dato Objeto")
    triplo_table.heading("#2", text="Dato Fuente")
    triplo_table.heading("#3", text="Operador")

    temp_variable_count = 1
    temp_variable_stack = []

    for line in lines:
        tokens = line.split()
        if len(tokens) >= 3 and tokens[1] == "=":
            result = tokens[0]
            operator = tokens[2]
            if len(tokens) == 3:  # Asignación simple
                triplo_table.insert("", "end", values=(f"T{temp_variable_count}", result, operator))
                temp_variable_count += 1
            else:  # Operación con más de dos operandos
                operands = tokens[3:]
                for operand in operands:
                    if operand not in '+-*/;':  # Si el token no es un operador o punto y coma
                        temp_variable_stack.append(operand)
                    else:  # Si el token es un operador
                        if len(temp_variable_stack) >= 2:  # Verificar si hay suficientes elementos en la pila
                            operand2 = temp_variable_stack.pop()
                            operand1 = temp_variable_stack.pop()
                            if operand1 == ';' or operand2 == ';':
                                continue  # Evitar agregar el ";" a la tabla
                            triplo_table.insert("", "end", values=(operand1, operand2, operand))
                            temp_variable_stack.append(f"T{temp_variable_count}")
                            temp_variable_count += 1
                        else:
                            print("Error: No hay suficientes elementos en la pila para la operación")
                            # Podrías agregar un manejo de error más adecuado aquí si es necesario
                if temp_variable_stack:  # Verificar si la pila no está vacía antes de extraer un elemento
                    last_value = temp_variable_stack.pop()
                    if last_value != ';':  # Evitar agregar el ";" a la tabla
                        triplo_table.insert("", "end", values=(result, last_value, operator))
                else:
                    print("Error: Pila vacía al finalizar la operación")

    triplo_table.pack()

# Resto del código...


# Crear la ventana de la interfaz
window = tk.Tk()
window.title("Analizador Léxico")

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

generate_triplo_button = tk.Button(window, text="Generar Triplo", command=generate_triplo_table)
generate_triplo_button.pack()

window.mainloop()
# Iniciar la interfaz


