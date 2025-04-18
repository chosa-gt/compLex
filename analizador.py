import re

def cargar_diccionario(filepath):
    try:
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
    except FileNotFoundError:
        print(f"Error: No se encuentra el archivo '{filepath}'")
        return []
    except Exception as e:
        print(f"Error al cargar el diccionario: {e}")
        return []

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
    
    # Definir palabras reservadas de Java
    palabras_reservadas = {
        "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char",
        "class", "const", "continue", "default", "do", "double", "else", "enum",
        "extends", "final", "finally", "float", "for", "goto", "if", "implements",
        "import", "instanceof", "int", "interface", "long", "native", "new", "package",
        "private", "protected", "public", "return", "short", "static", "strictfp", 
        "super", "switch", "synchronized", "this", "throw", "throws", "transient", 
        "try", "void", "volatile", "while", "true", "false", "null"
    }

    # Definir patrones en orden de prioridad (los más específicos primero)
    patrones = [
        ("comentario_linea", r'//[^\n]*'),
        ("comentario_bloque", r'/\*[\s\S]*?\*/'),
        ("whitespace", r'\s+'),
        ("literal_caracter", r"'([^'\\\n]|\\[tnrfb\"'\\]|\\u[0-9a-fA-F]{4})'"),
        ("cadenaLiteral", r'"([^"\\\n]|\\[tnrfb\"\'\\]|\\u[0-9a-fA-F]{4})*"'),
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
        ("numero_decimal", r'\d+\.\d+([eE][+-]?\d+)?[fFdD]?'),
        ("numero_entero", r'\d+[lL]?'),
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
    posicion_actual = 0
    for match in re.finditer(patron_combinado, codigo):
        tipo_token = match.lastgroup
        lexema = match.group(tipo_token)
        start = match.start()

        # Verificar si hay caracteres no reconocidos entre el último match y este
        if start > posicion_actual:
            fragmento_no_reconocido = codigo[posicion_actual:start]
            if fragmento_no_reconocido.strip():  # Si hay algo que no sean espacios
                linea = calcular_linea(codigo, posicion_actual)
                columna = calcular_columna(codigo, posicion_actual)
                resultados.append({
                    "ID": "ERROR",
                    "Lexema": fragmento_no_reconocido,
                    "Línea": linea,
                    "Columna": columna,
                    "Patrón": "Carácter no reconocido",
                    "Reservada": False
                })
        
        posicion_actual = match.end()

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
                "ID": "ERROR",
                "Lexema": lexema,
                "Línea": linea,
                "Columna": columna,
                "Patrón": tipo_error,
                "Reservada": False,
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
                
            # Verificar si es una palabra reservada
            es_reservada = lexema in palabras_reservadas
            
            resultados.append({
                "ID": tipo_token if not es_reservada else "reserved_" + lexema,
                "Lexema": lexema,
                "Línea": linea,
                "Columna": columna,
                "Patrón": patron,
                "Reservada": es_reservada
            })

    # Verificar si hay caracteres no reconocidos al final del código
    if posicion_actual < len(codigo):
        fragmento_final = codigo[posicion_actual:]
        if fragmento_final.strip():  # Si hay algo que no sean espacios
            linea = calcular_linea(codigo, posicion_actual)
            columna = calcular_columna(codigo, posicion_actual)
            resultados.append({
                "ID": "ERROR",
                "Lexema": fragmento_final,
                "Línea": linea,
                "Columna": columna,
                "Patrón": "Carácter no reconocido",
                "Reservada": False
            })

    return resultados