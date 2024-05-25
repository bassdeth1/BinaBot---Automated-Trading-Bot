# BinaBot – Automated Trading Bot (under construction)

## Description
BinaBot is an automated trading bot designed to operate in the cryptocurrency market using advanced technical strategies. This bot connects to the Binance API to obtain real-time market data and execute buy and sell orders based on technical analysis.

### Features
- Connects to Binance API for real-time data.
- Implementation of customizable trading strategies.
- Detection of buy and sell opportunities using technical indicators.
- Logging of results and analysis in JSON and HTML files.
- Real-time notifications about new buying opportunities.

## Requirements
- Python 3.8+
- Flask
- Flask-SocketIO
- CCXT
- Pandas
- Binance Client

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/your_user/BinaBot.git
    ```
2. Navigate to the project directory:
    ```sh
    cd BinaBot
    ```
3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration
1. Configure the Binance API credentials and other parameters in the `config.json` file:
    ```json
    {
        "api_key": "YOUR_API_KEY",
        "api_secret": "YOUR_API_SECRET",
        "telegram_api_key": "YOUR_TELEGRAM_API_KEY",
        "telegram_chat_id": "YOUR_TELEGRAM_CHAT_ID",
        "selected_strategy": "estrategia1",
        "strategies": [
            "estrategia1",
            "estrategia2",
            "estrategia3"
        ],
        "parameters": {
            "interval": "30m",
            "start_date": "",
            "end_date": ""
        },
        "filters": {
            "min_duration_days": 60,
            "min_volatility": 0.01,
            "min_volume": 1000.0
        }
    }
    ```

## Usage
1. Start the Flask application:
    ```sh
    python app.py
    ```
2. Open your browser and navigate to `http://localhost:5000` to access the bot control panel.

## Copyright
© 2024 Agustín Arellano. All rights reserved.


# BinaBot - Bot de Trading Automatizado (en proceso de construcciòn)

## Descripción
BinaBot es un bot de trading automatizado diseñado para operar en el mercado de criptomonedas utilizando estrategias técnicas avanzadas. Este bot se conecta a la API de Binance para obtener datos de mercado en tiempo real y ejecutar órdenes de compra y venta basadas en análisis técnicos.

### Funcionalidades
- Conexión a la API de Binance para datos en tiempo real.
- Implementación de estrategias de trading personalizables.
- Detección de oportunidades de compra y venta mediante indicadores técnicos.
- Registro de resultados y análisis en archivos JSON y HTML.
- Notificaciones en tiempo real sobre nuevas oportunidades de compra.

## Requisitos
- Python 3.8+
- Flask
- Flask-SocketIO
- CCXT
- Pandas
- Binance Client

## Instalación
1. Clona el repositorio:
    ```sh
    git clone https://github.com/tu_usuario/BinaBot.git
    ```
2. Navega al directorio del proyecto:
    ```sh
    cd BinaBot
    ```
3. Instala las dependencias:
    ```sh
    pip install -r requirements.txt
    ```

## Configuración
1. Configura las credenciales de la API de Binance y otros parámetros en el archivo `config.json`:
    ```json
    {
        "api_key": "TU_API_KEY",
        "api_secret": "TU_API_SECRET",
        "telegram_api_key": "TU_TELEGRAM_API_KEY",
        "telegram_chat_id": "TU_TELEGRAM_CHAT_ID",
        "selected_strategy": "estrategia1",
        "strategies": [
            "estrategia1",
            "estrategia2",
            "estrategia3"
        ],
        "parameters": {
            "interval": "30m",
            "start_date": "",
            "end_date": ""
        },
        "filters": {
            "min_duration_days": 60,
            "min_volatility": 0.01,
            "min_volume": 1000.0
        }
    }
    ```

## Uso
1. Inicia la aplicación Flask:
    ```sh
    python app.py
    ```
2. Abre tu navegador y navega a `http://localhost:5000` para acceder al panel de control del bot.

## Copyright
© 2024 Agustín Arellano. Todos los derechos reservados.

