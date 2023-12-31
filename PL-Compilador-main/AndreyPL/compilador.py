import re
import tkinter as tk
from tkinter import ttk

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
                            
def generate_triplo_table():
    user_code = '''
    cruz E3a , E3b , 3Ec ;
    nube E3d , E3e , E3f ;
    alfa E3g , E3h , E3i ;
    E3a = 383 ;
    E3b = 353 + E3c ;
    3if3 ( E3a > 100 && E3a < 200 ) {
        E3a = E3a * 3103 ;
        E3a = E3b ~ 3153 ;
        E3h = "perro" ;
    } 3else3 {
        E3a = E3a + 313 ;
        E3g = E3h + "hola" ;
    }
    E3d = E3e * 1234.334563 ;
    E3c = E3a ;
    '''

    lines = user_code.strip().split('\n')
    triplo_table = []
    temp_variable_count = 1

    for line_number, line in enumerate(lines, start=1):
        words = line.split()
        if words:
            keyword = words[0]

            if keyword == '3if3':
                triplo_table.append((f"T{temp_variable_count}", 'E3a', '100', '>'))
                triplo_table.append((f"TR1", 'TRUE', 14))
                triplo_table.append((f"TR1", 'FALSE', 10))
                temp_variable_count += 1
            elif keyword == '3else3':
                triplo_table.append(('JMP', None, None))
                triplo_table.append((f"TR1", 'TRUE', 14))
                triplo_table.append((f"TR1", 'FALSE', 23))
            elif keyword in ['cruz', 'nube', 'alfa']:
                data_type = keyword
                for variable in words[1:]:
                    triplo_table.append((f"{variable}", None, None))
                    triplo_table.append((f"T{temp_variable_count}", f"{variable}", "=", None))
                    temp_variable_count += 1
            else:
                if '=' in line:
                    parts = line.split('=')
                    left_part = parts[0].strip()
                    right_part = parts[1].strip()

                    if '+' in right_part:
                        operands = right_part.split('+')
                        triplo_table.append((f"T{temp_variable_count}", operands[0].strip(), operands[1].strip(), '+'))
                        temp_variable_count += 1
                    elif '*' in right_part:
                        operands = right_part.split('*')
                        triplo_table.append((f"T{temp_variable_count}", operands[0].strip(), operands[1].strip(), '*'))
                        temp_variable_count += 1
                    elif '~' in right_part:
                        operands = right_part.split('~')
                        triplo_table.append((f"T{temp_variable_count}", operands[0].strip(), operands[1].strip(), '~'))
                        temp_variable_count += 1
                    else:
                        triplo_table.append((left_part, right_part, '=', None))

    for entry in triplo_table:
        print(entry)

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
