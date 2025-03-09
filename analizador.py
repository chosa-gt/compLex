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

def analizar_codigo(codigo):
    diccionario = cargar_diccionario('tabla_signos_java.txt')
    # Aquí va la lógica del analizador léxico utilizando el diccionario
    resultados = []
    # Ejemplo de cómo podrías usar el diccionario para analizar el código
    for palabra in codigo.split():
        for entrada in diccionario:
            if palabra == entrada["lexema"]:
                resultados.append({
                    "ID": len(resultados) + 1,
                    "Lexema": entrada["lexema"],
                    "Línea": 1,  # Esto es solo un ejemplo, deberías calcular la línea real
                    "Columna": 1,  # Esto es solo un ejemplo, deberías calcular la columna real
                    "Patrón": entrada["nombre"],
                    "Reservada": entrada["palabraReservada"]
                })
    return resultados