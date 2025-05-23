import time
import numpy as np
from binance.client import Client

# test de mise à jour à partir du Raspberry
# Remplacez par vos clés API Binance
api_key = 'VOTRE_API_KEY'
api_secret = 'VOTRE_SECRET_API'
client = Client(api_key, api_secret)

# Paramètres
symbol = "ETHUSDT"
interval = Client.KLINE_INTERVAL_1SECOND
token_quantity = 2

# Variables
position = None
historical_data = []
initial_price = None
cumulative_pnl = 0
transaction_count = 0

# Fonctions utilitaires
def get_new_data():
    klines = client.get_klines(symbol=symbol, interval=interval, limit=1)
    return float(klines[0][4])  # prix de clôture

def calculate_moving_average(data, period):
    if len(data) < period:
        return None
    return np.mean(data[-period:])

def is_increasing(ma_values):
    return len(ma_values) >= 2 and ma_values[-1] > ma_values[-2]

def is_decreasing(ma_values):
    return len(ma_values) >= 2 and ma_values[-1] < ma_values[-2]

# Décision de trading
def trade_decision(current_price, mms_2_list, mms_5_list, mms_20_list):
    global position, initial_price, cumulative_pnl, transaction_count

    # Vérifie qu'on a les dernières valeurs
    if None in (mms_2_list[-1], mms_5_list[-1], mms_20_list[-1]):
        return

    # Conditions d'entrée
    C1 = mms_5_list[-1] > mms_20_list[-1]
    C2 = len(mms_2_list) >= 3 and mms_2_list[-3] is not None and mms_2_list[-2] is not None and mms_2_list[-1] is not None and mms_2_list[-3] > mms_2_list[-2] < mms_2_list[-1]
    C3 = current_price > mms_5_list[-1]

    # Conditions de sortie (on vérifie qu'il y a assez de valeurs non-None)
    C4 = False
    C5 = False
    if len(mms_5_list) >= 2 and len(mms_20_list) >= 2:
        if mms_5_list[-2] is not None and mms_20_list[-2] is not None:
            C4 = mms_5_list[-2] > mms_20_list[-2] and mms_5_list[-1] < mms_20_list[-1]
        if mms_5_list[-2] is not None:
            C5 = mms_5_list[-2] > mms_5_list[-1]

    # Entrée en position
    if position != 'buy' and C1 and C2 and C3:
        print(f"Achat de {token_quantity} tokens à {current_price}")
        position = 'buy'
        initial_price = current_price

    # Sortie de position
    elif position == 'buy' and (C4 or C5):
        pnl = (current_price - initial_price) * token_quantity
        cumulative_pnl += pnl
        transaction_count += 1
        print(f"Vente de {token_quantity} tokens à {current_price} | PnL de la transaction : {pnl:.2f}")
        print(f"Gains/Pertes cumulés après {transaction_count} transactions : {cumulative_pnl:.2f}")
        position = None


# Boucle principale
def real_time_simulation():
    global historical_data
    mms_2_list, mms_5_list, mms_20_list = [], [], []

    print("Démarrage de la simulation en temps réel...")
    while True:
        current_price = get_new_data()
        historical_data.append(current_price)

        # Calcul des MMS
        mms_2 = calculate_moving_average(historical_data, 2)
        mms_5 = calculate_moving_average(historical_data, 5)
        mms_20 = calculate_moving_average(historical_data, 20)

        mms_2_list.append(mms_2)
        mms_5_list.append(mms_5)
        mms_20_list.append(mms_20)

        print(f"Prix actuel : {current_price} | MMS5 : {mms_5} | MMS20 : {mms_20}")

        trade_decision(current_price, mms_2_list, mms_5_list, mms_20_list)

        time.sleep(1)

# Exécuter la simulation
real_time_simulation()
