import re

def cargar_diccionario(filepath):
    diccionario = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:  # Saltar la primera línea (encabezado)
            partes = line.strip().split()
            if len(partes) == 4:
                diccionario.append({
                    "id": partes[0],
                    "lexema": partes[1],
                    "palabraReservada": partes[2] == "true",
                    "nombre": partes[3]
                })
    return diccionario

def calcular_linea(codigo, posicion):
    return codigo.count('\n', 0, posicion) + 1

def calcular_columna(codigo, posicion):
    # Encuentra la última nueva línea antes de la posición
    ultima_nueva_linea = codigo.rfind('\n', 0, posicion)
    if ultima_nueva_linea == -1:
        # Si no hay nuevas líneas, la columna es posicion + 1 (contando desde 1)
        return posicion + 1
    else:
        # La columna es la diferencia entre posicion y la última nueva línea
        return posicion - ultima_nueva_linea

def analizar_codigo(codigo):
    diccionario = cargar_diccionario('tabla_signos_java.txt')
    resultados = []

    # Definir patrones en orden de prioridad (los más específicos primero)
    patrones = [
        ("comentario_linea", r'//.*'),
        ("comentario_bloque", r'/\*.*?\*/'),
        ("whitespace", r'\s+'),
        ("literal_caracter", r"'([^'\\]|\\.)'"),
        ("cadenaLiteral", r'"(?:[^"\\]|\\.)*"'),
        ("literal_booleano", r'true|false'),
        ("literal_nulo", r'null'),
        ("operador_lambda", r'->'),
        ("operador_referencia", r'::'),
        ("operador_incremento", r'\+\+|--'),
        ("operador_asignacion", r'=|\+=|-=|\*=|/=|%='),
        ("operador_relacional", r'==|!=|>|<|>=|<='),
        ("operador_logico", r'&&|\|\||!'),
        ("operador_bit", r'&|\^|\||~|>>|<<|>>>'),
        ("operador_ternario", r'\?|:'),
        ("operador_aritmetico", r'\+|-|\*|/|%'),
        ("numero_decimal", r'\d+\.\d+'),
        ("numero_entero", r'\d+'),
        ("delimitador", r'\.|,|;|\[|\]|\(|\)|\{|\}'),
        ("tipo_primitivo", r'byte|short|int|long|float|double|char|boolean'),
        ("control_flujo", r'if|else|switch|case|default|for|while|do|break|continue'),
        ("modificador_acceso", r'class|interface|enum|extends|implements|public|private|protected|static|final|abstract'),
        ("identificador", r'[a-zA-Z_][a-zA-Z0-9_]*'),
        # Patrones para símbolos no válidos
        ("operador_no_valido", r'\*\*|:=|=>|<=>|<>'),
        ("caracter_especial_no_valido", r'¿|¡|¬|‰|§'),
        ("delimitador_no_valido", r'«|»|„|›|‹'),
        ("operador_matematico_no_valido", r'÷|×|∑|∏'),
        ("caracter_no_reconocido", r'ñ|Ñ|æ|ø|ß|ð'),
    ]

    # Construir el regex combinado
    patron_combinado = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in patrones)

    # Escanear el código original
    for match in re.finditer(patron_combinado, codigo, flags=re.DOTALL):
        tipo_token = match.lastgroup
        lexema = match.group(tipo_token)
        start = match.start()

        # Saltar comentarios y espacios
        if tipo_token in ["whitespace", "comentario_linea", "comentario_bloque"]:
            continue

        # Manejar símbolos no válidos
        if tipo_token in ["operador_no_valido", "caracter_especial_no_valido", 
                          "delimitador_no_valido", "operador_matematico_no_valido", 
                          "caracter_no_reconocido"]:
            linea = calcular_linea(codigo, start)
            columna = calcular_columna(codigo, start)
            tipo_error = {
                "operador_no_valido": "Operador no válido en Java",
                "caracter_especial_no_valido": "Carácter especial no válido en Java",
                "delimitador_no_valido": "Delimitador no válido en Java",
                "operador_matematico_no_valido": "Operador matemático no válido en Java",
                "caracter_no_reconocido": "Carácter no reconocido en identificadores de Java",
            }[tipo_token]
            
            resultados.append({
                "ID": len(resultados) + 1,
                "Lexema": lexema,
                "Línea": linea,
                "Columna": columna,
                "Patrón": tipo_error,
                "Reservada": False,
                #"Mensaje": f"{tipo_error}: '{lexema}' no es válido en Java."
            })
            continue  # Saltar al siguiente token

        # Buscar en el diccionario
        entrada_diccionario = next((entrada for entrada in diccionario if entrada["lexema"] == lexema), None)
        linea = calcular_linea(codigo, start)
        columna = calcular_columna(codigo, start)
        
        if entrada_diccionario:
            resultados.append({
                "ID": entrada_diccionario["id"],
                "Lexema": lexema,
                "Línea": linea,
                "Columna": columna,
                "Patrón": entrada_diccionario["nombre"],
                "Reservada": entrada_diccionario["palabraReservada"]
            })
        else:
            # Determinar el patrón para tokens no reservados
            patron = tipo_token
            if tipo_token == "cadenaLiteral":
                patron = "literal_cadena"
            elif tipo_token == "literal_caracter":
                patron = "literal_caracter"
            resultados.append({
                "ID": tipo_token,
                "Lexema": lexema,
                "Línea": linea,
                "Columna": columna,
                "Patrón": patron,
                "Reservada": False
            })

    return resultados