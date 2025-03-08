def analizar_codigo(codigo):
    # Aquí va la lógica del analizador léxico
    # Por ejemplo, podrías retornar una lista de diccionarios con los resultados
    resultados = [
        {"ID": 1, "Lexema": "int", "Línea": 1, "Columna": 1, "Patrón": "tipo", "Reservada": True},
        {"ID": 2, "Lexema": "main", "Línea": 1, "Columna": 5, "Patrón": "identificador", "Reservada": False},
        # Agrega más resultados según sea necesario
    ]
    return resultados