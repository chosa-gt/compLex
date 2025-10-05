import re

def cargar_diccionario(filepath):
    """
    Carga el diccionario de tokens desde un archivo de texto con el nuevo formato.
    El archivo debe tener un encabezado "TOKEN_TYPE LEXEME IS_RESERVED DESCRIPTION".
    Las líneas que comienzan con '#' o están vacías son ignoradas.
    """
    try:
        diccionario = []
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            header_found = False
            for line in lines:
                if line.strip().startswith("TOKEN_TYPE LEXEME IS_RESERVED DESCRIPTION"):
                    header_found = True
                    continue
                if not header_found: # Saltar líneas antes del encabezado
                    continue

                line = line.strip()
                if not line or line.startswith('#'): # Saltar líneas vacías o comentarios
                    continue
                
                parts = line.split(None, 3)  # divide en máximo 4 partes, permitiendo espacios en DESCRIPTION
                if len(parts) == 4:
                    diccionario.append({
                        "TOKEN_TYPE": parts[0],
                        "LEXEME": parts[1],
                        "IS_RESERVED": parts[2].lower() == "true",
                        "DESCRIPTION": parts[3]
                    })
                else:
                    print(f"Advertencia: Línea con formato incorrecto en el diccionario ignorada: '{line}'")
        return diccionario
    except FileNotFoundError:
        print(f"Error: No se encuentra el archivo '{filepath}'")
        return []
    except Exception as e:
        print(f"Error al cargar el diccionario: {e}")
        return []

def calcular_linea(codigo, posicion):
    """Calcula el número de línea dado el código y una posición."""
    return codigo.count('\n', 0, posicion) + 1

def calcular_columna(codigo, posicion):
    """Calcula el número de columna dado el código y una posición."""
    ultima_nueva_linea = codigo.rfind('\n', 0, posicion)
    if ultima_nueva_linea == -1:
        return posicion + 1
    else:
        return posicion - ultima_nueva_linea

