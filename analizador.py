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


#def limpiar_codigo(codigo):
#   # Eliminar comentarios de línea
#    codigo = re.sub(r'//.*', '', codigo)
#    # Eliminar comentarios de bloque
#    codigo = re.sub(r'/\*.*?\*/', '', codigo, flags=re.DOTALL)
#    # Eliminar espacios en blanco, tabulaciones y saltos de línea
#    codigo = re.sub(r'\s+', ' ', codigo)
#    return codigo.strip()

def limpiar_codigo(codigo):
    # Expresión regular para cadenas de texto (entre comillas dobles o simples)
    patron_cadenas = r'"[^"]*"|\'[^\']*\''
    
    # Lista para almacenar las cadenas de texto
    cadenas = []

    # Función para reemplazar cadenas con un marcador temporal
    def guardar_cadenas(match):
        cadenas.append(match.group(0))
        return f"__CADENA_{len(cadenas) - 1}__"

    # Paso 1: Reemplazar cadenas de texto con marcadores temporales
    codigo = re.sub(patron_cadenas, guardar_cadenas, codigo)

    # Paso 2: Eliminar comentarios de línea
    codigo = re.sub(r'//.*', '', codigo)

    # Paso 3: Eliminar comentarios de bloque
    codigo = re.sub(r'/\*.*?\*/', '', codigo, flags=re.DOTALL)

    # Paso 4: Eliminar espacios en blanco, tabulaciones y saltos de línea
    codigo = re.sub(r'\s+', ' ', codigo)

    # Paso 5: Restaurar las cadenas de texto
    for i, cadena in enumerate(cadenas):
        codigo = codigo.replace(f"__CADENA_{i}__", cadena)

    # Paso 6: Eliminar espacios al principio y al final
    return codigo.strip()

def calcular_linea(codigo, posicion):
    return codigo.count('\n', 0, posicion) + 1

def calcular_columna(codigo, posicion):
    ultima_nueva_linea = codigo.rfind('\n', 0, posicion)
    if ultima_nueva_linea == -1:
        return posicion + 1
    else:
        return posicion - ultima_nueva_linea

def analizar_codigo(codigo):
    diccionario = cargar_diccionario('tabla_signos_java.txt')
    codigo_limpio = limpiar_codigo(codigo)
    resultados = []

    # Definir patrones para los diferentes tipos de tokens
    patrones = {
        # Identificadores y números
        "identificador": r'[a-zA-Z_][a-zA-Z0-9_]*',
        "numero_entero": r'\d+',
        "numero_decimal": r'\d+\.\d+',

        # Operadores
        "operador_asignacion": r'=|\+=|-=|\*=|/=|%=',
        "operador_aritmetico": r'\+|-|\*|/|%',
        "operador_relacional": r'==|!=|>|<|>=|<=',
        "operador_logico": r'&&|\|\||!',
        "operador_incremento": r'\+\+|--',
        "operador_bit": r'&|\^|\||~|>>|<<|>>>',
        "operador_ternario": r'\?|:',
        "operador_lambda": r'->',
        "operador_referencia": r'::',

        # Delimitadores
        "delimitador": r'\.|,|;|\[|\]|\(|\)|\{|\}',
        
        #Literales
        "comilla_doble": r'"',
        "contenido_cadena": r'"[^"]*"',#"literal_cadena": r'(?=")|"',
        "literal_caracter": r"'([^'\\]|\\.)'",#"literal_caracter": r"'[^']'",
        "literal_booleano": r'true|false',
        "literal_nulo": r'null',

        #Comentarios
        "comentario_linea": r'//.*',
        "comentario_bloque": r'/\*.*?\*/',
        
        "tipo_primitivo": r'byte|short|int|long|float|double|char|boolean',
        "control_flujo": r'if|else|switch|case|default|for|while|do|break|continue',
        "modificador_acceso": r'class|interface|enum|extends|implements|public|private|protected|static|final|abstract'
    }

    # Combinar todos los patrones en uno solo
    patron_combinado = '|'.join(f'(?P<{key}>{value})' for key, value in patrones.items())

    # Escanear el código limpio para identificar los tokens
    for match in re.finditer(patron_combinado, codigo_limpio):
        tipo_token = match.lastgroup
        lexema = match.group(tipo_token)
        entrada_diccionario = next((entrada for entrada in diccionario if entrada["lexema"] == lexema), None)
        linea = calcular_linea(codigo, match.start())
        columna = calcular_columna(codigo, match.start())
        if entrada_diccionario:
            resultados.append({
                "ID": len(resultados) + 1,
                "Lexema": lexema,
                "Línea": linea,
                "Columna": columna,
                "Patrón": entrada_diccionario["nombre"],
                "Reservada": entrada_diccionario["palabraReservada"]
            })
        else:
            resultados.append({
                "ID": len(resultados) + 1,
                "Lexema": lexema,
                "Línea": linea,
                "Columna": columna,
                "Patrón": tipo_token,
                "Reservada": False
            })

    return resultados