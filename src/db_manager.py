import sqlite3
import pandas as pd
import os

class DBManager:
    def __init__(self, db_name="crypto_logs.db"):
        """
        Veritabanı bağlantısını kurar ve tabloyu oluşturur.
        Veritabanı dosyasını 'data/' klasörüne kaydeder.
        """
        # Proje ana dizinini bul
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(base_dir, "data", db_name)
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """
        Eğer tablo yoksa analiz için gerekli sütunlarla oluşturur.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                news_text TEXT,
                sentiment TEXT,
                entry_price REAL,
                exit_price REAL,
                pnl_percent REAL,
                success INTEGER
            )
        ''')
        self.conn.commit()

    def save_trade(self, trade_data):
        """
        Tek bir işlem sonucunu veritabanına kaydeder.
        
        Args:
            trade_data (dict): Tüm verileri içeren sözlük.
        """
        # Başarı Durumu (Labeling):
        # Eğer Sentiment Pozitif ise ve PnL > 0 ise -> Başarılı (1)
        # Eğer Sentiment Negatif ise ve PnL < 0 ise -> Başarılı (1) (Short işlem mantığı)
        # Diğer durumlar başarısız (0)
        is_success = 0
        pnl = trade_data['pnl']
        sentiment = trade_data['sentiment']
        
        if (sentiment == "POSITIVE" and pnl > 0) or \
           (sentiment == "NEGATIVE" and pnl < 0):
            is_success = 1
            
        self.cursor.execute('''
            INSERT INTO trades (timestamp, symbol, news_text, sentiment, entry_price, exit_price, pnl_percent, success)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_data['timestamp'],
            trade_data['symbol'],
            trade_data['news_text'],
            trade_data['sentiment'],
            trade_data['entry_price'],
            trade_data['exit_price'],
            trade_data['pnl'],
            is_success
        ))
        self.conn.commit()
        print(f"💾 Kayıt Başarılı: {sentiment} | PnL: %{pnl:.2f}")

    def get_results_as_dataframe(self):
        """
        Tüm veriyi Pandas DataFrame olarak döner (Analiz için).
        """
        return pd.read_sql_query("SELECT * FROM trades", self.conn)

    def close(self):
        self.conn.close()

# --- TEST BLOĞU ---
if __name__ == "__main__":
    db = DBManager()
    
    # Sahte bir veri ile test edelim
    dummy_data = {
        "timestamp": "2024-01-01 12:00:00",
        "symbol": "BTCUSDT",
        "news_text": "Test Haberi: Bitcoin yükseliyor.",
        "sentiment": "POSITIVE",
        "entry_price": 50000.0,
        "exit_price": 50500.0,
        "pnl": 1.0
    }
    
    print("Veritabanı testi yapılıyor...")
    db.save_trade(dummy_data)
    
    print("\n--- Kayıtlı Veriler ---")
    df = db.get_results_as_dataframe()
    print(df)
    
    db.close()