import json

# --- AYARLAR ---
COINS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]

def decode_params(params):
    """
    0-1 arasındaki ham sayıları gerçek indikatör değerlerine çevirir.
    (main.py içindeki formüllerin aynısıdır)
    """
    decoded = {}
    
    # 1. RSI Ayarları
    decoded['RSI Periyodu'] = int(params[0] * 16) + 4
    decoded['RSI Al Seviyesi'] = int(params[1] * 30) + 20
    decoded['RSI Sat Seviyesi'] = int(params[2] * 30) + 60
    
    # 2. MACD Ayarları
    decoded['MACD Hızlı'] = int(params[3] * 10) + 8
    decoded['MACD Yavaş'] = int(params[4] * 15) + 19
    decoded['MACD Sinyal'] = int(params[5] * 8) + 5
    
    # 3. Risk Yönetimi
    decoded['Stop Loss (%)'] = round((params[6] * 0.15 + 0.01) * 100, 2)
    decoded['Take Profit (%)'] = round((params[7] * 0.30 + 0.02) * 100, 2)
    
    # 4. Genel Strateji
    decoded['SMA Trend Filtresi'] = int(params[8] * 150) + 20
    decoded['İşlem Başı Bütçe (%)'] = round((params[9] * 0.9 + 0.1) * 100, 2)
    
    return decoded

def generate_report():
    try:
        with open("best_results.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Hata: 'best_results.json' bulunamadı. Önce main.py'yi çalıştırın.")
        return

    best_score = data["best_score"]
    best_params = data["best_params"]
    
    print("="*60)
    print(f"      50 BOYUTLU OPTİMİZASYON SONUÇ RAPORU")
    print(f"      Toplam Portföy Kârı: ${best_score:.2f}")
    print("="*60)
    
    # 50 parametreyi 5 coine böl (10'arlı paketler)
    for i, symbol in enumerate(COINS):
        start_index = i * 10
        end_index = start_index + 10
        
        # O coin'e ait 10 parametreyi al
        coin_raw_params = best_params[start_index:end_index]
        
        # Okunabilir hale getir
        readable_params = decode_params(coin_raw_params)
        
        print(f"\n🔹 {symbol} İÇİN OPTİMİZE EDİLEN STRATEJİ:")
        print("-" * 40)
        for key, value in readable_params.items():
            print(f"{key:<25}: {value}")
        print("-" * 40)

if __name__ == "__main__":
    generate_report()