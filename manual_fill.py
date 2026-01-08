import json
import time
import os
import sys
from src.market import MarketData
from src.db_manager import DBManager

# Dosya Yolları
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_DATA_PATH = os.path.join(BASE_DIR, "data", "large_news.json")
DB_PATH = os.path.join(BASE_DIR, "data", "crypto_logs.db")

def main():
    print("🚀 SİSTEM BAŞLATILIYOR: Manuel Veri Yükleme (Hızlı Mod)")
    print("-" * 50)

    # 1. TEMİZLİK: Veritabanını sıfırdan kuralım (En temiz yöntem)
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("🗑️  Eski/Hatalı veritabanı silindi.")
        except Exception as e:
            print(f"⚠️ Dosya silinemedi (Açık olabilir): {e}")

    # 2. Modülleri Başlat 
    try:
        print("🔌 Modüller yükleniyor (Market & DB)...")
        market_bot = MarketData()
        db_bot = DBManager() # Tabloyu sıfırdan oluşturur
        print("✅ Modüller hazır.\n")
    except Exception as e:
        print(f"❌ Başlatma Hatası: {e}")
        return

    # 3. JSON Verisini Yükle
    try:
        with open(NEWS_DATA_PATH, 'r', encoding='utf-8') as f:
            news_list = json.load(f)
        print(f"📂 {len(news_list)} adet etiketli veri bulundu. İşleniyor...\n")
    except FileNotFoundError:
        print("❌ Hata: 'data/large_news.json' bulunamadı!")
        return

    successful_ops = 0
    
    # 4. Hızlı Döngü
    for i, item in enumerate(news_list, 1):
        # Gemini'ye sormuyoruz, JSON'daki hazır etiketi alıyoruz
        sentiment = item.get('expected_sentiment', 'NEUTRAL')
        
        print(f"İşlem {i}/{len(news_list)}: {item['timestamp']}")
        print(f"   📝 Etiket: {sentiment}")
        
        # Piyasa Verisi Çek
        market_result = market_bot.get_price_movement(item['symbol'], item['timestamp'])
        
        if market_result:
            # Kayıt Oluştur
            trade_record = {
                "timestamp": item['timestamp'],
                "symbol": item['symbol'],
                "news_text": item['text'],
                "sentiment": sentiment, # Hazır etiket
                "entry_price": market_result['entry_price'],
                "exit_price": market_result['exit_price'],
                "pnl": market_result['pnl']
            }
            
            db_bot.save_trade(trade_record)
            successful_ops += 1
        else:
            print("   ⚠️ Piyasa verisi bulunamadı (Tarih çok eski/hatalı olabilir).")

        # Binance'e çok yüklenmemek için minik bir bekleme 
        time.sleep(1) 
        print("-" * 30)

    print("\n🏁 İŞLEM TAMAMLANDI!")
    print(f"Toplam {successful_ops} adet veri başarıyla veritabanına işlendi.")
    db_bot.close()

if __name__ == "__main__":
    main()