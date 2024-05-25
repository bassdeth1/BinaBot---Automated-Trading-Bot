import pandas as pd
import numpy as np

class Estrategia1:
    def __init__(self, client, parameters):
        self.client = client
        self.parameters = parameters

    def run(self, data):
        # Ejemplo de análisis técnico: calcular medias móviles
        data['SMA_20'] = data['close'].rolling(window=20).mean()
        data['SMA_50'] = data['close'].rolling(window=50).mean()
        data['SMA_200'] = data['close'].rolling(window=200).mean()
        
        # Generar señales de compra/venta basadas en medias móviles
        data['Signal'] = np.where(data['SMA_20'] > data['SMA_50'], 'Compra', 'Venta')
        
        return data
