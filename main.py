import json
import time
import os
import sys
from src.market import MarketData
from src.db_manager import DBManager
# Gemini'yi bu modda çağırmıyoruz çünkü JSON'daki hazır etiketi kullanacağız.
# Böylece kota sorunu yaşamayız.

# Dosya Yolları
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_DATA_PATH = os.path.join(BASE_DIR, "data", "large_news.json")
DB_PATH = os.path.join(BASE_DIR, "data", "crypto_logs.db")

def get_db_choice():
    """Kullanıcıya veritabanı modunu sorar."""
    print("\n--- 🛠️ VERİTABANI MODU ---")
    print("1. [TEMİZLE] Veritabanını SİL ve sıfırdan başla.")
    print("2. [EKLE]    Mevcut veritabanına dokunma, SONUNA EKLE.")
    
    while True:
        choice = input("Seçiminiz (1 veya 2): ").strip()
        if choice == '1':
            return 'clean'
        elif choice == '2':
            return 'append'
        print("❌ Hatalı giriş! Sadece 1 veya 2 yazın.")

def get_range_choice(total_count):
    """Kullanıcıya hangi haberleri işleyeceğini sorar."""
    print(f"\n--- 📊 VERİ ARALIĞI (Toplam {total_count} Haber) ---")
    print("1. [HEPSİ]  Listeyi baştan sona işle (1 - 60).")
    print("2. [ARALIK] Belirli bir aralığı işle (Örn: 22 - 60).")
    
    while True:
        choice = input("Seçiminiz (1 veya 2): ").strip()
        if choice == '1':
            return 0, total_count
        elif choice == '2':
            try:
                start = int(input("Başlangıç No (Örn: 22): "))
                end = int(input(f"Bitiş No (Maks {total_count}): "))
                if 1 <= start <= end <= total_count:
                    # Python index 0'dan başlar, o yüzden -1 yapıyoruz
                    return start - 1, end
                else:
                    print(f"❌ Hatalı aralık! 1 ile {total_count} arasında sayı girin.")
            except ValueError:
                print("❌ Lütfen sadece sayı girin.")
        else:
            print("❌ Geçersiz seçim.")

def main():
    print("🚀 SİSTEM BAŞLATILIYOR: Crypto Thesis Veri Yöneticisi")
    print("-" * 50)

    # 1. JSON Verisini Yükle
    try:
        with open(NEWS_DATA_PATH, 'r', encoding='utf-8') as f:
            all_news = json.load(f)
        total_news = len(all_news)
        print(f"📂 Veri seti yüklendi: {total_news} adet haber mevcut.")
    except FileNotFoundError:
        print("❌ Hata: 'data/large_news.json' bulunamadı! Önce generate_dataset.py çalıştır.")
        return

    # 2. Kullanıcıdan Emirleri Al
    db_mode = get_db_choice()
    start_idx, end_idx = get_range_choice(total_news)

    # 3. Veritabanı Temizliği (Eğer istenirse)
    if db_mode == 'clean':
        if os.path.exists(DB_PATH):
            try:
                os.remove(DB_PATH)
                print("\n🗑️  Eski veritabanı silindi. Temiz sayfa açılıyor...")
            except Exception as e:
                print(f"⚠️ Silme hatası: {e}")
    else:
        print("\n🛡️  Mevcut veriler korunuyor, üzerine ekleme yapılacak...")

    # 4. Modülleri Başlat
    try:
        print("🔌 Modüller yükleniyor (Market & DB)...")
        market_bot = MarketData()
        db_bot = DBManager()
        print("✅ Modüller hazır. İşlem Başlıyor!\n")
    except Exception as e:
        print(f"❌ Başlatma Hatası: {e}")
        return

    # Hedef Aralığı Belirle
    target_news = all_news[start_idx:end_idx]
    print(f"🎯 Hedef: {start_idx + 1}. haberden {end_idx}. habere kadar işlenecek.")
    print("-" * 50)

    successful_ops = 0
    
    # 5. Ana Döngü
    for i, item in enumerate(target_news, start_idx + 1):
        # ÖNEMLİ: Gemini yerine JSON içindeki hazır etiketi kullanıyoruz
        sentiment = item.get('expected_sentiment', 'NEUTRAL')
        
        print(f"İşlem {i}: {item['timestamp']}")
        print(f"   📝 Etiket: {sentiment}")
        
        # Piyasa Verisi Çek
        market_result = market_bot.get_price_movement(item['symbol'], item['timestamp'])
        
        if market_result:
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
            print(f"   💾 Kaydedildi. (Fiyat: {market_result['entry_price']})")
        else:
            print("   ⚠️ Piyasa verisi bulunamadı.")

        # Binance'i yormamak için çok kısa bekleme
        time.sleep(1) 
        print("-" * 30)

    print("\n🏁 İŞLEM TAMAMLANDI!")
    print(f"Toplam {successful_ops} adet yeni veri veritabanına eklendi.")
    
    # Son Durumu Göster
    try:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM trades")
        total_in_db = cursor.fetchone()[0]
        print(f"📊 Veritabanındaki Toplam Kayıt Sayısı: {total_in_db}")
        conn.close()
    except:
        pass
        
    db_bot.close()

if __name__ == "__main__":
    main()