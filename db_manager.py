import sqlite3

# Veritabanı dosyasının adı
DB_NAME = "crypto_data.db"

def create_connection():
    """Veritabanına bağlanır veya yoksa oluşturur."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        return conn
    except sqlite3.Error as e:
        print(f"Bağlantı hatası: {e}")
    return conn

def create_table():
    """Tabloyu oluşturur (Eğer yoksa)"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            # 5 farklı coin olacağı için 'symbol' kolonu kritik
            sql_create_candles_table = """
                CREATE TABLE IF NOT EXISTS candles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    UNIQUE(symbol, timestamp)
                );
            """
            cursor.execute(sql_create_candles_table)
            conn.commit()
            print("Tablo başarıyla oluşturuldu/kontrol edildi.")
        except sqlite3.Error as e:
            print(f"Tablo oluşturma hatası: {e}")
        finally:
            conn.close()
    else:
        print("Veritabanı bağlantısı kurulamadı.")

def add_candle(symbol, timestamp, open_p, high_p, low_p, close_p, volume_p):
    """Yeni bir mum verisi ekler"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = ''' INSERT OR IGNORE INTO candles(symbol, timestamp, open, high, low, close, volume)
                      VALUES(?,?,?,?,?,?,?) '''
            cursor.execute(sql, (symbol, timestamp, open_p, high_p, low_p, close_p, volume_p))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Veri ekleme hatası: {e}")
        finally:
            conn.close()

# Bu dosya doğrudan çalıştırılırsa tabloyu oluştursun
if __name__ == "__main__":
    create_table()