def analizar_codigo(codigo):
    diccionario_original = cargar_diccionario('tabla_signos_java.txt')
    if not diccionario_original:
        return []

    resultados = []

    # Mapeo rápido de lexema -> entrada del diccionario (solo para palabras reservadas y símbolos)
    lexeme_to_token_info = {}
    for entry in diccionario_original:
        if entry["LEXEME"] not in ["__ID__", "__STRING__", "__CHAR__", "__INTEGER__", "__FLOAT__", "__BINARY__", "__HEX__"]:
            lexeme_to_token_info[entry["LEXEME"]] = entry

    # --- Construcción de patrones regex ---
    all_regex_patterns = []

    # 1. Comentarios
    all_regex_patterns.append(("COMMENT_DOC_START", r'/\*\*.*?\*/'))
    all_regex_patterns.append(("COMMENT_BLOCK_START", r'/\*.*?\*/'))
    all_regex_patterns.append(("COMMENT_LINE_PREFIX", r'//[^\n]*'))

    # 2. Literales de Cadena y Carácter
    all_regex_patterns.append(("LIT_STRING", r'"(?:[^"\\\n]|\\.)*"'))
    all_regex_patterns.append(("LIT_CHAR", r"'(?:[^'\\\n]|\\.)'"))

    # 3. Literales Numéricos
    all_regex_patterns.append(("LIT_HEX", r'0x[0-9a-fA-F_]+'))
    all_regex_patterns.append(("LIT_BINARY", r'0b[01_]+'))
    # Flotantes mejorados
    all_regex_patterns.append(("LIT_FLOAT", 
        r'(?:(?:[0-9][0-9_]*\.[0-9_]+|\.[0-9_]+)(?:[eE][+-]?[0-9_]+)?[fFdD]?|'
        r'[0-9][0-9_]*(?:[eE][+-]?[0-9_]+)[fFdD]?|'
        r'[0-9][0-9_]*[fFdD])'))
    # Enteros (se ponen después)
    all_regex_patterns.append(("LIT_INTEGER", r'[0-9][0-9_]*[lL]?'))

    # 4. Lexemas fijos (solo símbolos y operadores, no keywords)
    fixed_lexeme_entries = [
        entry for entry in diccionario_original
        if entry["LEXEME"] not in ["__ID__", "__STRING__", "__CHAR__", "__INTEGER__", "__FLOAT__", "__BINARY__", "__HEX__"]
        and not entry["IS_RESERVED"]  # no incluir palabras reservadas
    ]
    fixed_lexeme_entries.sort(key=lambda x: len(x["LEXEME"]), reverse=True)

    for entry in fixed_lexeme_entries:
        group_name = f"FIXED_LEXEME_{entry['TOKEN_TYPE']}"
        all_regex_patterns.append((group_name, re.escape(entry["LEXEME"])))

    # 5. Identificadores
    all_regex_patterns.append(("IDENTIFIER", r'[a-zA-Z_$][a-zA-Z0-9_$]*'))

    # 6. Espacios en blanco
    all_regex_patterns.append(("WHITESPACE", r'\s+'))

    # 7. Catch-all
    all_regex_patterns.append(("ERROR_UNRECOGNIZED_CHAR", r'.'))

    # Compilar regex
    patron_combinado = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in all_regex_patterns), re.DOTALL)

    posicion_actual = 0
    for match in patron_combinado.finditer(codigo):
        tipo_token_grupo = match.lastgroup
        lexema = match.group(tipo_token_grupo)
        start = match.start()

        linea = calcular_linea(codigo, start)
        columna = calcular_columna(codigo, start)

        # Texto no reconocido entre tokens
        if start > posicion_actual:
            fragmento_no_reconocido = codigo[posicion_actual:start]
            if fragmento_no_reconocido.strip():
                error_line = calcular_linea(codigo, posicion_actual)
                error_col = calcular_columna(codigo, posicion_actual)
                resultados.append({
                    "TOKEN_TYPE": "ERROR_FRAGMENT",
                    "LEXEME": fragmento_no_reconocido,
                    "LINE": error_line,
                    "COLUMN": error_col,
                    "DESCRIPTION": "Fragmento no reconocido entre tokens",
                    "IS_RESERVED": False
                })

        posicion_actual = match.end()

        # Ignorar espacios y comentarios
        if tipo_token_grupo in ["WHITESPACE", "COMMENT_LINE_PREFIX", "COMMENT_BLOCK_START", "COMMENT_DOC_START"]:
            continue

        # Error de carácter
        if tipo_token_grupo == "ERROR_UNRECOGNIZED_CHAR":
            resultados.append({
                "TOKEN_TYPE": "ERROR",
                "LEXEME": lexema,
                "LINE": linea,
                "COLUMN": columna,
                "DESCRIPTION": "Carácter no reconocido",
                "IS_RESERVED": False
            })
            continue

        token_entry = None

        # Lexemas fijos
        if tipo_token_grupo.startswith("FIXED_LEXEME_"):
            token_type_from_group = tipo_token_grupo.replace("FIXED_LEXEME_", "")
            token_entry = next((e for e in diccionario_original if e["TOKEN_TYPE"] == token_type_from_group and e["LEXEME"] == lexema), None)
            if not token_entry:
                token_entry = lexeme_to_token_info.get(lexema)

        # Identificadores y keywords
        elif tipo_token_grupo == "IDENTIFIER":
            if lexema in lexeme_to_token_info and lexeme_to_token_info[lexema]["IS_RESERVED"]:
                token_entry = lexeme_to_token_info[lexema]
            else:
                token_entry = {
                    "TOKEN_TYPE": "ID_IDENTIFIER",
                    "LEXEME": lexema,
                    "IS_RESERVED": False,
                    "DESCRIPTION": "identificador"
                }

        # Literales
        elif tipo_token_grupo.startswith("LIT_"):
            descripcion = {
                "LIT_STRING": "literal de cadena",
                "LIT_CHAR": "literal de carácter",
                "LIT_HEX": "literal hexadecimal",
                "LIT_BINARY": "literal binario",
                "LIT_FLOAT": "literal flotante",
                "LIT_INTEGER": "literal entero"
            }.get(tipo_token_grupo, "literal")
            token_entry = {
                "TOKEN_TYPE": tipo_token_grupo,
                "LEXEME": lexema,
                "IS_RESERVED": False,
                "DESCRIPTION": descripcion
            }

        if token_entry:
            resultados.append({
                "TOKEN_TYPE": token_entry["TOKEN_TYPE"],
                "LEXEME": token_entry["LEXEME"],
                "LINE": linea,
                "COLUMN": columna,
                "DESCRIPTION": token_entry["DESCRIPTION"],
                "IS_RESERVED": token_entry["IS_RESERVED"]
            })
        else:
            resultados.append({
                "TOKEN_TYPE": "ERROR_UNCLASSIFIED",
                "LEXEME": lexema,
                "LINE": linea,
                "COLUMN": columna,
                "DESCRIPTION": f"Token no clasificado o mapeado: {tipo_token_grupo}",
                "IS_RESERVED": False
            })

    # Fragmento final no reconocido
    if posicion_actual < len(codigo):
        fragmento_final = codigo[posicion_actual:]
        if fragmento_final.strip():
            linea = calcular_linea(codigo, posicion_actual)
            columna = calcular_columna(codigo, posicion_actual)
            resultados.append({
                "TOKEN_TYPE": "ERROR_FRAGMENT",
                "LEXEME": fragmento_final,
                "LINE": linea,
                "COLUMN": columna,
                "DESCRIPTION": "Fragmento final no reconocido",
                "IS_RESERVED": False
            })

    return resultados