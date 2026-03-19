# ==============================================================================
# ВАЖНО: Эти две строки должны быть САМЫМИ ПЕРВЫМИ.
# Они отключают графический интерфейс и заставляют рисовать прямо в память.
# Это решает проблему с исчезающими окнами на Windows и в облаке.
# ==============================================================================
import matplotlib
matplotlib.use('Agg') 

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import os
from typing import Dict, List, Tuple

print(">>> СИСТЕМА ЗАПУЩЕНА. Инициализация модулей ФСС...")

# ==============================================================================
# ЧАСТЬ 1: ЯДРО ФИЛОСОФИИ СВОБОДНОЙ СУЩНОСТИ (ФСС)
# Реализация онтологической архитектуры: СФД + DE + Операторы
# ==============================================================================

class FSS_Core:
    """
    Ядро системы. Преобразует рыночные данные в онтологические состояния.
    """
    
    def calculate_state_P(self, data: pd.DataFrame) -> Tuple[float, str]:
        """
        P (Состояние): Внутренний потенциал.
        Шкала: Сухое -> Холодное -> Влажное -> Горячее
        """
        close = data['close']
        sma_50 = close.rolling(50).mean()
        current_price = close.iloc[-1]
        
        # Расчет волатильности как меры энергии
        returns = data['close'].pct_change()
        volatility = returns.std() * 100
        
        # Отклонение от средней
        if pd.isna(sma_50.iloc[-1]) or sma_50.iloc[-1] == 0:
            deviation = 0
        else:
            deviation = (current_price - sma_50.iloc[-1]) / sma_50.iloc[-1] * 100
            
        avg_vol = data['volume'].rolling(20).mean().iloc[-1]
        curr_vol = data['volume'].iloc[-1]
        if pd.isna(avg_vol): avg_vol = 1

        # Определение фазы
        if volatility < 1.0 and curr_vol < avg_vol * 0.8:
            return 2.0, "Сухое (Инертность)"
        elif deviation < -2.0:
            return 4.0, "Холодное (Поглощение)"
        elif -2.0 <= deviation <= 2.0:
            return 6.0, "Влажное (Проводимость)"
        else: # deviation > 2.0
            return 9.0, "Горячее (Выделение)"

    def calculate_form_S(self, data: pd.DataFrame) -> Tuple[float, str]:
        """
        S (Форма): Структурная организация.
        Шкала: Неподвижная -> Статичная -> Подвижная -> Нестатичная
        """
        sma_50 = data['close'].rolling(50).mean()
        sma_200 = data['close'].rolling(200).mean()
        last_close = data['close'].iloc[-1]
        s50 = sma_50.iloc[-1]
        s200 = sma_200.iloc[-1]
        
        if pd.isna(s50) or pd.isna(s200):
            return 5.0, "Неопределенная"

        # Проверка на пересечение (Нестатичная)
        if abs(s50 - s200) < (last_close * 0.01):
            return 9.0, "Нестатичная (Трансформация)"
        
        # Проверка тренда
        if (last_close > s50 > s200) or (last_close < s50 < s200):
            if abs(last_close - s50) < (last_close * 0.02):
                return 7.0, "Подвижная (Адаптация)"
            else:
                return 8.0, "Статичная (Устойчивость)"
        else:
            return 3.0, "Неподвижная (Хаос/Флэт)"

    def calculate_action_D(self, data: pd.DataFrame) -> Tuple[float, str]:
        """
        D (Действие): Процесс и взаимодействие.
        Шкала: Распад -> Покой -> Равновесие -> Движение
        """
        vol = data['volume']
        avg_vol = vol.rolling(20).mean()
        current_vol = vol.iloc[-1]
        last_avg = avg_vol.iloc[-1]
        price_change = data['returns'].iloc[-1]
        
        if pd.isna(last_avg):
            return 5.0, "Неопределенное"

        if current_vol > last_avg * 1.8 and price_change < 0:
            return 2.0, "Распад (Паника)"
        elif current_vol < last_avg * 0.6:
            return 3.0, "Покой (Отсутствие интереса)"
        elif abs(price_change) < 0.01 and abs(current_vol - last_avg) < last_avg * 0.2:
            return 6.0, "Равновесие (Баланс)"
        else:
            return 8.0, "Движение (Активность)"

    def calculate_de_factor(self, data: pd.DataFrame) -> Tuple[float, str]:
        """
        DE (Фактор Трансформации): Источник новизны.
        Шкала: Ошибка -> Шум -> Неопределенность -> Напряжение
        """
        volatility = data['returns'].rolling(10).std().iloc[-1] * 100
        mean_20 = data['close'].rolling(20).mean().iloc[-1]
        
        if pd.isna(mean_20) or mean_20 == 0:
            tension = 0
        else:
            tension = abs(data['close'].iloc[-1] - mean_20) / data['close'].iloc[-1] * 100
        
        if volatility < 0.5:
            return 3.0, "Шум (Фон)"
        elif volatility > 3.0 and tension > 2.0:
            return 9.0, "Напряжение (Перед взрывом)"
        elif volatility > 1.5:
            return 6.0, "Неопределенность"
        else:
            return 4.0, "Ошибка (Локальный сбой)"

    def calculate_operators(self, p: float, s: float, d: float, de: float) -> Dict[str, float]:
        """
        Расчет эмерджентных операторов через синергию базовых факторов.
        Любовь (PD), Смысл (SI), Воля (EP), Намерение (NV)
        """
        # Эвристика синергии для демонстрации
        love = (p * 0.3 + (10-s) * 0.3 + (10-d) * 0.2 + (10-de) * 0.2)
        meaning = (p * 0.2 + s * 0.4 + d * 0.2 + (10-de) * 0.2)
        will = (p * 0.3 + s * 0.3 + d * 0.2 + de * 0.2)
        intention = (p * 0.4 + s * 0.3 + d * 0.2 + de * 0.1)
        
        return {
            'Love': min(10.0, max(0.0, love)),
            'Meaning': min(10.0, max(0.0, meaning)),
            'Will': min(10.0, max(0.0, will)),
            'Intention': min(10.0, max(0.0, intention))
        }

    def determine_pattern(self, p: float, s: float, d: float, de: float) -> str:
        """Определение доминирующего паттерна"""
        if p < 4 and s < 4 and d < 4: 
            return 'PD' # Пассивное Доминирование
        if 4 <= p <= 7 and 6 <= s <= 9 and d < 5: 
            return 'SI' # Структурная Интеграция
        if 5 <= p <= 8 and 5 <= s <= 8 and 5 <= d <= 8: 
            return 'EP' # Эмпатическое Проникновение
        if p > 7 and s > 7 and d > 7 and de > 6: 
            return 'NV' # Направленный Взрыв
        return 'MIX'

    def generate_signal(self, pattern: str, ops: Dict[str, float]) -> str:
        """Генерация сигнала на основе операторов"""
        # Немного сниженные пороги для лучшей видимости на тесте
        if pattern == 'PD' and ops['Love'] > 5.5: 
            return 'ACCUMULATE' 
        elif pattern == 'SI' and ops['Meaning'] > 6.5: 
            return 'HOLD' 
        elif pattern == 'EP' and ops['Will'] > 6.0: 
            return 'BUY' 
        elif pattern == 'NV' and ops['Intention'] > 7.5: 
            return 'STRONG_BUY' 
        elif pattern == 'NV' and ops['Intention'] < 4.5: 
            return 'SELL' 
        else: 
            return 'WAIT'

