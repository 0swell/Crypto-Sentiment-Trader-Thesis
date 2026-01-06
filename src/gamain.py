import pygad
import numpy as np
import time
import matplotlib.pyplot as plt

# ---  PARAMETRELER (M=10) ---
# Genetik Algoritmanın optimize edeceği 10 karar değişkeni:
# Gen 0: Buy Threshold (AI Skoru > 0.X ise AL) [0.5 - 0.99]
# Gen 1: Sell Threshold (AI Skoru < 0.X ise SAT) [0.1 - 0.5]
# Gen 2: Stop Loss % (Zarar Kes) [0.5 - 5.0]
# Gen 3: Take Profit % (Kâr Al) [1.0 - 15.0]
# Gen 4: Trailing Stop % (İzleyen Durdurma) [0.1 - 3.0]
# Gen 5: Max Holding Time (Dakika) [1 - 120]
# Gen 6: RSI Lower Limit (Filtre) [20 - 40]
# Gen 7: RSI Upper Limit (Filtre) [60 - 80]
# Gen 8: Volume Multiplier (Hacim Çarpanı) [1.0 - 5.0]
# Gen 9: Risk Per Trade % (Kasa Yönetimi) [1.0 - 10.0]

GEN_SAYISI_M = 10 

# --- SİMÜLASYON VERİSİ (HIZLI TEST İÇİN) ---
# Normalde buraya veritabanından çektiğimiz geçmiş veriyi koyacağız.
# Şimdilik algoritma çalışsın diye rastgele bir fiyat listesi uyduruyoruz.
simulated_market_data = np.random.uniform(low=40000, high=45000, size=100) # 100 dakikalık fiyat

def fitness_func(ga_instance, solution, solution_idx):
    """
    AMAÇ FONKSİYONU:
    Verilen 10 parametreyi (solution) kullanarak simülasyon yapar.
    Sonuçta elde edilen TOPLAM KÂR ne kadar yüksekse, fitness o kadar yüksek olur.
    Hoca 'Minimize' dediği için, Kârı negatife çevirip minimize etmeyi hedefleyebiliriz.
    """
    
    # 1. Genleri Değişkenlere Ata
    buy_thresh = solution[0]
    stop_loss = solution[2]
    take_profit = solution[3]
    # ... diğer genler de burada işleme alınır ...
    
    # 2. Basit Simülasyon (Backtest Mantığı)
    # Bu kısım normalde çok detaylı olacak, şimdilik basit bir matematiksel model kuruyorum.
    # Örnek: Eğer Buy Threshold yüksekse ve Stop Loss düşükse puan ver.
    
    # (Temsili Skor Hesabı - İleride Gerçek Backtest Gelecek)
    # Bu formül tamamen algoritmanın çalışıp çalışmadığını test etmek içindir.
    score = (buy_thresh * 100) + (take_profit * 2) - (stop_loss * 5)
    
    # PyGAD varsayılan olarak MAXIMIZE eder.
    # Eğer minimize etmek istiyorsak: 1.0 / (score + 0.0001) veya -score kullanabiliriz.
    # Şimdilik biz KÂRI MAKSimize etmeye odaklanalım (PyGAD default).
    
    return score

def on_generation(ga_instance):
    """Her jenerasyon bittiğinde çalışır (İlerleme Çubuğu gibi)"""
    print(f"Jenerasyon {ga_instance.generations_completed} | En İyi Fitness: {ga_instance.best_solution()[1]:.4f}")

def main_optimizer():
    print("🧬 GENETİK ALGORİTMA OPTİMİZASYONU BAŞLIYOR...")
    print(f"Hedef: {GEN_SAYISI_M} adet parametreyi optimize etmek.")
    
    # Genlerin alabileceği değer aralıkları (Space Boundaries)
    # 10 gen için sırasıyla min ve max değerler:
    gene_space = [
        {'low': 0.5, 'high': 0.99}, # Gen 0: Buy Threshold
        {'low': 0.1, 'high': 0.5},  # Gen 1: Sell Threshold
        {'low': 0.5, 'high': 5.0},  # Gen 2: Stop Loss
        {'low': 1.0, 'high': 15.0}, # Gen 3: Take Profit
        {'low': 0.1, 'high': 3.0},  # Gen 4: Trailing Stop
        {'low': 1, 'high': 120},    # Gen 5: Time
        {'low': 20, 'high': 40},    # Gen 6: RSI Low
        {'low': 60, 'high': 80},    # Gen 7: RSI High
        {'low': 1.0, 'high': 5.0},  # Gen 8: Volume
        {'low': 1.0, 'high': 10.0}  # Gen 9: Risk
    ]

    # --- AYARLAR ---
    ga_instance = pygad.GA(
        num_generations=1000,       # Hoca: 1000 İterasyon
        num_parents_mating=10,      # Eşleşecek ebeveyn sayısı
        fitness_func=fitness_func,
        sol_per_pop=60,             # Hoca: 60 Popülasyon
        num_genes=GEN_SAYISI_M,     # Hoca: M=10
        gene_space=gene_space,
        parent_selection_type="rws",# Rulet Tekerleği Seçimi
        crossover_type="uniform",
        mutation_type="random",
        mutation_percent_genes=10,  # Genlerin %10'u mutasyona uğrasın
        on_generation=on_generation
    )

    # Algoritmayı Çalıştır
    start_time = time.time()
    ga_instance.run()
    end_time = time.time()

    # --- SONUÇLARI RAPORLA ---
    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    
    print("\n" + "="*40)
    print("🏆 OPTİMİZASYON TAMAMLANDI")
    print("="*40)
    print(f"Süre: {end_time - start_time:.2f} saniye")
    print(f"En İyi Fitness Skoru: {solution_fitness:.4f}")
    print("-" * 30)
    print("💎 BULUNAN EN İYİ PARAMETRELER (KROMOZOM):")
    print(f"1.  Buy Threshold  : {solution[0]:.4f}")
    print(f"2.  Sell Threshold : {solution[1]:.4f}")
    print(f"3.  Stop Loss %    : {solution[2]:.2f}")
    print(f"4.  Take Profit %  : {solution[3]:.2f}")
    print(f"5.  Trailing Stop %: {solution[4]:.2f}")
    print(f"6.  Max Time (dk)  : {solution[5]:.0f}")
    print(f"7.  RSI Low        : {solution[6]:.0f}")
    print(f"8.  RSI High       : {solution[7]:.0f}")
    print(f"9.  Volume Mult    : {solution[8]:.2f}")
    print(f"10. Risk %         : {solution[9]:.2f}")
    print("="*40)

    # --- GRAFİK ---
    print("📈 Grafik çiziliyor...")
    ga_instance.plot_fitness(title="İterasyon vs Fitness (Kâr) Grafiği")

if __name__ == "__main__":
    main_optimizer()