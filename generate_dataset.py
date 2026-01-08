import json
import random
from datetime import datetime, timedelta
import os

# --- AYARLAR ---
DATA_COUNT = 60  
OUTPUT_FILE = os.path.join("data", "large_news.json")

# Haber Şablonları
NEWS_TEMPLATES = [
    ("SEC, {coin} ETF başvurusunu ertelediğini açıkladı.", "NEGATIVE"),
    ("{coin} ağındaki günlük işlem sayısı rekor kırdı.", "POSITIVE"),
    ("Fed başkanı, faiz indirimlerinin yakında başlayabileceğini ima etti.", "POSITIVE"),
    ("Binance, {coin} çekim işlemlerini geçici olarak durdurdu.", "NEGATIVE"),
    ("Büyük bir balina cüzdanı borsaya 5000 {coin} transfer etti.", "NEGATIVE"),
    ("Teknik göstergeler {coin} için aşırı satım bölgesini işaret ediyor.", "POSITIVE"),
    ("Avrupa Merkez Bankası kripto regülasyonlarını sıkılaştırıyor.", "NEGATIVE"),
    ("{coin} geliştiricileri, ağ güncellemesinin başarılı olduğunu duyurdu.", "POSITIVE"),
    ("Global piyasalardaki belirsizlik, yatırımcıları {coin} gibi varlıklara itiyor.", "POSITIVE"),
    ("Ünlü analist, {coin} için düşüş trendinin devam edeceğini öngördü.", "NEGATIVE")
]

def generate_large_dataset():
    data = []
    # (Binance verisi)
    start_date = datetime(2024, 1, 15)
    
    print(f"🛠️ {DATA_COUNT} adet sentetik haber verisi oluşturuluyor...")
    
    for i in range(1, DATA_COUNT + 1):
        # Rastgele Tarih Seçimi (Her veri arasına 1-3 gün koyalım)
        # Piyasa verisinin kesin olması için saatleri 10:00 - 20:00 arasına sabitliyoruz.
        random_days = i * 2 
        random_hour = random.randint(10, 20)
        random_minute = random.randint(10, 50)
        
        current_date = start_date + timedelta(days=random_days)
        # Saati güncelle
        current_date = current_date.replace(hour=random_hour, minute=random_minute, second=0)
        
        date_str = current_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # Rastgele Coin ve Haber Seçimi
        coin = "BTC" if random.random() > 0.4 else "ETH" # %60 BTC, %40 ETH
        template, expected_sentiment = random.choice(NEWS_TEMPLATES)
        text = template.format(coin=coin)
        
        entry = {
            "id": i,
            "timestamp": date_str,
            "symbol": f"{coin}USDT",
            "text": text,
            "expected_sentiment": expected_sentiment
        }
        data.append(entry)

    # Dosyayı Kaydet
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ BAŞARILI: Veriler '{OUTPUT_FILE}' dosyasına kaydedildi.")
    except Exception as e:
        print(f"❌ HATA: Dosya oluşturulamadı. {e}")

if __name__ == "__main__":
    generate_large_dataset()