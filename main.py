import json
import time
import os
import pandas as pd
from src.sentiment import GeminiClient
from src.market import MarketData
from src.db_manager import DBManager

# Dosya yollarını ayarla
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_DATA_PATH = os.path.join(BASE_DIR, "data", "mock_news.json")

def main():
    print("🚀 SİSTEM BAŞLATILIYOR: Crypto Thesis Bot V1.0 (Rate Limit Korumalı)")
    print("-" * 50)

    # 1. Modülleri Başlat (Init)
    try:
        print("🔌 Modüller yükleniyor...")
        ai_bot = GeminiClient()
        market_bot = MarketData()
        db_bot = DBManager()
        print("✅ Tüm modüller hazır!\n")
    except Exception as e:
        print(f"❌ Başlatma Hatası: {e}")
        return

    # 2. Haber Verisini Yükle (JSON)
    try:
        with open(NEWS_DATA_PATH, 'r', encoding='utf-8') as f:
            news_list = json.load(f)
        print(f"📂 {len(news_list)} adet haber yüklendi. İşlem başlıyor...\n")
    except FileNotFoundError:
        print("❌ Hata: 'data/mock_news.json' bulunamadı!")
        return

    # 3. Ana Döngü (Pipeline)
    successful_ops = 0
    
    for i, item in enumerate(news_list, 1):
        print(f"Flux {i}/{len(news_list)}: {item['timestamp']} işleniyor...")
        
        # --- ADIM A: Yapay Zeka Analizi ---
        sentiment = ai_bot.analyze_text(item['text'])
        print(f"   🧠 AI Kararı: {sentiment}")
        
        # --- ADIM B: Piyasa Verisi Çekme ---
        if sentiment == "NEUTRAL":
            print("   ⏩ Nötr haber, işlem yapılmadı.")
        else: 
            market_result = market_bot.get_price_movement(item['symbol'], item['timestamp'])
            
            if market_result:
                # --- ADIM C: Veritabanına Kayıt ---
                trade_record = {
                    "timestamp": item['timestamp'],
                    "symbol": item['symbol'],
                    "news_text": item['text'],
                    "sentiment": sentiment,
                    "entry_price": market_result['entry_price'],
                    "exit_price": market_result['exit_price'],
                    "pnl": market_result['pnl']
                }
                
                db_bot.save_trade(trade_record)
                successful_ops += 1
            else:
                print("   ⚠️ Piyasa verisi bulunamadı.")

        # --- GÜNCELLEME: RATE LIMIT KORUMASI ---
        # Dakikada 5 istek sınırını aşmamak için her turda 15 saniye bekliyoruz.
        print("⏳ API kotası için 15 saniye bekleniyor...")
        time.sleep(15) 
        print("-" * 30)

    # 4. Raporlama
    print("\n🏁 İŞLEM TAMAMLANDI!")
    print(f"Toplam {successful_ops} adet işlem veritabanına kaydedildi.")
    
    print("\n📊 ÖZET TABLO:")
    df = db_bot.get_results_as_dataframe()
    
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    # Sadece son eklenenleri gösterelim ki tablo taşmasın
    print(df[['timestamp', 'sentiment', 'entry_price', 'pnl_percent', 'success']].tail(10))

    db_bot.close()

if __name__ == "__main__":
    main()