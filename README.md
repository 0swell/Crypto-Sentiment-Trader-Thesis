# Kripto Para Piyasalarında GWO Destekli Ticaret Stratejisi (v0.3)

Bu proje, 50 boyutlu Gri Kurt Optimizasyonu (GWO) algoritması kullanarak 5 farklı kripto para birimi (BTC, ETH, BNB, SOL, XRP) için en uygun teknik analiz parametrelerini belirleyen bir yapay zeka sistemidir.

**Versiyon:** 0.3 (Kararlı Optimizasyon Sürümü)

## 🚀 Kurulum

1. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt 

   or
   
   #python -m pip install -r requirements.txt 


   Veri Çekme: Binance üzerinden geçmiş verileri çekmek için:

Bash

python add.py
Optimizasyon (Eğitim): Yapay zekayı çalıştırıp en iyi parametreleri bulmak için:

Bash

python main.py
Bu işlem sonucunda best_results.json dosyası ve yakınsama grafiği oluşturulur.

Raporlama: Bulunan karmaşık parametreleri okunabilir rapora çevirmek için:

Bash

python report.py