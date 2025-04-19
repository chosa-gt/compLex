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
CONTROL_FLUJO = {'if', 'else', 'switch', 'case', 'default', 'for', 'while', 'do', 'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw', 'throws'}
ORIENTACION_OBJETOS = {'class', 'interface', 'enum', 'extends', 'implements', 'new', 'this', 'super'}
LITERALES_ESPECIALES = {'true', 'false', 'null'}

# Funciones incorporadas
METODOS_ESENCIALES = {'main', 'println', 'print', 'format'}

class ParseError(Exception):
    pass

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
        
        # Herencia e interfaces
        if self.comprobar('palabraReservada', 'extends'):
            self.consumir('palabraReservada', 'extends')
            self.consumir('identificador')
        if self.comprobar('palabraReservada', 'implements'):
            self.consumir('palabraReservada', 'implements')
            self.lista_identificadores()
        
        # Cuerpo de la clase
        self.consumir('separador', '{')
        self.ambito_actual.append('clase')
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
        
        # Tipo de retorno
        if not self.comprobar_tipo(incluir_void=True):
            self.error("Tipo de retorno inválido")
        self.avanzar()
        
        # Nombre del método
        if self.comprobar('metodoEspecial', 'main'):
            self.consumir('metodoEspecial', 'main')
        else:
            self.consumir('identificador')
        
        # Parámetros
        self.consumir('separador', '(')
        self.lista_parametros()
        self.consumir('separador', ')')
        
        # Cuerpo del método
        self.parse_bloque()

    def lista_parametros(self):
        # Analiza parámetros separados por comas
        while not self.comprobar('separador', ')'):
            self.consumir_tipo()
            while self.comprobar('separador', '['):
                self.consumir('separador', '[')
                self.consumir('separador', ']')
            # Nombre del parámetro
            if not (self.comprobar('identificador') or self.comprobar('parametro')):
                self.error("Se esperaba un identificador como nombre del parámetro")
            self.avanzar()
            if self.comprobar('separador', ','):
                self.consumir('separador', ',')

    def lista_identificadores(self):
        while True:
            self.consumir('identificador')
            if not self.comprobar('separador', ','):
                break
            self.consumir('separador', ',')

    def consumir_tipo(self):
        if self.comprobar('tipoPrimitivo') or self.comprobar('tipoReferencia'):
            self.avanzar()
        else:
            self.error("Tipo inválido")

    def comprobar_tipo(self, incluir_void=False):
        if incluir_void:
            return (self.comprobar('tipoPrimitivo') or 
                    self.comprobar('tipoReferencia') or 
                    self.comprobar('tipoRetorno', 'void'))
        return self.comprobar('tipoPrimitivo') or self.comprobar('tipoReferencia')

    # --- Manejo de declaraciones dentro de métodos ---
    def declaracion(self):
        # Determina qué tipo de sentencia hay y la parsea
        if self.comprobar('palabraReservada', 'if'):
            self.sentencia_if()
        elif self.comprobar('palabraReservada', 'for'):
            self.sentencia_for()
        elif self.comprobar('palabraReservada', 'while'):
            self.sentencia_while()
        elif self.comprobar('palabraReservada', 'return'):
            self.sentencia_return()
        else:
            self.sentencia_expresion()

    def parse_bloque(self):
        self.consumir('separador', '{')
        self.ambito_actual.append('bloque')
        while not self.comprobar('separador', '}'):
            self.declaracion()
        self.consumir('separador', '}')
        self.ambito_actual.pop()

    # Sentencias de control y expresiones
    def sentencia_if(self):
        self.consumir('palabraReservada', 'if')
        self.consumir('separador', '(')
        self.sentencia_expresion(inner=True)
        self.consumir('separador', ')')
        self.declaracion()  # cuerpo if
        if self.comprobar('palabraReservada', 'else'):
            self.consumir('palabraReservada', 'else')
            self.declaracion()

    def sentencia_for(self):
        self.consumir('palabraReservada', 'for')
        self.consumir('separador', '(')
        self.sentencia_expresion(inner=True)
        self.consumir('separador', ';')
        self.sentencia_expresion(inner=True)
        self.consumir('separador', ';')
        self.sentencia_expresion(inner=True)
        self.consumir('separador', ')')
        self.declaracion()

    def sentencia_while(self):
        self.consumir('palabraReservada', 'while')
        self.consumir('separador', '(')
        self.sentencia_expresion(inner=True)
        self.consumir('separador', ')')
        self.declaracion()

    def sentencia_return(self):
        self.consumir('palabraReservada', 'return')
        # expresión opcional
        if not self.comprobar('separador', ';'):
            self.sentencia_expresion(inner=True)
        self.consumir('separador', ';')

    def sentencia_expresion(self, inner=False):
        # Consume tokens hasta ; o ) si inner=True
        terminador = ')' if inner else ';'
        while not self.comprobar('separador', terminador) and not self.esta_al_final():
            self.avanzar()
        if not inner:
            self.consumir('separador', ';')

    # --- Métodos auxiliares ---
    def consumir(self, tipo, valor=None):
        if self.esta_al_final():
            self.error(f"Se esperaba {tipo} pero se terminó el código")
            return
        token = self.token_actual()
        if token['ID'] != tipo or (valor is not None and token['Lexema'] != valor):
            esperado = f"{tipo}{' '+valor if valor else ''}".strip()
            encontrado = f"{token['ID']} '{token['Lexema']}'"
            self.error(f"Se esperaba {esperado} pero se encontró {encontrado}")
            return
        self.pos_actual += 1

    def comprobar(self, tipo, valor=None):
        if self.esta_al_final():
            return False
        token = self.token_actual()
        return token['ID'] == tipo and (valor is None or token['Lexema'] == valor)

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
        msg = f"Error sintáctico en línea {linea}, columna {columna}: {mensaje}"
        self.errores.append(msg)
        raise ParseError()


