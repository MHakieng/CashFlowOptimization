import numpy as np
import pulp
import datetime
from models import NakitAkisiVeri
from cash_operations import NakitIslemleri
from analysis import NakitAnaliz

class NakitAkisiOptimizasyon:
    """
    Nakit akışı optimizasyon sınıfı - işlem sayısını ve maliyetleri minimize etmek için 
    optimizasyon algoritmalarını uygular
    """
    
    def __init__(self, veri_modeli=None, nakit_islemleri=None, nakit_analiz=None):
        if veri_modeli is None:
            self.veri = NakitAkisiVeri()
        else:
            self.veri = veri_modeli
            
        if nakit_islemleri is None:
            self.nakit_islemleri = NakitIslemleri(self.veri)
        else:
            self.nakit_islemleri = nakit_islemleri
            
        if nakit_analiz is None:
            self.nakit_analiz = NakitAnaliz(self.veri, self.nakit_islemleri)
        else:
            self.nakit_analiz = nakit_analiz
    
    def islem_sayisi_optimize_et(self, taraflar=None, max_islem_sayisi=None, min_islem_tutari=0):
        """
        İşlem sayısını azaltmak için nakit akışlarını optimize eder
        Örneğin, birden fazla küçük ödeme yerine daha az sayıda büyük ödeme yapılması
        """
        if taraflar is None:
            taraflar = self.nakit_islemleri.taraf_listele()
        elif isinstance(taraflar, str):
            taraflar = [taraflar]
            
        sonuc = {}
        
        for taraf in taraflar:
            if not self.veri.taraf_varmi(taraf):
                continue
                
            taraf_cikislar = self.veri.get_taraflar()[taraf]["nakit_cikislar"]
            
            # Kategori bazlı işlemleri grupla
            kategori_gruplar = {}
            for cikis in taraf_cikislar:
                kategori = cikis["kategori"]
                if kategori not in kategori_gruplar:
                    kategori_gruplar[kategori] = []
                kategori_gruplar[kategori].append(cikis)
            
            optimize_edilmis_islemler = []
            toplam_azaltilan_islem = 0
            
            for kategori, islemler in kategori_gruplar.items():
                # Tarihe göre sırala
                islemler.sort(key=lambda x: x["tarih"])
                
                # Tarih bazlı gruplandırma (ay bazında)
                tarih_gruplari = {}
                for islem in islemler:
                    tarih_key = f"{islem['tarih'].year}-{islem['tarih'].month}"
                    if tarih_key not in tarih_gruplari:
                        tarih_gruplari[tarih_key] = []
                    tarih_gruplari[tarih_key].append(islem)
                
                # Her ay için optimize et
                for tarih_key, ay_islemleri in tarih_gruplari.items():
                    yil, ay = map(int, tarih_key.split('-'))
                    
                    # Minimum işlem tutarından küçük olanları birleştir
                    kucuk_islemler = [i for i in ay_islemleri if i["miktar"] < min_islem_tutari]
                    buyuk_islemler = [i for i in ay_islemleri if i["miktar"] >= min_islem_tutari]
                    
                    if kucuk_islemler:
                        toplam_miktar = sum(i["miktar"] for i in kucuk_islemler)
                        son_tarih = max(i["tarih"] for i in kucuk_islemler)
                        aciklama = f"Birleştirilmiş {len(kucuk_islemler)} işlem"
                        
                        birlestirilmis_islem = {
                            "miktar": toplam_miktar,
                            "tarih": son_tarih,
                            "kategori": kategori,
                            "aciklama": aciklama
                        }
                        
                        optimize_edilmis_islemler.append(birlestirilmis_islem)
                        toplam_azaltilan_islem += len(kucuk_islemler) - 1
                    
                    optimize_edilmis_islemler.extend(buyuk_islemler)
            
            sonuc[taraf] = {
                "orijinal_islem_sayisi": len(taraf_cikislar),
                "optimize_edilmis_islem_sayisi": len(optimize_edilmis_islemler),
                "azaltilan_islem_sayisi": toplam_azaltilan_islem,
                "optimize_edilmis_islemler": optimize_edilmis_islemler
            }
        
        return sonuc
    
    def maliyet_optimize_et(self, taraflar=None, islem_maliyetleri=None, hedef_bakiye=0):
        """
        İşlem maliyetlerini minimize edecek şekilde nakit akışlarını optimize eder
        """
        if taraflar is None:
            taraflar = self.nakit_islemleri.taraf_listele()
        elif isinstance(taraflar, str):
            taraflar = [taraflar]
            
        # Varsayılan işlem maliyetleri
        if islem_maliyetleri is None:
            islem_maliyetleri = {
                "standart": 10,  # Her işlem için standart maliyet
                "acil": 25,      # Acil işlemler için maliyet
                "buyuk_miktar": 15  # Büyük miktarlı işlemler için maliyet
            }
            
        sonuc = {}
        
        for taraf in taraflar:
            if not self.veri.taraf_varmi(taraf):
                continue
                
            taraf_girisler = self.veri.get_taraflar()[taraf]["nakit_girisler"]
            taraf_cikislar = self.veri.get_taraflar()[taraf]["nakit_cikislar"]
            
            # Lineer programlama problemi tanımlama
            problem = pulp.LpProblem(f"Maliyet_Optimizasyonu_{taraf}", pulp.LpMinimize)
            
            # İşlemleri zamana göre sırala
            tum_islemler = taraf_girisler + taraf_cikislar
            tum_islemler.sort(key=lambda x: x["tarih"])
            
            # Her işlem için değişkenler oluştur (1: işlem yapılacak, 0: yapılmayacak)
            islem_degiskenleri = {}
            for i, islem in enumerate(tum_islemler):
                islem_degiskenleri[i] = pulp.LpVariable(f"islem_{i}", 0, 1, pulp.LpBinary)
            
            # Amaç fonksiyonu: Toplam maliyeti minimize et
            toplam_maliyet = pulp.lpSum([self._islem_maliyeti_hesapla(tum_islemler[i], islem_maliyetleri) * islem_degiskenleri[i] 
                                        for i in range(len(tum_islemler))])
            problem += toplam_maliyet
            
            # Kısıt: Nakit bakiyesi hedeflenen değere eşit ya da büyük olmalı
            nakit_bakiyesi = pulp.lpSum([(1 if i < len(taraf_girisler) else -1) * tum_islemler[i]["miktar"] * islem_degiskenleri[i]
                                        for i in range(len(tum_islemler))])
            problem += nakit_bakiyesi >= hedef_bakiye
            
            # Problemi çöz
            problem.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=10))
            
            # Sonuçları topla
            secilen_islemler = []
            toplam_optimize_maliyet = 0
            
            for i, var in enumerate(islem_degiskenleri.values()):
                if var.value() == 1.0:
                    islem = tum_islemler[i]
                    secilen_islemler.append(islem)
                    toplam_optimize_maliyet += self._islem_maliyeti_hesapla(islem, islem_maliyetleri)
            
            # Seçilen işlemlerle nakit akışını hesapla
            optimize_nakit_akisi = sum([(1 if i < len(taraf_girisler) else -1) * islem["miktar"] 
                                      for i, islem in enumerate(secilen_islemler)])
            
            sonuc[taraf] = {
                "orijinal_islem_sayisi": len(tum_islemler),
                "optimize_edilmis_islem_sayisi": len(secilen_islemler),
                "orijinal_maliyet": sum([self._islem_maliyeti_hesapla(islem, islem_maliyetleri) for islem in tum_islemler]),
                "optimize_edilmis_maliyet": toplam_optimize_maliyet,
                "optimize_nakit_akisi": optimize_nakit_akisi,
                "secilen_islemler": secilen_islemler
            }
        
        return sonuc
    
    def nakit_akisi_simulasyonu(self, taraflar=None, senaryo_parametreleri=None, simulasyon_sayisi=100):
        """
        Farklı senaryolarda nakit akışı simülasyonu yapar ve sonuçları analiz eder
        """
        if taraflar is None:
            taraflar = self.nakit_islemleri.taraf_listele()
        elif isinstance(taraflar, str):
            taraflar = [taraflar]
            
        # Varsayılan senaryo parametreleri
        if senaryo_parametreleri is None:
            senaryo_parametreleri = {
                "giriş_değişkenliği": 0.2,  # Nakit girişlerindeki değişkenlik oranı
                "çıkış_değişkenliği": 0.15,  # Nakit çıkışlarındaki değişkenlik oranı
                "gecikme_olasılığı": 0.1,    # Ödemelerde gecikme olasılığı
                "ay_sayısı": 6               # Simülasyon yapılacak ay sayısı
            }
            
        sonuc = {}
        
        for taraf in taraflar:
            if not self.veri.taraf_varmi(taraf):
                continue
                
            # Taraf için tahminleri al
            tahminler = self.nakit_analiz.nakit_akisi_tahmin_et(senaryo_parametreleri["ay_sayısı"], taraf)
            
            # Monte Carlo simülasyonu yap
            simulasyon_sonuclari = []
            
            for _ in range(simulasyon_sayisi):
                simulasyon = []
                mevcut_bakiye = self.nakit_islemleri.nakit_durumu_hesapla(taraf=taraf)
                
                for tahmin in tahminler:
                    # Rastgele değişkenlik ekle
                    giris_carpani = np.random.normal(1, senaryo_parametreleri["giriş_değişkenliği"])
                    cikis_carpani = np.random.normal(1, senaryo_parametreleri["çıkış_değişkenliği"])
                    
                    # Negatif değerleri engelle
                    giris_carpani = max(0, giris_carpani)
                    cikis_carpani = max(0, cikis_carpani)
                    
                    # Gecikme simülasyonu
                    gecikme_var_mi = np.random.random() < senaryo_parametreleri["gecikme_olasılığı"]
                    
                    simulasyon_giris = tahmin["tahmini_giris"] * giris_carpani
                    simulasyon_cikis = tahmin["tahmini_cikis"] * cikis_carpani
                    
                    if gecikme_var_mi:
                        # Girişlerin %30'u gelecek aya erteleniyor
                        ertelenen_giris = simulasyon_giris * 0.3
                        simulasyon_giris -= ertelenen_giris
                        # Ertelenen miktar bir sonraki simulasyonda eklenir
                        if len(simulasyon) > 0:
                            simulasyon[-1]["tahmini_giris"] += ertelenen_giris
                    
                    net_nakit_akisi = simulasyon_giris - simulasyon_cikis
                    mevcut_bakiye += net_nakit_akisi
                    
                    simulasyon.append({
                        "ay": tahmin["ay"],
                        "yil": tahmin["yil"],
                        "tahmini_giris": simulasyon_giris,
                        "tahmini_cikis": simulasyon_cikis,
                        "net_nakit_akisi": net_nakit_akisi,
                        "tahmini_bakiye": mevcut_bakiye
                    })
                
                simulasyon_sonuclari.append(simulasyon)
            
            # Simülasyon sonuçlarını analiz et
            ay_bazli_analizler = []
            
            for ay_indeks in range(senaryo_parametreleri["ay_sayısı"]):
                ay_bakiyeler = [sim[ay_indeks]["tahmini_bakiye"] for sim in simulasyon_sonuclari]
                
                analiz = {
                    "ay": tahminler[ay_indeks]["ay"],
                    "yil": tahminler[ay_indeks]["yil"],
                    "ortalama_bakiye": np.mean(ay_bakiyeler),
                    "minimum_bakiye": min(ay_bakiyeler),
                    "maksimum_bakiye": max(ay_bakiyeler),
                    "standart_sapma": np.std(ay_bakiyeler),
                    "negatif_olasılık": sum(1 for b in ay_bakiyeler if b < 0) / simulasyon_sayisi
                }
                
                ay_bazli_analizler.append(analiz)
            
            sonuc[taraf] = {
                "tahminler": tahminler,
                "simulasyon_sonuclari": simulasyon_sonuclari,
                "ay_bazli_analizler": ay_bazli_analizler
            }
        
        return sonuc
    
    def what_if_analizi(self, senaryo, taraf=None):
        """
        Farklı senaryolar için 'what-if' analizi yapar
        """
        # Mevcut durumu kopyala
        mevcut_durum = {
            "nakit_girisler": self.veri.get_nakit_girisler().copy(),
            "nakit_cikislar": self.veri.get_nakit_cikislar().copy(),
            "taraflar": {t: {"nakit_girisler": self.veri.get_taraflar()[t]["nakit_girisler"].copy(),
                            "nakit_cikislar": self.veri.get_taraflar()[t]["nakit_cikislar"].copy()}
                        for t in self.veri.get_taraflar()}
        }
        
        # Senaryo uygula
        self._senaryo_uygula(senaryo, taraf)
        
        # Senaryo sonrası analiz
        senaryo_sonrasi = {}
        
        if taraf:
            nakit_durumu = self.nakit_islemleri.nakit_durumu_hesapla(taraf=taraf)
            tahminler = self.nakit_analiz.nakit_akisi_tahmin_et(6, taraf)
            
            senaryo_sonrasi = {
                "taraf": taraf,
                "nakit_durumu": nakit_durumu,
                "tahminler": tahminler
            }
        else:
            # Tüm taraflar için analiz
            genel_durum = self.nakit_islemleri.nakit_durumu_hesapla()
            genel_tahminler = self.nakit_analiz.nakit_akisi_tahmin_et(6)
            
            taraf_durumlari = {}
            taraf_tahminleri = {}
            
            for t in self.veri.get_taraflar():
                taraf_durumlari[t] = self.nakit_islemleri.nakit_durumu_hesapla(taraf=t)
                taraf_tahminleri[t] = self.nakit_analiz.nakit_akisi_tahmin_et(6, t)
            
            senaryo_sonrasi = {
                "genel_durum": genel_durum,
                "genel_tahminler": genel_tahminler,
                "taraf_durumlari": taraf_durumlari,
                "taraf_tahminleri": taraf_tahminleri
            }
        
        # Orjinal durumu geri yükle
        self._durumu_geri_yukle(mevcut_durum)
        
        return {
            "senaryo": senaryo,
            "sonuc": senaryo_sonrasi
        }
    
    def _islem_maliyeti_hesapla(self, islem, maliyet_tablosu):
        """İşlem maliyetini hesaplar"""
        maliyet = maliyet_tablosu["standart"]
        
        # Büyük miktar kontrolü (örneğin 5000 TL üstü)
        if islem["miktar"] > 5000:
            maliyet = maliyet_tablosu["buyuk_miktar"]
        
        # Acil işlem kontrolü (3 günden kısa sürede)
        bugun = datetime.datetime.now()
        if (islem["tarih"] - bugun).days < 3:
            maliyet = maliyet_tablosu["acil"]
            
        return maliyet
    
    def _senaryo_uygula(self, senaryo, taraf=None):
        """Senaryoyu uygula"""
        if senaryo["tip"] == "giriş_artışı":
            # Nakit girişlerinde belirli oranda artış
            oran = senaryo["oran"]
            if taraf:
                for giris in self.veri.get_taraflar()[taraf]["nakit_girisler"]:
                    giris["miktar"] *= (1 + oran)
            else:
                for giris in self.veri.get_nakit_girisler():
                    giris["miktar"] *= (1 + oran)
                    
        elif senaryo["tip"] == "giriş_azalışı":
            # Nakit girişlerinde belirli oranda azalış
            oran = senaryo["oran"]
            if taraf:
                for giris in self.veri.get_taraflar()[taraf]["nakit_girisler"]:
                    giris["miktar"] *= (1 - oran)
            else:
                for giris in self.veri.get_nakit_girisler():
                    giris["miktar"] *= (1 - oran)
                    
        elif senaryo["tip"] == "çıkış_artışı":
            # Nakit çıkışlarında belirli oranda artış
            oran = senaryo["oran"]
            if taraf:
                for cikis in self.veri.get_taraflar()[taraf]["nakit_cikislar"]:
                    cikis["miktar"] *= (1 + oran)
            else:
                for cikis in self.veri.get_nakit_cikislar():
                    cikis["miktar"] *= (1 + oran)
                    
        elif senaryo["tip"] == "çıkış_azalışı":
            # Nakit çıkışlarında belirli oranda azalış
            oran = senaryo["oran"]
            if taraf:
                for cikis in self.veri.get_taraflar()[taraf]["nakit_cikislar"]:
                    cikis["miktar"] *= (1 - oran)
            else:
                for cikis in self.veri.get_nakit_cikislar():
                    cikis["miktar"] *= (1 - oran)
                    
        elif senaryo["tip"] == "yeni_taraf":
            # Yeni bir taraf ekle
            yeni_taraf = senaryo["taraf_adi"]
            self.veri.taraf_ekle(yeni_taraf)
            
            # Örnek nakit akışları
            for giris in senaryo.get("nakit_girisler", []):
                self.nakit_islemleri.nakit_girisi_ekle(
                    giris["miktar"], 
                    giris["tarih"], 
                    giris["kategori"], 
                    giris.get("aciklama", ""), 
                    yeni_taraf
                )
                
            for cikis in senaryo.get("nakit_cikislar", []):
                self.nakit_islemleri.nakit_cikisi_ekle(
                    cikis["miktar"], 
                    cikis["tarih"], 
                    cikis["kategori"], 
                    cikis.get("aciklama", ""), 
                    yeni_taraf
                )
    
    def _durumu_geri_yukle(self, mevcut_durum):
        """Orijinal durumu geri yükle"""
        # Nakit girişleri ve çıkışlarını geri yükle
        self.veri.nakit_girisler = mevcut_durum["nakit_girisler"]
        self.veri.nakit_cikislar = mevcut_durum["nakit_cikislar"]
        
        # Tarafları geri yükle
        self.veri.taraflar = mevcut_durum["taraflar"] 