# ==============================================================================
# ЧАСТЬ 2: ПРОЦЕСС АНАЛИЗА И ВИЗУАЛИЗАЦИИ
# ==============================================================================

def run_fss_analysis(ticker: str = 'AAPL', period: str = '2y'):
    print(f"--- ИНИЦИАЛИЗАЦИЯ ФСС: Анализ сущности {ticker} ---")
    
    # 1. СКАЧИВАНИЕ ДАННЫХ (Материя)
    try:
        df = yf.download(ticker, period=period, progress=False)
        if len(df) == 0:
            print("ОШИБКА: Нет данных от Yahoo Finance.")
            return
    except Exception as e:
        print(f"ОШИБКА СЕТИ: {e}")
        return

    # Подготовка данных
    df['returns'] = df['Close'].pct_change()
    df['Volume'] = df['Volume'].fillna(0)
    df['close'] = df['Close']
    df['volume'] = df['Volume']
    
    core = FSS_Core()
    
    # Списки для хранения точек
    buy_points = {'x': [], 'y': []}
    sell_points = {'x': [], 'y': []}
    hold_points = {'x': [], 'y': []}
    
    signal_dates = []
    signals_list = []
    
    print("Запуск процесса РИСЭ (анализ квантов существования)...")
    
    # Начинаем с 200 дня для формирования полных форм
    start_idx = 200
    if len(df) <= start_idx:
        print("ОШИБКА: Недостаточно данных. Нужно больше 200 дней.")
        return

    # Переменная состояния для симуляции торговли
    in_position = False
    entry_price = 0.0

    for i in range(start_idx, len(df)):
        window = df.iloc[i-start_idx:i+1]
        
        # Расчет базовых факторов
        p_score, p_phase = core.calculate_state_P(window)
        s_score, s_phase = core.calculate_form_S(window)
        d_score, d_phase = core.calculate_action_D(window)
        de_score, de_phase = core.calculate_de_factor(window)
        
        # Расчет эмерджентных операторов
        operators = core.calculate_operators(p_score, s_score, d_score, de_score)
        
        # Определение паттерна и сигнала
        pattern = core.determine_pattern(p_score, s_score, d_score, de_score)
        signal = core.generate_signal(pattern, operators)
        
        current_date = df.index[i]
        current_price = df['Close'].iloc[i]
        
        signal_dates.append(current_date)
        signals_list.append(signal)
        
        # Логика сбора точек для графика
        if signal in ['BUY', 'STRONG_BUY', 'ACCUMULATE']:
            buy_points['x'].append(current_date)
            buy_points['y'].append(current_price)
            if not in_position:
                in_position = True
                entry_price = current_price
                
        elif signal == 'SELL':
            sell_points['x'].append(current_date)
            sell_points['y'].append(current_price)
            if in_position:
                in_position = False
                # Здесь можно было бы считать прибыль, но пока просто фиксируем выход

    # Статистика
    print(f"\n--- Анализ завершен. Обработано дней: {len(signal_dates)} ---")
    print(f"Сигналов входа (Зеленые): {len(buy_points['x'])}")
    print(f"Сигналов выхода (Красные): {len(sell_points['x'])}")

    # 2. ВИЗУАЛИЗАЦИЯ (Отражение в форме)
    print("\nГенерация визуального образа (режим Agg)...")
    
    plt.figure(figsize=(15, 8))
    
    # Рисуем линию цены (Поток Энергии)
    plt.plot(df.index, df['Close'], label='Поток Энергии (Цена)', color='#1f77b4', linewidth=1.5, alpha=0.8)
    
    # Точки входа (РЕЗОНАНС)
    if buy_points['x']:
        plt.scatter(buy_points['x'], buy_points['y'], color='#2ca02c', marker='^', s=120, label='РЕЗОНАНС (Вход)', zorder=5, edgecolors='black')
    
    # Точки выхода (ДИССОНАНС)
    if sell_points['x']:
        plt.scatter(sell_points['x'], sell_points['y'], color='#d62728', marker='v', s=120, label='ДИССОНАНС (Выход)', zorder=5, edgecolors='black')

    plt.title(f'Карта Реальности ФСС: {ticker}\nАрхитектура: СФД + РИСЭ + Эмерджентные Операторы', fontsize=14)
    plt.xlabel('Время (Кванты)', fontsize=12)
    plt.ylabel('Уровень Энергии (Цена)', fontsize=12)
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # ЖЕСТКОЕ СОХРАНЕНИЕ В ФАЙЛ
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(script_dir, 'fss_map.png')
    
    try:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print("\n" + "="*60)
        print(">>> УСПЕХ! ГРАФИК СОХРАНЕН В ФАЙЛ:")
        print(f">>> {filename}")
        print("="*60)
        print("\n1. Откройте папку: " + script_dir)
        print("2. Найдите файл 'fss_map.png'")
        print("3. Откройте его как обычную картинку.")
        print("\nПроанализируйте: попадают ли зеленые точки в начало роста?")
    except Exception as e:
        print(f"\n!!! КРИТИЧЕСКАЯ ОШИБКА ПРИ СОХРАНЕНИИ: {e}")
        print("Проверьте права на запись в папку.")
    
    plt.close() # Освобождаем память

if __name__ == "__main__":
    # Запуск анализа для Apple (можно заменить на 'MSFT', 'GOOG', 'BTC-USD')
    run_fss_analysis('AAPL')
    
    # Пауза, чтобы вы успели прочитать текст перед закрытием консоли
    input("\nНажмите Enter, чтобы завершить работу системы...")
