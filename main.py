import numpy as np
import pandas as pd
import random
import db_manager
import matplotlib.pyplot as plt
import json

# --- AYARLAR ---
COINS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
DIMENSIONS = 50   # 5 Coin x 10 Parametre
WOLVES_COUNT = 5  # Popülasyon sayısı (Hız için düşük tuttuk, artırılabilir)
ITERATIONS = 10   # Döngü sayısı

class TradingSystem:
    def __init__(self):
        self.data_store = {}
        self.load_all_data()

    def load_all_data(self):
        """Veritabanından tüm coin verilerini çeker"""
        print("Veriler yükleniyor...")
        conn = db_manager.create_connection()
        cursor = conn.cursor()
        
        for symbol in COINS:
            # Timestamp, Open, High, Low, Close, Volume
            cursor.execute("SELECT timestamp, open, high, low, close, volume FROM candles WHERE symbol=? ORDER BY timestamp ASC", (symbol,))
            rows = cursor.fetchall()
            
            if not rows:
                print(f"UYARI: {symbol} için veri bulunamadı!")
                self.data_store[symbol] = pd.DataFrame()
                continue
            
            # Pandas DataFrame'e çeviriyoruz (Hesaplamalar kolay olsun diye)
            df = pd.DataFrame(rows, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            self.data_store[symbol] = df
            print(f"{symbol}: {len(df)} mum yüklendi.")
        
        conn.close()

    def calculate_indicators(self, df, rsi_period, macd_fast, macd_slow, macd_signal, sma_period):
        """Dinamik olarak indikatörleri hesaplar"""
        # RSI Hesaplama
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # MACD Hesaplama
        ema_fast = df['close'].ewm(span=macd_fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=macd_slow, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=macd_signal, adjust=False).mean()

        # SMA (Trend Filtresi)
        df['sma_trend'] = df['close'].rolling(window=sma_period).mean()
        
        return df

    def backtest_coin(self, symbol, params):
        """
        Tek bir coin için 10 parametre ile gelişmiş test yapar.
        """
        original_df = self.data_store.get(symbol)
        if original_df is None or original_df.empty:
            return 0 

        # DataFrame'in kopyasını al (Orijinal veriyi bozmamak için)
        df = original_df.copy()

        # --- 1. PARAMETRELERİ ÇÖZÜMLEME (0-1 arasından gerçeğe dönüştürme) ---
        rsi_period  = int(params[0] * 16) + 4       # 4 - 20 arası
        rsi_buy     = int(params[1] * 30) + 20      # 20 - 50 arası (RSI < bu ise AL)
        rsi_sell    = int(params[2] * 30) + 60      # 60 - 90 arası (RSI > bu ise SAT)
        
        macd_fast   = int(params[3] * 10) + 8       # 8 - 18 arası
        macd_slow   = int(params[4] * 15) + 19      # 19 - 34 arası
        macd_sig    = int(params[5] * 8) + 5        # 5 - 13 arası
        
        stop_loss_pct = params[6] * 0.15 + 0.01     # %1 - %16 Stop Loss
        take_profit_pct = params[7] * 0.30 + 0.02   # %2 - %32 Take Profit
        
        sma_trend   = int(params[8] * 150) + 20     # 20 - 170 mumluk Trend Filtresi
        wallet_pct  = params[9] * 0.9 + 0.1         # Kasadan %10 - %100 arası kullanım
        
        # --- 2. İNDİKATÖRLERİ HESAPLA ---
        df = self.calculate_indicators(df, rsi_period, macd_fast, macd_slow, macd_sig, sma_trend)
        
        # --- 3. AL-SAT SİMÜLASYONU ---
        balance = 1000 # Başlangıç Dolar
        position_size = 0 # Elimdeki Coin Adedi
        in_position = False
        entry_price = 0

        # İndikatörler oluşana kadar baştaki verileri atla
        start_index = max(sma_trend, macd_slow) + 5
        
        # Pandas iterrows yavaştır ama anlaşılırdır, tez için yeterli.
        # Hızlandırmak için numpy array kullanılabilir ama şimdilik logic önemli.
        for i in range(start_index, len(df)):
            current_price = df['close'].iloc[i]
            current_rsi = df['rsi'].iloc[i]
            current_macd = df['macd'].iloc[i]
            current_signal = df['macd_signal'].iloc[i]
            trend_filter = df['sma_trend'].iloc[i]
            
            # --- ALIM KOŞULLARI ---
            # 1. Pozisyonda değilsek
            # 2. RSI AL seviyesinin altındaysa (Aşırı satım)
            # 3. MACD sinyali yukarı kestiyse
            # 4. Fiyat Trendin (SMA) üstündeyse (Yükseliş trendindeyiz demek)
            if not in_position:
                if (current_rsi < rsi_buy) and (current_macd > current_signal) and (current_price > trend_filter):
                    # Alım Yap
                    trade_amount = balance * wallet_pct
                    position_size = trade_amount / current_price
                    balance -= trade_amount
                    entry_price = current_price
                    in_position = True
            
            # --- SATIŞ KOŞULLARI ---
            elif in_position:
                # 1. Stop Loss Oldu mu?
                if current_price <= entry_price * (1 - stop_loss_pct):
                    balance += position_size * current_price
                    in_position = False
                
                # 2. Take Profit Oldu mu?
                elif current_price >= entry_price * (1 + take_profit_pct):
                    balance += position_size * current_price
                    in_position = False
                    
                # 3. İndikatör Sat Verdi mi? (RSI Tepe yaptıysa)
                elif current_rsi > rsi_sell:
                    balance += position_size * current_price
                    in_position = False

        # Son durumda elimde coin kaldıysa nakite dön
        if in_position:
            balance += position_size * df['close'].iloc[-1]
            
        return balance - 1000  # Net Kâr
    
    def evaluate_fitness(self, total_params):
        """
        50 Boyutlu vektörü alır, parçalar ve toplam skoru hesaplar.
        """
        total_score = 0
        
        for i, symbol in enumerate(COINS):
            start_index = i * 10
            end_index = start_index + 10
            
            coin_params = total_params[start_index:end_index]
            
            # O coin için backtest yap
            score = self.backtest_coin(symbol, coin_params)
            total_score += score
            
        return total_score

# --- GREY WOLF OPTIMIZER (Basitleştirilmiş) ---
class GWO:
    def __init__(self, obj_func, dim, pop_size, max_iter):
        self.obj_func = obj_func
        self.dim = dim
        self.pop_size = pop_size
        self.max_iter = max_iter
        
        # Kurtları (Çözümleri) Rastgele Başlat [0, 1] arasında
        self.positions = np.random.uniform(0, 1, (pop_size, dim))
        self.alpha_pos = np.zeros(dim)
        self.alpha_score = -float("inf") 
        
        # Grafik için skor geçmişini tutacak liste
        self.convergence_curve = [] 

    def optimize(self):
        print(f"\nOptimizasyon Başlıyor: {self.dim} Boyut, {self.pop_size} Kurt...")
        
        for it in range(self.max_iter):
            # Her kurdun skorunu hesapla
            for i in range(self.pop_size):
                # Sınır kontrolü (Parametreler 0-1 dışına çıkmasın)
                self.positions[i] = np.clip(self.positions[i], 0, 1)
                
                fitness = self.obj_func(self.positions[i])
                
                # Alpha (En iyi) güncellemesi
                if fitness > self.alpha_score:
                    self.alpha_score = fitness
                    self.alpha_pos = self.positions[i].copy()
            
            # Bu turdaki en iyi skoru kaydet
            self.convergence_curve.append(self.alpha_score)
            print(f"Iterasyon {it+1}: En İyi Skor: ${self.alpha_score:.2f}")

            # GWO Matematiksel Güncelleme
            a = 2 - it * (2 / self.max_iter) 
            
            for i in range(self.pop_size):
                r1 = np.random.random()
                r2 = np.random.random()
                A1 = 2 * a * r1 - a
                C1 = 2 * r2
                
                D_alpha = abs(C1 * self.alpha_pos - self.positions[i])
                X1 = self.alpha_pos - A1 * D_alpha
                
                # Pozisyonu güncelle (Basit GWO mantığı)
                self.positions[i] = X1 
                
        return self.alpha_pos, self.alpha_score, self.convergence_curve

# --- ÇALIŞTIRMA ---
if __name__ == "__main__":
    # 1. Sistemi Kur
    system = TradingSystem()
    
    # 2. Optimizasyonu Başlat
    # Daha iyi sonuç görmek istersen iterasyonu 20 veya 30 yapabilirsin
    optimizer = GWO(system.evaluate_fitness, dim=DIMENSIONS, pop_size=WOLVES_COUNT, max_iter=ITERATIONS)
    
    # optimize() artık 3 değer döndürüyor: pozisyon, skor ve grafik verisi
    best_params, best_score, curve = optimizer.optimize()
    
    print("\n--- SONUÇLAR ---")
    print(f"En İyi Toplam Kâr: ${best_score:.2f}")
    
    # 3. Sonuçları Kaydet (JSON formatında)
    result_data = {
        "best_score": best_score,
        "best_params": best_params.tolist() # Numpy array'i listeye çevir
    }
    
    with open("best_results.json", "w") as f:
        json.dump(result_data, f)
    print("En iyi parametreler 'best_results.json' dosyasına kaydedildi.")

    # 4. Başarı Grafiğini Çiz (Tez için en önemli kısım)
    plt.figure(figsize=(10, 6))
    plt.plot(curve, marker='o', color='b', linestyle='-')
    plt.title('GWO Optimizasyon Süreci (Convergence Curve)')
    plt.xlabel('İterasyon Sayısı')
    plt.ylabel('Toplam Portföy Kârı ($)')
    plt.grid(True)
    plt.show()