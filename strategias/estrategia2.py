def estrategia(data):
    # Ejemplo simple de estrategia
    # Vender si el cierre es menor que la apertura
    return data['close'] < data['open']
