import datetime
from models import NakitAkisiVeri
from cash_operations import NakitIslemleri

class NakitAnaliz:
    """
    Nakit akışı analizlerini yapan sınıf
    """
    
    def __init__(self, veri_modeli=None, nakit_islemleri=None):
        if veri_modeli is None:
            self.veri = NakitAkisiVeri()
        else:
            self.veri = veri_modeli
            
        if nakit_islemleri is None:
            self.nakit_islemleri = NakitIslemleri(self.veri)
        else:
            self.nakit_islemleri = nakit_islemleri
    
    def nakit_akisi_tahmin_et(self, ay_sayisi=12, taraf=None):
        """Gelecek aylara yönelik nakit akışı tahmini yapar"""
        bugun = datetime.datetime.now()
        
        # Son 3 ayın verilerini kullanarak ortalama hesapla
        uc_ay_once = bugun - datetime.timedelta(days=90)
        
        if taraf and self.veri.taraf_varmi(taraf):
            # Belirli bir tarafın verilerini kullan
            son_uc_ay_girisler = [giris["miktar"] for giris in self.veri.get_taraflar()[taraf]["nakit_girisler"] 
                                if giris["tarih"] >= uc_ay_once]
            
            son_uc_ay_cikislar = [cikis["miktar"] for cikis in self.veri.get_taraflar()[taraf]["nakit_cikislar"] 
                                if cikis["tarih"] >= uc_ay_once]
        else:
            # Tüm verileri kullan
            son_uc_ay_girisler = [giris["miktar"] for giris in self.veri.get_nakit_girisler() 
                                if giris["tarih"] >= uc_ay_once]
            
            son_uc_ay_cikislar = [cikis["miktar"] for cikis in self.veri.get_nakit_cikislar() 
                                if cikis["tarih"] >= uc_ay_once]
        
        ortalama_giris = sum(son_uc_ay_girisler) / max(len(son_uc_ay_girisler), 1)
        ortalama_cikis = sum(son_uc_ay_cikislar) / max(len(son_uc_ay_cikislar), 1)
        
        # Tahminleri oluştur
        tahminler = []
        mevcut_bakiye = self.nakit_islemleri.nakit_durumu_hesapla(taraf=taraf)
        
        for i in range(1, ay_sayisi + 1):
            ay = bugun.month + i
            yil = bugun.year + ((ay - 1) // 12)
            ay = ((ay - 1) % 12) + 1
            
            tahmini_giris = ortalama_giris * (1 + (i * 0.01))  # Hafif büyüme varsayımı
            tahmini_cikis = ortalama_cikis * (1 + (i * 0.005))  # Daha düşük oranda büyüme
            
            net_nakit_akisi = tahmini_giris - tahmini_cikis
            mevcut_bakiye += net_nakit_akisi
            
            tahminler.append({
                "ay": ay,
                "yil": yil,
                "tahmini_giris": tahmini_giris,
                "tahmini_cikis": tahmini_cikis,
                "net_nakit_akisi": net_nakit_akisi,
                "tahmini_bakiye": mevcut_bakiye
            })
        
        projeksiyon_key = "aylik"
        if taraf:
            projeksiyon_key = f"aylik_{taraf}"
        
        self.veri.set_projeksiyonlar(projeksiyon_key, tahminler)
        return tahminler
    
    def kategori_bazli_analiz(self, taraf=None):
        """Kategori bazlı nakit akışı analizi yapar"""
        kategori_girisler = {}
        kategori_cikislar = {}
        
        if taraf and self.veri.taraf_varmi(taraf):
            # Belirli bir tarafın verilerini analiz et
            nakit_girisler = self.veri.get_taraflar()[taraf]["nakit_girisler"]
            nakit_cikislar = self.veri.get_taraflar()[taraf]["nakit_cikislar"]
        else:
            # Tüm verileri analiz et
            nakit_girisler = self.veri.get_nakit_girisler()
            nakit_cikislar = self.veri.get_nakit_cikislar()
        
        # Giriş kategorilerini topla
        for giris in nakit_girisler:
            kategori = giris["kategori"]
            if kategori not in kategori_girisler:
                kategori_girisler[kategori] = 0
            kategori_girisler[kategori] += giris["miktar"]
        
        # Çıkış kategorilerini topla
        for cikis in nakit_cikislar:
            kategori = cikis["kategori"]
            if kategori not in kategori_cikislar:
                kategori_cikislar[kategori] = 0
            kategori_cikislar[kategori] += cikis["miktar"]
        
        return {
            "girisler": kategori_girisler,
            "cikislar": kategori_cikislar
        }
        
    def taraf_performans_analizi(self):
        """Her tarafın performans analizini yapar"""
        sonuc = {}
        
        for taraf in self.veri.get_taraflar():
            taraf_girisler = self.veri.get_taraflar()[taraf]["nakit_girisler"]
            taraf_cikislar = self.veri.get_taraflar()[taraf]["nakit_cikislar"]
            
            toplam_giris = sum(giris["miktar"] for giris in taraf_girisler)
            toplam_cikis = sum(cikis["miktar"] for cikis in taraf_cikislar)
            net_durum = toplam_giris - toplam_cikis
            
            # Son 3 ayın nakit akışı trendini hesapla
            bugun = datetime.datetime.now()
            uc_ay_once = bugun - datetime.timedelta(days=90)
            
            son_uc_ay_net = sum(giris["miktar"] for giris in taraf_girisler if giris["tarih"] >= uc_ay_once) - \
                           sum(cikis["miktar"] for cikis in taraf_cikislar if cikis["tarih"] >= uc_ay_once)
                           
            # Taraf için kategori analizini yap
            kategori_analiz = self.kategori_bazli_analiz(taraf)
            
            sonuc[taraf] = {
                "toplam_giris": toplam_giris,
                "toplam_cikis": toplam_cikis,
                "net_durum": net_durum,
                "son_uc_ay_net": son_uc_ay_net,
                "kategoriler": kategori_analiz
            }
            
        return sonuc 