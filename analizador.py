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

# Operadores
OPERADOR_ASIGNACION = {'+=', '-=', '*=', '/=', '%=', '=', '&=', '|=', '^=', '<<=', '>>=', '>>>='}
OPERADOR_ARITMETICO = {'+', '-', '*', '/', '%', '++', '--'}
OPERADOR_RELACIONAL = {'==', '!=', '>', '<', '>=', '<=', 'instanceof'}
OPERADOR_LOGICO = {'&&', '||', '!'}
OPERADOR_BIT = {'&', '|', '^', '~', '<<', '>>', '>>>'}
OPERADOR_TERCIARIO = {'?', ':'}
OPERADOR_REFERENCIA = '::'

# Delimitadores
DELIMITADORES = {'(', ')', '{', '}', '[', ']', ';', ',', '.', '...', '@'}

# Palabras reservadas
TIPOS_PRIMITIVOS = {'byte', 'short', 'int', 'long', 'float', 'double', 'char', 'boolean', 'void'}
MODIFICADORES_ACCESO = {'public', 'private', 'protected', 'static', 'final', 'abstract'}
CONTROL_FLUJO = {'if', 'else', 'switch', 'case', 'default', 'for', 'while', 'do', 'break', 'continue'}
MANEJO_EXCEPCIONES = {'try', 'catch', 'finally', 'throw', 'throws'}
ORIENTACION_OBJETOS = {'class', 'interface', 'enum', 'extends', 'implements', 'new', 'this', 'super'}
LITERALES_ESPECIALES = {'true', 'false', 'null'}

# Funciones incorporadas
METODOS_ESENCIALES = {'main', 'println', 'print', 'format'}

class AnalizadorSintactico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos_actual = 0
        self.errores = []
        self.ambito_actual = []  # Para manejar bloques anidados

    def analizar(self):
        try:
            self.programa()
            if not self.esta_al_final():
                token = self.token_actual()
                self.error(f"Tokens inesperados al final: '{token['Lexema']}'")
            return self.errores
        except ParseError:
            return self.errores

    def programa(self):
        # Punto de entrada principal para analizar un programa Java
        while not self.esta_al_final():
            if self.comprobar('modificadorAcceso', 'public'):
                self.declaracion_clase()
            else:
                self.error("Se esperaba una clase pública")
                break

    def declaracion_clase(self):
        self.consumir('modificadorAcceso', 'public')
        self.consumir('palabraReservada', 'class')
        self.consumir('identificador')  # Nombre de la clase
        
        # Herencia
        if self.comprobar('palabraReservada', 'extends'):
            self.consumir('palabraReservada', 'extends')
            self.consumir('identificador')  # Clase padre
            
        # Implementación de interfaces
        if self.comprobar('palabraReservada', 'implements'):
            self.consumir('palabraReservada', 'implements')
            self.lista_identificadores()  # Lista de interfaces
            
        self.consumir('separador', '{')
        self.ambito_actual.append('clase')
        
        # Miembros de la clase
        while not self.comprobar('separador', '}'):
            if self.comprobar('modificadorAcceso'):
                self.declaracion_metodo()
            else:
                self.error("Declaración inválida en ámbito de clase")
                
        self.consumir('separador', '}')
        self.ambito_actual.pop()

    def declaracion_metodo(self):
    # Modificadores
        while self.comprobar('modificadorAcceso') or self.comprobar('palabraReservada', 'static'):
            self.avanzar()
            
        # Tipo de retorno (incluyendo void)
        if not self.comprobar_tipo(incluir_void=True):  # Cambio clave aquí
            self.error("Tipo de retorno inválido")
        self.avanzar()
        
        # Nombre del método
        if self.comprobar('metodoEspecial', 'Main'):
            self.consumir('metodoEspecial', 'Main')
        else:
            self.consumir('identificador')
        
        # Parámetros
        self.consumir('separador', '(')
        self.lista_parametros()
        self.consumir('separador', ')')
        
        # Cuerpo del método
        self.consumir('separador', '{')
        self.ambito_actual.append('metodo')
        
        while not self.comprobar('separador', '}'):
            self.declaracion()
            
        self.consumir('separador', '}')
        self.ambito_actual.pop()

    def lista_parametros(self):
        while not self.comprobar('separador', ')'):
            self.consumir_tipo()
            self.consumir('identificador')
            
            if self.comprobar('separador', ','):
                self.consumir('separador', ',')
            else:
                break

    def consumir_tipo(self):
        if self.comprobar('tipoPrimitivo') or self.comprobar('tipoReferencia'):
            self.avanzar()
        else:
            self.error("Tipo inválido")

    # Métodos auxiliares esenciales
    def comprobar_tipo(self, incluir_void=False):
        if incluir_void:
            return (self.comprobar('tipoPrimitivo') or 
                    self.comprobar('tipoReferencia') or 
                    self.comprobar('tipoRetorno', 'void'))
        else:
            return self.comprobar('tipoPrimitivo') or self.comprobar('tipoReferencia')
    def lista_identificadores(self):
        while True:
            self.consumir('identificador')
            if not self.comprobar('separador', ','):
                break
            self.consumir('separador', ',')

    def consumir(self, tipo, valor=None):
        if self.esta_al_final():
            self.error(f"Se esperaba {tipo} pero se terminó el código")
            return

        token = self.token_actual()
        if token['ID'] != tipo:
            self.error(f"Se esperaba {tipo} pero se encontró {token['ID']}")
            return

        if valor is not None and token['Lexema'] != valor:
            self.error(f"Se esperaba '{valor}' pero se encontró '{token['Lexema']}'")
            return

        self.pos_actual += 1

    def comprobar(self, tipo, valor=None):
        if self.esta_al_final():
            return False
        token = self.token_actual()
        if valor is not None:
            return token['ID'] == tipo and token['Lexema'] == valor
        return token['ID'] == tipo

    def token_actual(self):
        return self.tokens[self.pos_actual] if self.pos_actual < len(self.tokens) else None

    def esta_al_final(self):
        return self.pos_actual >= len(self.tokens)

    def avanzar(self):
        self.pos_actual += 1

    def error(self, mensaje):
        token = self.token_actual() or (self.tokens[-1] if self.tokens else None)
        linea = token['Línea'] if token else 1
        columna = token['Columna'] if token else 1
        error_msg = f"Error sintáctico en línea {linea}, columna {columna}: {mensaje}"
        self.errores.append(error_msg)
        raise ParseError()

class ParseError(Exception):
    pass