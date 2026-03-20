# ВАЖНО: Режим отрисовки без окна
import matplotlib
matplotlib.use('Agg')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import timedelta

print(">>> ЗАПУСК ФСС v5.0: Генерация синтетической реальности (Исправление Series)...")

# ==============================================================================
# ГЕНЕРАТОР ДАННЫХ (Вместо yfinance)
# Создаем математическую модель рынка, похожую на AAPL
# ==============================================================================
def generate_synthetic_data(days=600):
    np.random.seed(42) 
    start_date = pd.Timestamp('2024-01-01')
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    # Генерируем цену как случайное блуждание с трендом
    returns = np.random.normal(loc=0.0005, scale=0.02, size=days)
    price = 150 * np.cumprod(1 + returns)
    
    # Генерируем объем
    base_volume = 1000000
    volume = base_volume + np.abs(np.random.normal(0, 200000, size=days)) + \
             np.abs(returns) * 5000000
    
    df = pd.DataFrame({
        'Date': dates,
        'Close': price,
        'Volume': volume
    })
    df.set_index('Date', inplace=True)
    df['returns'] = df['Close'].pct_change().fillna(0)
    
    return df

# ==============================================================================
# ЯДРО ФСС (ИСПРАВЛЕННАЯ ЛОГИКА СКАЛЯРОВ)
# ==============================================================================
class FSS_Core:
    def calculate_state_P(self, data):
        # Извлекаем ТОЛЬКО последние значения как обычные числа (float)
        current_price = float(data['close'].iloc[-1])
        
        # Считаем SMA вручную для последнего элемента, чтобы избежать Series
        sma_50_val = float(data['close'].rolling(50).mean().iloc[-1])
        
        volatility = float(data['returns'].std() * 100)
        
        avg_vol = float(data['volume'].rolling(20).mean().iloc[-1])
        curr_vol = float(data['volume'].iloc[-1])
        
        # Защита от деления на ноль
        if sma_50_val == 0 or np.isnan(sma_50_val):
            deviation = 0.0
        else:
            deviation = (current_price - sma_50_val) / sma_50_val * 100
            
        if np.isnan(avg_vol): avg_vol = 1.0
        if np.isnan(curr_vol): curr_vol = 1.0
        if np.isnan(volatility): volatility = 0.0

        # Теперь сравнения работают ТОЛЬКО с числами
        if volatility < 1.0 and curr_vol < avg_vol * 0.8: 
            return 2.0 # Сухое
        elif deviation < -2.0: 
            return 4.0 # Холодное
        elif -2.0 <= deviation <= 2.0: 
            return 6.0 # Влажное
        else: 
            return 9.0 # Горячее

    def calculate_form_S(self, data):
        # Извлекаем скаляры
        last_close = float(data['close'].iloc[-1])
        s50 = float(data['close'].rolling(50).mean().iloc[-1])
        s200 = float(data['close'].rolling(200).mean().iloc[-1])
        
        if np.isnan(s50) or np.isnan(s200): 
            return 5.0

        # Сравнения только чисел
        if abs(s50 - s200) < (last_close * 0.01): 
            return 9.0 # Нестатичная
        elif (last_close > s50 and s50 > s200) or (last_close < s50 and s50 < s200):
            if abs(last_close - s50) < (last_close * 0.02): 
                return 7.0 # Подвижная
            else: 
                return 8.0 # Статичная
        else: 
            return 3.0 # Неподвижная

    def calculate_action_D(self, data):
        # Извлекаем скаляры
        current_vol = float(data['volume'].iloc[-1])
        last_avg = float(data['volume'].rolling(20).mean().iloc[-1])
        price_change = float(data['returns'].iloc[-1])
        
        if np.isnan(last_avg): 
            return 5.0

        # Сравнения только чисел
        if current_vol > last_avg * 1.8 and price_change < 0: 
            return 2.0 # Распад
        elif current_vol < last_avg * 0.6: 
            return 3.0 # Покой
        elif abs(price_change) < 0.01 and abs(current_vol - last_avg) < last_avg * 0.2: 
            return 6.0 # Равновесие
        else: 
            return 8.0 # Движение

    def calculate_de_factor(self, data):
        volatility = float(data['returns'].rolling(10).std().iloc[-1] * 100)
        mean_20 = float(data['close'].rolling(20).mean().iloc[-1])
        current_price = float(data['close'].iloc[-1])
        
        if np.isnan(mean_20) or mean_20 == 0: 
            tension = 0.0
        else: 
            tension = abs(current_price - mean_20) / current_price * 100
        
        if np.isnan(volatility): volatility = 0.0
        
        if volatility < 0.5: return 3.0
        elif volatility > 3.0 and tension > 2.0: return 9.0
        elif volatility > 1.5: return 6.0
        else: return 4.0

    def calculate_operators(self, p, s, d, de):
        love = (p * 0.3 + (10-s) * 0.3 + (10-d) * 0.2 + (10-de) * 0.2)
        meaning = (p * 0.2 + s * 0.4 + d * 0.2 + (10-de) * 0.2)
        will = (p * 0.3 + s * 0.3 + d * 0.2 + de * 0.2)
        intention = (p * 0.4 + s * 0.3 + d * 0.2 + de * 0.1)
        return {'Love': min(10, love), 'Meaning': min(10, meaning), 'Will': min(10, will), 'Intention': min(10, intention)}

    def determine_pattern(self, p, s, d, de):
        if p < 4 and s < 4 and d < 4: return 'PD'
        if 4 <= p <= 7 and 6 <= s <= 9 and d < 5: return 'SI'
        if 5 <= p <= 8 and 5 <= s <= 8 and 5 <= d <= 8: return 'EP'
        if p > 7 and s > 7 and d > 7 and de > 6: return 'NV'
        return 'MIX'

    def generate_signal(self, pattern, ops, in_position, current_price, entry_price):
        if not in_position:
            if pattern == 'PD' and ops['Love'] > 5.5: return 'BUY'
            if pattern == 'EP' and ops['Will'] > 6.0: return 'BUY'
            if pattern == 'NV' and ops['Intention'] > 7.5: return 'BUY'
        
        if in_position:
            if pattern == 'NV' and ops['Intention'] < 4.5: return 'SELL'
            if pattern == 'PD' and ops['Love'] < 4.0: return 'SELL'
            if current_price < entry_price * 0.95: return 'SELL_STOP'
            if current_price > entry_price * 1.15 and ops['Will'] < 5.0: return 'SELL_PROFIT'
            
        return 'HOLD'

