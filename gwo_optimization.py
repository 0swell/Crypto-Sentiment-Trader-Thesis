import numpy as np
import sqlite3
import os
import matplotlib.pyplot as plt
import time

# ---  PARAMETRELER (M=10) ---
# 0. Buy Threshold (0.5 - 0.9)
# 1. Sell Threshold (0.1 - 0.5)
# 2. Stop Loss % (0.5 - 5.0)
# 3. Take Profit % (1.0 - 15.0)
# 4. Trailing Stop % (0.1 - 3.0)
# 5. Risk Per Trade % (0.5 - 5.0)
# 6. Max Holding Time (1 - 120 dk)
# 7. Volume Filter (1.0 - 3.0)
# 8. RSI Lower (20 - 40)
# 9. RSI Upper (60 - 80)

LB = [0.5, 0.1, 0.5, 1.0, 0.1, 0.5, 1, 1.0, 20, 60]
UB = [0.9, 0.5, 5.0, 15.0, 3.0, 5.0, 120, 3.0, 40, 80]
DIM = 10 
SEARCH_AGENTS_NO = 60
MAX_ITER = 1000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "crypto_logs.db")

def get_data_from_db():
    """Veritabanındaki işlemleri çeker."""
    if not os.path.exists(DB_PATH):
        print("❌ Veritabanı bulunamadı! Önce main.py çalıştır.")
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT sentiment, entry_price, pnl_percent, news_text FROM trades")
        data = cursor.fetchall()
    except sqlite3.OperationalError:
       
        try:
            cursor.execute("SELECT sentiment, entry_price, pnl, news_text FROM trades")
            data = cursor.fetchall()
        except:
            print("❌ Kritik Hata: Veritabanı sütun isimleri uyuşmuyor.")
            data = []

    conn.close()
    return data

# Veriyi yükle
TRADE_DATA = get_data_from_db()
print(f"✅ {len(TRADE_DATA)} adet geçmiş işlem verisi yüklendi.")

def fitness_function(position):
    """
    AMAÇ FONKSİYONU:
    Parametre setini test eder ve Toplam Kârı döndürür.
    """
    if not TRADE_DATA:
        return -1000
    
    stop_loss_pct = position[2]
    take_profit_pct = position[3]
    risk_per_trade = position[5]
    
    total_profit = 0
    initial_capital = 10000 
    current_capital = initial_capital
    
    for trade in TRADE_DATA:
        sentiment, entry, market_pnl, text = trade
        
        # PnL verisini sayıya çevir
        try:
            if isinstance(market_pnl, str):
                market_pnl_val = float(market_pnl.replace('%', ''))
            else:
                market_pnl_val = float(market_pnl)
        except:
            continue

        actual_trade_pnl = 0

        if sentiment == "POSITIVE":
            # Long Senaryosu
            if market_pnl_val > take_profit_pct:
                actual_trade_pnl = take_profit_pct 
            elif market_pnl_val < -stop_loss_pct:
                actual_trade_pnl = -stop_loss_pct 
            else:
                actual_trade_pnl = market_pnl_val 
                
        elif sentiment == "NEGATIVE":
            
            # Short Senaryosu
            # Short işlemde, piyasa düşerse (market_pnl negatifse) biz kazanırız.
            # Ancak veritabanındaki pnl, "Long açsaydık ne olurdu"yu gösteriyor.
            # O yüzden Short açınca, market_pnl'in tersini (-) kazanırız.
            
            # Örneğin: Piyasa %-5 düştü. Short açan %5 kazanır.
            short_pnl = -1 * market_pnl_val
            
            if short_pnl > take_profit_pct:
                actual_trade_pnl = take_profit_pct
            elif short_pnl < -stop_loss_pct:
                actual_trade_pnl = -stop_loss_pct
            else:
                actual_trade_pnl = short_pnl
        
        else:
            continue 

        # Kasa Hesaplama
        trade_amount = current_capital * (risk_per_trade / 100)
        profit_amount = trade_amount * (actual_trade_pnl / 100)
        current_capital += profit_amount

    return current_capital - initial_capital

