def estrategia(data):
    # Ejemplo simple de estrategia
    # Comprar si el volumen es mayor que un umbral
    return data['volume'] > 1000