# ==============================================================================
# ЗАПУСК
# ==============================================================================
def run_fss_analysis():
    print("--- ГЕНЕРАЦИЯ СИНТЕТИЧЕСКОГО РЫНКА ---")
    df = generate_synthetic_data(600)
    
    # Переименуем колонки для удобства внутри класса
    df['close'] = df['Close']
    df['volume'] = df['Volume']
    
    core = FSS_Core()
    
    buy_points = {'x': [], 'y': []}
    sell_points = {'x': [], 'y': []}
    
    in_position = False
    entry_price = 0.0
    trades_count = 0
    total_profit_pct = 0.0
    
    print("Обработка квантов существования...")
    
    for i in range(200, len(df)):
        # Берем окно данных
        window = df.iloc[i-200:i+1]
        
        # Расчет факторов
        p = core.calculate_state_P(window)
        s = core.calculate_form_S(window)
        d = core.calculate_action_D(window)
        de = core.calculate_de_factor(window)
        ops = core.calculate_operators(p, s, d, de)
        pattern = core.determine_pattern(p, s, d, de)
        
        current_price = float(df['Close'].iloc[i])
        signal = core.generate_signal(pattern, ops, in_position, current_price, entry_price)
        
        if signal == 'BUY':
            in_position = True
            entry_price = current_price
            buy_points['x'].append(df.index[i])
            buy_points['y'].append(current_price)
            
        elif signal in ['SELL', 'SELL_STOP', 'SELL_PROFIT']:
            if in_position:
                profit_pct = ((current_price - entry_price) / entry_price) * 100
                total_profit_pct += profit_pct
                trades_count += 1
                in_position = False
                entry_price = 0.0
                sell_points['x'].append(df.index[i])
                sell_points['y'].append(current_price)

    print("\n" + "="*40)
    print(f"ВСЕГО СДЕЛОК: {trades_count}")
    print(f"СУММАРНАЯ ДОХОДНОСТЬ: {total_profit_pct:.2f}%")
    print("="*40)

    # Отрисовка
    plt.figure(figsize=(15, 8))
    plt.plot(df.index, df['Close'], label='Синтетический Поток (Цена)', color='#1f77b4', linewidth=1.5)
    
    if buy_points['x']:
        plt.scatter(buy_points['x'], buy_points['y'], color='#2ca02c', marker='^', s=150, label='РЕЗОНАНС (Вход)', zorder=5, edgecolors='black')
    
    if sell_points['x']:
        plt.scatter(sell_points['x'], sell_points['y'], color='#d62728', marker='v', s=150, label='ДИССОНАНС (Выход)', zorder=5, edgecolors='black')
        
    title_text = f'Карта Реальности ФСС (Синтетика)\nДоходность: {total_profit_pct:.2f}%'
    plt.title(title_text)
    plt.xlabel('Время (Кванты)')
    plt.ylabel('Уровень Энергии (Цена)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(script_dir, 'fss_synthetic_map.png')
    
    try:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"\n>>> УСПЕХ! ГРАФИК СОХРАНЕН:")
        print(f">>> {filename}")
        print("\nОткройте этот файл, чтобы увидеть результат.")
    except Exception as e:
        print(f"Ошибка сохранения: {e}")
    
    plt.close()

if __name__ == "__main__":
    run_fss_analysis()
    input("\nНажмите Enter для завершения...")
