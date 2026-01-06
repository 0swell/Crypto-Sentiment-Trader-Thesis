from binance.client import Client
from datetime import datetime, timedelta
import pandas as pd

class MarketData:
    def __init__(self):
        """
        Binance istemcisini başlatır.
        Halka açık veri (Fiyatlar) için API Key gerekmez.
        """
        self.client = Client()

    def get_price_movement(self, symbol, news_time_str):
        """
        Verilen sembol ve tarih için giriş ve çıkış fiyatlarını getirir.
        
        Args:
            symbol (str): 'BTCUSDT' gibi.
            news_time_str (str): '2024-01-10 21:00:00' formatında tarih.
            
        Returns:
            dict: {Giriş Fiyatı, Çıkış Fiyatı, Yüzdesel Değişim}
        """
        try:
            # 1. String tarihi datetime objesine çevir
            # Haber saati bizim için "Giriş Saati"dir.
            start_time = datetime.strptime(news_time_str, "%Y-%m-%d %H:%M:%S")
            
            # 2. Bitiş saati (1 dakika sonrası)
            # Binance'e "Bana bu 2 dakikalık aralığı ver" diyeceğiz.
            end_time = start_time + timedelta(minutes=2) 

            # 3. Binance API'si için tarihi string formatına geri çevir veya timestamp yap
            # python-binance '1 Jan, 2024' gibi formatları da anlar ama en garantisi timestamp'tir.
            start_str = str(int(start_time.timestamp() * 1000))
            end_str = str(int(end_time.timestamp() * 1000))

            # 4. Mum verilerini (Klines) çek
            # Interval: 1M (1 Dakika)
            klines = self.client.get_klines(
                symbol=symbol,
                interval=Client.KLINE_INTERVAL_1MINUTE,
                startTime=start_str,
                endTime=end_str,
                limit=2 # Bize sadece giriş anı ve sonraki dakika lazım
            )

            if not klines or len(klines) < 2:
                print(f"Veri eksik: {news_time_str} için fiyat bulunamadı.")
                return None

            # Binance Kline Formatı: [Open time, Open, High, Low, Close, Volume, ...]
            # 0. index -> Haberin geldiği dakika (Giriş)
            # 1. index -> Bir sonraki dakika (Çıkış)
            
            # Strateji: Haberin geldiği mumun AÇILIŞ fiyatından giriyoruz.
            entry_candle = klines[0]
            entry_price = float(entry_candle[1]) # Open Price
            
            # Strateji: Bir sonraki mumun AÇILIŞ fiyatından çıkıyoruz (1 dk tutmuş oluyoruz).
            exit_candle = klines[1]
            exit_price = float(exit_candle[1]) # Open Price (of next candle)

            # 5. Kâr/Zarar Hesabı (Yüzde)
            pnl_percent = ((exit_price - entry_price) / entry_price) * 100

            return {
                "entry_price": entry_price,
                "exit_price": exit_price,
                "pnl": pnl_percent
            }

        except Exception as e:
            print(f"Piyasa Verisi Hatası: {e}")
            return None

# --- TEST BLOĞU ---
if __name__ == "__main__":
    market = MarketData()
    test_time = "2024-01-10 22:00:00" # ETF Onay günü
    print(f"Tarih: {test_time} için BTC fiyatı çekiliyor...")
    
    result = market.get_price_movement("BTCUSDT", test_time)
    
    if result:
        print(f"Giriş Fiyatı: ${result['entry_price']}")
        print(f"Çıkış Fiyatı: ${result['exit_price']}")
        print(f"Değişim: %{result['pnl']:.4f}")
    else:
        print("Test başarısız.")