def GWO(search_agents_no, max_iter, lb, ub, dim):
    print(f"🐺 GWO Başlatılıyor... | Kurt: {search_agents_no} | İter: {max_iter}")
    
    Alpha_pos = np.zeros(dim)
    Alpha_score = float("-inf")
    
    Beta_pos = np.zeros(dim)
    Beta_score = float("-inf")
    
    Delta_pos = np.zeros(dim)
    Delta_score = float("-inf")
    
    Positions = np.zeros((search_agents_no, dim))
    for i in range(dim):
        Positions[:, i] = np.random.uniform(0, 1, search_agents_no) * (ub[i] - lb[i]) + lb[i]
        
    Convergence_curve = np.zeros(max_iter)
    
    print("⏳ Optimizasyon başladı (RAM üzerinden çalıştığı için hızlıdır)...")
    start_time = time.time()
    
    for l in range(0, max_iter):
        for i in range(0, search_agents_no):
            # Sınır Kontrolü
            for j in range(dim):
                Positions[i, j] = np.clip(Positions[i, j], lb[j], ub[j])
            
            # Fitness
            fitness = fitness_function(Positions[i, :])
            
            # Liderleri Güncelle
            if fitness > Alpha_score:
                Alpha_score = fitness
                Alpha_pos = Positions[i, :].copy()
            elif fitness > Beta_score:
                Beta_score = fitness
                Beta_pos = Positions[i, :].copy()
            elif fitness > Delta_score:
                Delta_score = fitness
                Delta_pos = Positions[i, :].copy()
        
        a = 2 - l * ((2) / max_iter)
        
        # Konum Güncelleme
        for i in range(0, search_agents_no):
            for j in range(0, dim):
                r1, r2 = np.random.random(), np.random.random()
                A1 = 2 * a * r1 - a
                C1 = 2 * r2
                D_alpha = abs(C1 * Alpha_pos[j] - Positions[i, j])
                X1 = Alpha_pos[j] - A1 * D_alpha
                
                r1, r2 = np.random.random(), np.random.random()
                A2 = 2 * a * r1 - a
                C2 = 2 * r2
                D_beta = abs(C2 * Beta_pos[j] - Positions[i, j])
                X2 = Beta_pos[j] - A2 * D_beta
                
                r1, r2 = np.random.random(), np.random.random()
                A3 = 2 * a * r1 - a
                C3 = 2 * r2
                D_delta = abs(C3 * Delta_pos[j] - Positions[i, j])
                X3 = Delta_pos[j] - A3 * D_delta
                
                Positions[i, j] = (X1 + X2 + X3) / 3
        
        Convergence_curve[l] = Alpha_score
        
        if l % 100 == 0:
            print(f"📍 İterasyon {l}: En İyi Kâr = ${Alpha_score:.2f}")

    end_time = time.time()
    print(f"\n✅ Bitti! Süre: {end_time - start_time:.2f} sn")
    return Alpha_pos, Alpha_score, Convergence_curve

if __name__ == "__main__":
    if len(TRADE_DATA) == 0:
        print("❌ Veri yok! Önce main.py çalıştır.")
    else:
        best_pos, best_score, curve = GWO(SEARCH_AGENTS_NO, MAX_ITER, LB, UB, DIM)
        
        print("-" * 50)
        print(f"🏆 EN İYİ ÇÖZÜM (ALPHA KURDU)")
        print(f"💰 Tahmini Kâr: ${best_score:.2f} (Başlangıç: 10.000$)")
        print("-" * 50)
        
        param_names = ["Buy Thresh", "Sell Thresh", "Stop Loss %", "Take Profit %", 
                       "Trailing %", "Risk %", "Time (m)", "Vol Fltr", "RSI Low", "RSI High"]
        
        for i in range(DIM):
            print(f"{i+1}. {param_names[i]}: {best_pos[i]:.4f}")
            
        plt.figure(figsize=(10, 6))
        plt.plot(curve, color='blue', linewidth=2)
        plt.title('GWO Optimizasyon Eğrisi')
        plt.xlabel('İterasyon')
        plt.ylabel('Kasa Büyüklüğü ($)')
        plt.grid(True)
        plt.show()