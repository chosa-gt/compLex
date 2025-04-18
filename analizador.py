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

class AnalizadorSintactico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos_actual = 0
        self.errores = []
        self.niveles_ambito = 0  # Para control de bloques anidados

    def analizar(self):
        try:
            self.programa()
            if not self.esta_al_final():
                self.error("Hay tokens inesperados al final del archivo")
        except ParseError:
            pass
        return self.errores

    def programa(self):
        while not self.esta_al_final():
            if self.comprobar('modificadorAcceso', 'public'):
                self.declaracion_clase()
            else:
                self.error("Se esperaba declaración de clase pública")
                break

    def declaracion_clase(self):
        self.consumir('modificadorAcceso', 'public')
        self.consumir('modificadorAcceso', 'class')
        self.consumir('identificador')
        self.consumir('separador', '{')
        self.niveles_ambito += 1
        
        while not self.comprobar('separador', '}'):
            if self.comprobar('modificadorAcceso'):
                self.declaracion_metodo()
            else:
                self.error("Se esperaba declaración de método o variable")
                break
        
        self.consumir('separador', '}')
        self.niveles_ambito -= 1

    def declaracion_metodo(self):
        # Modificadores
        while self.comprobar('modificadorAcceso'):
            self.avanzar()
        
        # Tipo de retorno
        if not self.comprobar_tipos(['Operadores', 'identificador']):
            self.error("Tipo de retorno inválido")
        self.avanzar()
        
        # Nombre del método
        self.consumir('identificador')
        
        # Parámetros
        self.consumir('delimitador', '(')
        self.lista_parametros()
        self.consumir('delimitador', ')')
        
        # Cuerpo del método
        self.consumir('delimitador', '{')
        self.niveles_ambito += 1
        
        while not self.comprobar('delimitador', '}'):
            self.declaracion()
        
        self.consumir('delimitador', '}')
        self.niveles_ambito -= 1

    def lista_parametros(self):
        if not self.comprobar('delimitador', ')'):
            while True:
                if not self.comprobar_tipos(['tipo_primitivo', 'identificador', 'metodoEspecial']):
                    self.error("Tipo de parámetro inválido")
                self.avanzar()
                self.consumir('identificador')
                if not self.comprobar('delimitador', ','):
                    break
                self.avanzar()

    def declaracion(self):
        if self.comprobar('palabraReservada', 'if'):
            self.declaracion_if()
        elif self.comprobar('palabraReservada', 'while'):
            self.declaracion_while()
        elif self.comprobar('palabraReservada', 'for'):
            self.declaracion_for()
        elif self.comprobar_tipos(['tipo_primitivo', 'identificador']):
            self.declaracion_variable()
        else:
            self.expresion()

    def declaracion_if(self):
        self.consumir('palabraReservada', 'if')
        self.consumir('delimitador', '(')
        self.expresion()
        self.consumir('delimitador', ')')
        self.consumir('delimitador', '{')
        self.niveles_ambito += 1
        
        while not self.comprobar('delimitador', '}'):
            self.declaracion()
        
        self.consumir('delimitador', '}')
        self.niveles_ambito -= 1
        
        if self.comprobar('palabraReservada', 'else'):
            self.avanzar()
            self.consumir('delimitador', '{')
            self.niveles_ambito += 1
            
            while not self.comprobar('delimitador', '}'):
                self.declaracion()
            
            self.consumir('delimitador', '}')
            self.niveles_ambito -= 1

    def declaracion_variable(self):
        self.avanzar()  # Tipo
        self.consumir('identificador')
        if self.comprobar('operador_asignacion', '='):
            self.avanzar()
            self.expresion()
        self.consumir('delimitador', ';')

    def expresion(self):
        self.expresion_primaria()
        while self.comprobar('operador_asignacion'):
            self.avanzar()
            self.expresion_primaria()

    def expresion_primaria(self):
        if self.comprobar('literal_booleano') or self.comprobar('literal_nulo'):
            self.avanzar()
        elif self.comprobar('numero_entero') or self.comprobar('numero_decimal'):
            self.avanzar()
        elif self.comprobar('cadenaLiteral'):
            self.avanzar()
        elif self.comprobar('identificador'):
            self.avanzar()
            if self.comprobar('delimitador', '('):
                self.lista_argumentos()
        else:
            self.error("Expresión inválida")

    def lista_argumentos(self):
        self.consumir('delimitador', '(')
        if not self.comprobar('delimitador', ')'):
            while True:
                self.expresion()
                if not self.comprobar('delimitador', ','):
                    break
                self.avanzar()
        self.consumir('delimitador', ')')

    # Funciones de utilidad
    def consumir(self, tipo, valor=None):
        if self.comprobar(tipo, valor):  # Método correcto
            self.avanzar()
        else:
            self.error(f"Se esperaba {tipo} '{valor}'")

    def comprobar(self, tipo, valor=None):
        if self.esta_al_final():
            return False
        token = self.tokens[self.pos_actual]
        if valor:
            return token['ID'] == tipo and token['Lexema'] == valor
        return token['ID'] == tipo
    
    def comprobar_tipos(self, tipos):
        return any(self.comprobar(tipo) for tipo in tipos)

    def avanzar(self):
        if not self.esta_al_final():
            self.pos_actual += 1

    def esta_al_final(self):
        return self.pos_actual >= len(self.tokens)

    def error(self, mensaje):
        if self.pos_actual < len(self.tokens):
            token = self.tokens[self.pos_actual]
            linea = token['Línea']
            columna = token['Columna']
        else:
            linea = self.tokens[-1]['Línea'] if self.tokens else 1
            columna = self.tokens[-1]['Columna'] if self.tokens else 1
        
        error_msg = f"Error sintáctico en línea {linea}, columna {columna}: {mensaje}"
        self.errores.append(error_msg)
        raise ParseError()

class ParseError(Exception):
    pass

# Uso del analizador
