import os
import threading
import json
import asyncio
from flask import Flask, render_template, request, jsonify, redirect, url_for
import config
import utils
import importlib
import pandas as pd
from binance import AsyncClient

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
                    save_analysis_results()  # Asegurarse de guardar los resultados después de cada hallazgo
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
    analyzed_pairs = config_data.get('analyzed_pairs', [])

    tasks = [analyze_pair(pair, interval, strategy_name, config_data['parameters']) for pair in analyzed_pairs]
    results = await asyncio.gather(*tasks)

    results = [result for result in results if result]
    results = sorted(results, key=lambda x: x['timestamp'], reverse=True)
    
    with results_lock:
        analysis_results.extend(results)
        save_analysis_results()  # Guardar todos los resultados después de analizarlos
        print(f"Resultados actualizados: {analysis_results}")

async def start_analysis_loop():
    while True:
        await analyze_pairs()
        print("Ciclo de análisis completado, iniciando de nuevo.")
        await asyncio.sleep(1)  # Espera 1 segundo antes de empezar el siguiente ciclo de análisis

# Inicia el loop asincrónico en un hilo separado
def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_analysis_loop())

load_analysis_results()  # Cargar resultados guardados al iniciar

# Crear y iniciar el loop asincrónico
loop = asyncio.new_event_loop()
t = threading.Thread(target=start_async_loop, args=(loop,), daemon=True)
t.start()

def get_available_pairs():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = loop.run_until_complete(AsyncClient.create())
    exchange_info = loop.run_until_complete(client.get_exchange_info())
    available_pairs = sorted([s['symbol'] for s in exchange_info['symbols'] if s['quoteAsset'] == 'USDT'])
    loop.run_until_complete(client.close_connection())
    return available_pairs

def apply_filters(pairs, filter_settings):
    # Lógica para aplicar filtros a la lista de pares
    filtered_pairs = pairs.copy()

    # Filtro de Edad
    if int(filter_settings['AgeFilter']['min_days_listed']) > 0:
        min_days_listed = int(filter_settings['AgeFilter']['min_days_listed'])
        filtered_pairs = [pair for pair in filtered_pairs if pair_meets_age_criteria(pair, min_days_listed)]

    # Agrega más lógica para otros filtros aquí...

    return filtered_pairs

def pair_meets_age_criteria(pair, min_days_listed):
    # Lógica para verificar si el par cumple con el criterio de antigüedad
    return True  # Este es solo un ejemplo, implementa la lógica adecuada

@app.route('/')
def index():
    config_data = config.load_config()
    available_pairs = get_available_pairs()
    filter_settings = config_data['filter_settings']
    filtered_pairs = apply_filters(available_pairs, filter_settings)
    analyzed_pairs = config_data.get('analyzed_pairs', [])
    return render_template('index.html', available_pairs=filtered_pairs, analyzed_pairs=analyzed_pairs, filter_settings=filter_settings)

@app.route('/add_pairs', methods=['POST'])
def add_pairs():
    pairs = request.json.get('pairs', [])
    config_data = config.load_config()
    analyzed_pairs = config_data.get('analyzed_pairs', [])
    analyzed_pairs.extend(pairs)
    config_data['analyzed_pairs'] = sorted(list(set(analyzed_pairs)))
    config.save_config(config_data)
    return jsonify({"status": "success"})

@app.route('/remove_pairs', methods=['POST'])
def remove_pairs():
    pairs = request.json.get('pairs', [])
    config_data = config.load_config()
    analyzed_pairs = config_data.get('analyzed_pairs', [])
    analyzed_pairs = [pair for pair in analyzed_pairs if pair not in pairs]
    config_data['analyzed_pairs'] = analyzed_pairs
    config.save_config(config_data)
    return jsonify({"status": "success"})

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

        # Guardar la configuración de los filtros
        filter_settings = config_data['filter_settings']
        for method, settings in filter_settings.items():
            for key in settings.keys():
                value = request.form.get(f"{method}_{key}", settings[key])
                if key == "sort_key":
                    filter_settings[method][key] = value  # Mantener como cadena de texto
                else:
                    try:
                        value = str(value)  # Asegurarse de que el valor es una cadena antes de buscar un punto
                        if "." in value:
                            filter_settings[method][key] = float(value)
                        else:
                            filter_settings[method][key] = int(value)
                    except ValueError:
                        filter_settings[method][key] = value  # Mantener como cadena de texto en caso de error
        config_data['filter_settings'] = filter_settings
        
        config.save_config(config_data)
        return redirect(url_for('configuracion'))
    
    config_data = config.load_config()
    return render_template('configuracion.html', config=config_data)

@app.route('/clear_analysis', methods=['POST'])
def clear_analysis():
    global analysis_results
    with results_lock:
        analysis_results = []
        save_analysis_results()
    return redirect(url_for('index'))

@app.route('/get_new_opportunities', methods=['GET'])
def get_new_opportunities():
    with results_lock:
        results = analysis_results.copy()
    return jsonify(results)

@app.route('/analysis', methods=['GET'])
def analysis():
    with results_lock:
        results = analysis_results.copy()
    return render_template('analysis.html', result=results)

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "running"}), 200

if __name__ == '__main__':
    app.run(debug=True)
