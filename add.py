import requests
import time
from datetime import datetime
import db_manager  # Senin mevcut db_manager dosyanı import ediyoruz

# Ayarlar
SYMBOL_LIST = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"] # Top 5 Coin (Stable hariç)
INTERVAL = "1h"  # 1 Saatlik veriler
LIMIT = 1000     # Her istekte kaç mum verisi çekilecek (Binance max 1000 verir)
TOTAL_DAYS = 30  # Geriye dönük kaç günlük veri istiyoruz?

def get_binance_data(symbol, interval, limit=1000, start_time=None):
    """Binance API'den mum verilerini çeker"""
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    if start_time:
        params["startTime"] = start_time
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Hata ({symbol}): {e}")
        return []

def fetch_and_store():
    # Veritabanı tablosunu oluştur (Eğer db_manager'da bu kontrol yoksa diye garanti olsun)
    if hasattr(db_manager, 'create_table'):
        db_manager.create_table()
        print("Tablo kontrolü yapıldı.")

    for symbol in SYMBOL_LIST:
        print(f"--- {symbol} verileri çekiliyor ---")
        
        # Şu andan geriye doğru hesaplama (basit mantıkla son 1000 mumu çekelim şimdilik)
        # Daha profesyonel geçmiş veri için döngü kurulabilir ama başlangıç için bu yeterli.
        data = get_binance_data(symbol, INTERVAL, LIMIT)
        
        if not data:
            print(f"{symbol} için veri alınamadı.")
            continue

        count = 0
        for candle in data:
            # Binance formatı: [OpenTime, Open, High, Low, Close, Volume, ...]
            timestamp = int(candle[0])
            open_price = float(candle[1])
            high_price = float(candle[2])
            low_price = float(candle[3])
            close_price = float(candle[4])
            volume = float(candle[5])
            
            # Tarihi okunabilir formata çevir (opsiyonel, log için)
            readable_date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

            # db_manager içindeki ekleme fonksiyonunu çağırıyoruz
            # Not: Senin db_manager.py dosandaki fonksiyon isminin 'add_candle' 
            # veya benzeri bir şey olduğunu varsayıyorum. Lütfen kontrol et.
            try:
                # ÖRNEK FONKSİYON ÇAĞRISI - Kendi db_manager'ına göre burayı düzeltebilirsin
                db_manager.add_candle(symbol, timestamp, open_price, high_price, low_price, close_price, volume)
                count += 1
            except Exception as e:
                print(f"DB Hatası ({symbol}): {e}")
        
        print(f"{symbol} için {count} adet mum verisi eklendi.")
        time.sleep(1) # API limitine takılmamak için kısa bekleme

if __name__ == "__main__":
    print("Veri çekme işlemi başlıyor...")
    fetch_and_store()
    print("İşlem tamamlandı.")