import numpy as np
import matplotlib.pyplot as plt
import time

# --- MICHALEWICZ FONKSİYONU (Benchmark Testi) ---
# Global minimum değeri (d=10 için) yaklaşık -9.66 olmalıdır.

def michalewicz_function(position, m=10):
    d = len(position)
    sum_val = 0
    for i in range(d):
        xi = position[i]
        new_val = np.sin(xi) * (np.sin((i + 1) * (xi ** 2) / np.pi)) ** (2 * m)
        sum_val += new_val
    return -sum_val

def GWO_Benchmark(search_agents_no, max_iter, dim):
    # Michalewicz için arama uzayı genelde [0, PI] arasındadır
    lb = 0
    ub = np.pi
    
    # Kurtları Başlat
    Alpha_pos = np.zeros(dim)
    Alpha_score = float("inf") # Minimizasyon problemi olduğu için +sonsuz
    
    Beta_pos = np.zeros(dim)
    Beta_score = float("inf")
    
    Delta_pos = np.zeros(dim)
    Delta_score = float("inf")
    
    Positions = np.zeros((search_agents_no, dim))
    # Rastgele dağıt
    Positions = np.random.uniform(0, 1, (search_agents_no, dim)) * (ub - lb) + lb
        
    Convergence_curve = np.zeros(max_iter)
    
    print(f"🧪 BENCHMARK TESTİ BAŞLIYOR: Michalewicz Fonksiyonu (D={dim})")
    print("-" * 50)
    
    # İterasyonlar
    for l in range(0, max_iter):
        for i in range(0, search_agents_no):
            # Sınır Kontrolü
            Positions[i, :] = np.clip(Positions[i, :], lb, ub)
            
            # Fitness Hesapla (Minimize ediyoruz)
            fitness = michalewicz_function(Positions[i, :])
            
            # Alpha, Beta, Delta Güncelle (En KÜÇÜK değer en iyisidir)
            if fitness < Alpha_score:
                Alpha_score = fitness
                Alpha_pos = Positions[i, :].copy()
            elif fitness < Beta_score:
                Beta_score = fitness
                Beta_pos = Positions[i, :].copy()
            elif fitness < Delta_score:
                Delta_score = fitness
                Delta_pos = Positions[i, :].copy()
        
        # a parametresi azalır
        a = 2 - l * ((2) / max_iter)
        
        # Konum Güncelleme
        for i in range(0, search_agents_no):
            for j in range(0, dim):
                r1, r2 = np.random.random(), np.random.random()
                A1 = 2 * a * r1 - a
                C1 = 2 * r2
                D_alpha = abs(C1 * Alpha_pos[j] - Positions[i, j])
                X1 = Alpha_pos[j] - A1 * D_alpha
                
                r1, r2 = np.random.random(), np.random.random()
                A2 = 2 * a * r1 - a
                C2 = 2 * r2
                D_beta = abs(C2 * Beta_pos[j] - Positions[i, j])
                X2 = Beta_pos[j] - A2 * D_beta
                
                r1, r2 = np.random.random(), np.random.random()
                A3 = 2 * a * r1 - a
                C3 = 2 * r2
                D_delta = abs(C3 * Delta_pos[j] - Positions[i, j])
                X3 = Delta_pos[j] - A3 * D_delta
                
                Positions[i, j] = (X1 + X2 + X3) / 3
        
        Convergence_curve[l] = Alpha_score
        
    return Alpha_score, Convergence_curve

if __name__ == "__main__":
    # Parametreler
    dim = 10         # M=10
    pop_size = 60    # Popülasyon
    iterations = 1000 
    
    best_score, curve = GWO_Benchmark(pop_size, iterations, dim)
    
    print(f"✅ Test Tamamlandı!")
    print(f"🏆 Bulunan Minimum Değer: {best_score:.5f}")
    print(f"🎯 Olması Gereken (Teorik): -9.66015 (Yaklaşık)")
    print("-" * 50)
    
    # Grafik Çiz
    plt.figure(figsize=(10, 6))
    plt.plot(curve, color='green', linewidth=2)
    plt.title(f'Michalewicz Fonksiyonu Yakınsama (D={dim})')
    plt.xlabel('İterasyon')
    plt.ylabel('Fitness Değeri (Hata)')
    plt.grid(True)
    plt.show()