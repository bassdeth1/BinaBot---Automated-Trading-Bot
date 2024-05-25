import os
import threading
import json
import asyncio
from flask import Flask, render_template, request, jsonify, redirect, url_for
import config
import utils
import importlib
import pandas as pd
from binance import AsyncClient, BinanceSocketManager

app = Flask(__name__)

RESULTS_FILE = 'results.json'

# Variables globales para almacenar los resultados del análisis y el bloqueo para acceder a ellos
analysis_results = []
results_lock = threading.Lock()

def load_analysis_results():
    global analysis_results
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            analysis_results = json.load(f)
            print("Resultados cargados:", analysis_results)

def save_analysis_results():
    global analysis_results
    with results_lock:
        with open(RESULTS_FILE, 'w') as f:
            json.dump(analysis_results, f, indent=4)
            print("Resultados guardados:", analysis_results)

async def analyze_pair(pair, interval, strategy_name, parameters):
    try:
        print(f"Analizando el par: {pair} con intervalo: {interval}")
        data = await utils.get_market_data_websocket(symbol=pair, interval=interval)
        strategy_module = importlib.import_module(f'strategias.{strategy_name}')
        strategy_class = getattr(strategy_module, strategy_name.capitalize())
        strategy_instance = strategy_class(client=None, parameters=parameters)
        result = strategy_instance.run(data)
        if isinstance(result, pd.DataFrame):
            signal_data = result[result['Signal'] == 'Compra']
            if not signal_data.empty:
                last_signal = signal_data.iloc[-1].to_dict()
                last_signal['pair'] = pair
                last_signal['timestamp'] = signal_data.index[-1].strftime("%Y-%m-%d %H:%M:%S")
                print(f"Oportunidad de compra encontrada: {last_signal}")
                with results_lock:
                    analysis_results.append(last_signal)
                    save_analysis_results()
                return last_signal
        else:
            print(f"El resultado de la estrategia no es un DataFrame para {pair}")
    except Exception as e:
        print(f"Error al analizar el par {pair}: {e}")
    return None

async def analyze_pairs():
    global analysis_results
    config_data = config.load_config()
    strategy_name = config_data['selected_strategy']
    interval = config_data['parameters']['interval']
    filters = config_data['filters']

    # Obtener la lista de pares USDT desde la WebSocket de Binance
    client = await AsyncClient.create()
    exchange_info = await client.get_exchange_info()
    usdt_pairs = [s['symbol'] for s in exchange_info['symbols'] if s['quoteAsset'] == 'USDT']
    await client.close_connection()

    # Aplicar filtros
    usdt_pairs = await utils.apply_filters(usdt_pairs, filters)

    tasks = [analyze_pair(pair, interval, strategy_name, config_data['parameters']) for pair in usdt_pairs]
    results = await asyncio.gather(*tasks)

    results = [result for result in results if result]
    results = sorted(results, key=lambda x: x['timestamp'], reverse=True)
    
    with results_lock:
        analysis_results.extend(results)
        save_analysis_results()
        print(f"Resultados actualizados: {analysis_results}")

async def start_analysis_loop():
    while True:
        await analyze_pairs()
        await asyncio.sleep(60)  # Espera 60 segundos antes de realizar el próximo análisis

# Inicia el loop asincrónico en un hilo separado
def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_analysis_loop())

load_analysis_results()  # Cargar resultados guardados al iniciar

# Crear y iniciar el loop asincrónico
loop = asyncio.new_event_loop()
t = threading.Thread(target=start_async_loop, args=(loop,), daemon=True)
t.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    if request.method == 'POST':
        config_data = config.load_config()
        
        config_data['api_key'] = request.form.get('api_key', config_data['api_key'])
        config_data['api_secret'] = request.form.get('api_secret', config_data['api_secret'])
        config_data['telegram_api_key'] = request.form.get('telegram_api_key', config_data['telegram_api_key'])
        config_data['telegram_chat_id'] = request.form.get('telegram_chat_id', config_data['telegram_chat_id'])
        config_data['selected_strategy'] = request.form.get('selected_strategy', config_data['selected_strategy'])
        
        # Extraer y asignar parámetros correctamente
        config_data['parameters']['interval'] = request.form.get('parameters[interval]', config_data['parameters']['interval'])
        config_data['parameters']['start_date'] = request.form.get('parameters[start_date]', config_data['parameters']['start_date'])
        config_data['parameters']['end_date'] = request.form.get('parameters[end_date]', config_data['parameters']['end_date'])

        # Extraer y asignar filtros correctamente
        config_data['filters']['min_duration_days'] = int(request.form.get('filters[min_duration_days]', config_data['filters']['min_duration_days']))
        config_data['filters']['min_volatility'] = float(request.form.get('filters[min_volatility]', config_data['filters']['min_volatility']))
        config_data['filters']['min_volume'] = float(request.form.get('filters[min_volume]', config_data['filters']['min_volume']))
        
        config.save_config(config_data)
        return redirect(url_for('configuracion'))
    
    config_data = config.load_config()
    return render_template('configuracion.html', config=config_data)

@app.route('/analyze', methods=['GET'])
def analyze():
    symbol = request.args.get('symbol')
    
    chart_data = {}

    if symbol:
        config_data = config.load_config()
        strategy_name = config_data['selected_strategy']
        interval = config_data['parameters']['interval']
        
        data = asyncio.run(utils.get_market_data_websocket(symbol=symbol, interval=interval))
        strategy_module = importlib.import_module(f'strategias.{strategy_name}')
        strategy_class = getattr(strategy_module, strategy_name.capitalize())
        strategy_instance = strategy_class(client=None, parameters=config_data['parameters'])
        result = strategy_instance.run(data)
        if isinstance(result, pd.DataFrame):
            chart_data = result.to_dict(orient='list')
    
    with results_lock:
        results = analysis_results.copy()

    return render_template('analysis.html', result=results, chart_data=chart_data)

@app.route('/clear_analysis', methods=['POST'])
def clear_analysis():
    global analysis_results
    with results_lock:
        analysis_results = []
        save_analysis_results()
    return redirect(url_for('analyze'))

@app.route('/get_new_opportunities', methods=['GET'])
def get_new_opportunities():
    with results_lock:
        results = analysis_results.copy()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
