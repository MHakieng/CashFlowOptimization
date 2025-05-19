import datetime
from models import NakitAkisiVeri
from cash_operations import NakitIslemleri
from analysis import NakitAnaliz
from visualization import NakitGorselleştirme
from reports import NakitRaporlama
from optimization import NakitAkisiOptimizasyon

class NakitAkisiPlatformu:
    """
    Dinamik Nakit Akışı Platformu
    
    Bu sınıf, modülleri birleştirerek ana platformu oluşturur.
    """
    
    def __init__(self):
        self.veri = NakitAkisiVeri()
        self.nakit_islemleri = NakitIslemleri(self.veri)
        self.nakit_analiz = NakitAnaliz(self.veri, self.nakit_islemleri)
        self.nakit_gorsel = NakitGorselleştirme(self.veri, self.nakit_analiz)
        self.nakit_raporlama = NakitRaporlama(self.veri, self.nakit_analiz, self.nakit_gorsel)
        self.nakit_optimizasyon = NakitAkisiOptimizasyon(self.veri, self.nakit_islemleri, self.nakit_analiz)
    
    def nakit_girisi_ekle(self, miktar, tarih, kategori, aciklama="", taraf=None):
        """Nakit girişi ekler"""
        self.nakit_islemleri.nakit_girisi_ekle(miktar, tarih, kategori, aciklama, taraf)
    
    def nakit_cikisi_ekle(self, miktar, tarih, kategori, aciklama="", taraf=None):
        """Nakit çıkışı ekler"""
        self.nakit_islemleri.nakit_cikisi_ekle(miktar, tarih, kategori, aciklama, taraf)
    
    def nakit_durumu_hesapla(self, baslangic_tarihi=None, bitis_tarihi=None, taraf=None):
        """Belirli bir tarih aralığındaki nakit durumunu hesaplar"""
        return self.nakit_islemleri.nakit_durumu_hesapla(baslangic_tarihi, bitis_tarihi, taraf)
    
    def nakit_akisi_tahmin_et(self, ay_sayisi=12, taraf=None):
        """Gelecek aylara yönelik nakit akışı tahmini yapar"""
        return self.nakit_analiz.nakit_akisi_tahmin_et(ay_sayisi, taraf)
    
    def kategori_bazli_analiz(self, taraf=None):
        """Kategori bazlı nakit akışı analizi yapar"""
        return self.nakit_analiz.kategori_bazli_analiz(taraf)
    
    def grafik_olustur(self, grafik_tipi="nakit_akisi", taraf=None):
        """Nakit akışı grafiği oluşturur"""
        return self.nakit_gorsel.grafik_olustur(grafik_tipi, taraf)
    
    def rapor_olustur(self, rapor_tipi="aylik"):
        """Nakit akışı raporu oluşturur"""
        return self.nakit_raporlama.rapor_olustur(rapor_tipi)
    
    def rapor_gonder(self, email, rapor_tipi="aylik"):
        """Oluşturulan raporu e-posta ile gönderir"""
        return self.nakit_raporlama.rapor_gonder(email, rapor_tipi)
    
    def excel_rapor_olustur(self, dosya_adi=None):
        """Nakit akışı verilerini Excel dosyasına aktarır"""
        return self.nakit_raporlama.excel_rapor_olustur(dosya_adi)
        
    def taraf_ekle(self, taraf_adi):
        """Yeni bir taraf ekler"""
        self.nakit_islemleri.taraf_ekle(taraf_adi)
        
    def taraf_listele(self):
        """Tüm tarafları listeler"""
        return self.nakit_islemleri.taraf_listele()
        
    def taraf_bazli_nakit_durumu(self):
        """Her tarafın nakit durumunu hesaplar ve döndürür"""
        return self.nakit_islemleri.taraf_bazli_nakit_durumu()
        
    def taraf_performans_analizi(self):
        """Her tarafın performans analizini yapar"""
        return self.nakit_analiz.taraf_performans_analizi()
        
    # Optimizasyon ve Simülasyon Metotları
    def islem_sayisi_optimize_et(self, taraflar=None, min_islem_tutari=1000):
        """İşlem sayısını optimize eder"""
        return self.nakit_optimizasyon.islem_sayisi_optimize_et(taraflar, min_islem_tutari=min_islem_tutari)
    
    def maliyet_optimize_et(self, taraflar=None, islem_maliyetleri=None, hedef_bakiye=0):
        """İşlem maliyetlerini optimize eder"""
        return self.nakit_optimizasyon.maliyet_optimize_et(taraflar, islem_maliyetleri, hedef_bakiye)
    
    def nakit_akisi_simulasyonu(self, taraflar=None, senaryo_parametreleri=None, simulasyon_sayisi=100):
        """Nakit akışı simülasyonu yapar"""
        return self.nakit_optimizasyon.nakit_akisi_simulasyonu(taraflar, senaryo_parametreleri, simulasyon_sayisi)
    
    def what_if_analizi(self, senaryo, taraf=None):
        """What-if analizi yapar"""
        return self.nakit_optimizasyon.what_if_analizi(senaryo, taraf) 