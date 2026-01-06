import google.generativeai as genai
import time
import sys
import os

# Üst klasördeki config.py'yi görebilmek için yol ayarı
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class GeminiClient:
    def __init__(self):
        """
        Gemini API bağlantısını başlatır.
        """
        if not config.GEMINI_API_KEY:
            raise ValueError("API Key bulunamadı! Lütfen config.py dosyasını kontrol edin.")
            
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)

    def analyze_text(self, text):
        """
        Verilen haber metnini analiz eder ve duygu durumunu döndürür.
        Çıktı: 'POSITIVE', 'NEGATIVE' veya 'NEUTRAL'
        """
        prompt = f"""
        Sen uzman bir kripto para finansal analistisin. 
        Aşağıdaki haberi kripto piyasası (özellikle Bitcoin veya ilgili altcoinler) üzerindeki etkisi açısından analiz et.
        
        Haber: "{text}"
        
        Cevap olarak SADECE aşağıdaki üç kelimeden birini ver (Başka hiçbir şey yazma):
        POSITIVE
        NEGATIVE
        NEUTRAL
        """
        
        try:
            # API'ye isteği gönder
            response = self.model.generate_content(prompt)
            
            # Gelen cevabı temizle (boşlukları sil, büyük harf yap)
            sentiment = response.text.strip().upper()
            
            # Güvenlik kontrolü: İstenmeyen bir cevap geldiyse NEUTRAL dön
            valid_responses = ["POSITIVE", "NEGATIVE", "NEUTRAL"]
            if sentiment not in valid_responses:
                # Bazen model "This is Positive" diyebilir, içinden kelimeyi ayıklayalım
                for valid in valid_responses:
                    if valid in sentiment:
                        return valid
                return "NEUTRAL" # Hiçbirini bulamazsa risk alma
                
            return sentiment

        except Exception as e:
            print(f"Gemini API Hatası: {e}")
            # Hata durumunda sistemi durdurmamak için NEUTRAL dönelim
            return "NEUTRAL"

# --- TEST BLOĞU ---
# Bu dosyayı doğrudan çalıştırırsan (python src/sentiment.py) bu kısım çalışır.
if __name__ == "__main__":
    client = GeminiClient()
    test_news = "Elon Musk, Tesla'nın tüm Bitcoin varlıklarını sattığını açıkladı."
    print(f"Test Haberi: {test_news}")
    print("Analiz yapılıyor...")
    result = client.analyze_text(test_news)
    print(f"Sonuç: {result}")