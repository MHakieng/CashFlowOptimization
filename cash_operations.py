import datetime
from models import NakitAkisiVeri

class NakitIslemleri:
    """
    Nakit giriş ve çıkış işlemlerini yöneten sınıf
    """
    
    def __init__(self, veri_modeli=None):
        if veri_modeli is None:
            self.veri = NakitAkisiVeri()
        else:
            self.veri = veri_modeli
    
    def nakit_girisi_ekle(self, miktar, tarih, kategori, aciklama="", taraf=None):
        """Nakit girişi ekler"""
        islem = {
            "miktar": miktar,
            "tarih": tarih,
            "kategori": kategori,
            "aciklama": aciklama,
            "taraf": taraf
        }
        
        # Genel nakit girişlerine ekle
        self.veri.get_nakit_girisler().append(islem)
        
        # Eğer taraf belirtilmişse, o tarafın nakit girişlerine de ekle
        if taraf:
            if not self.veri.taraf_varmi(taraf):
                self.veri.taraf_ekle(taraf)
            
            # Tarafın nakit girişlerine ekle
            taraf_islem = islem.copy()
            self.veri.get_taraflar()[taraf]["nakit_girisler"].append(taraf_islem)
        
    def nakit_cikisi_ekle(self, miktar, tarih, kategori, aciklama="", taraf=None):
        """Nakit çıkışı ekler"""
        islem = {
            "miktar": miktar,
            "tarih": tarih,
            "kategori": kategori,
            "aciklama": aciklama,
            "taraf": taraf
        }
        
        # Genel nakit çıkışlarına ekle
        self.veri.get_nakit_cikislar().append(islem)
        
        # Eğer taraf belirtilmişse, o tarafın nakit çıkışlarına da ekle
        if taraf:
            if not self.veri.taraf_varmi(taraf):
                self.veri.taraf_ekle(taraf)
            
            # Tarafın nakit çıkışlarına ekle
            taraf_islem = islem.copy()
            self.veri.get_taraflar()[taraf]["nakit_cikislar"].append(taraf_islem)
    
    def nakit_durumu_hesapla(self, baslangic_tarihi=None, bitis_tarihi=None, taraf=None):
        """Belirli bir tarih aralığındaki nakit durumunu hesaplar"""
        if not baslangic_tarihi:
            baslangic_tarihi = datetime.datetime.min
        if not bitis_tarihi:
            bitis_tarihi = datetime.datetime.max
        
        if taraf and self.veri.taraf_varmi(taraf):
            # Belirli bir tarafın nakit durumunu hesapla
            toplam_giris = sum(giris["miktar"] for giris in self.veri.get_taraflar()[taraf]["nakit_girisler"] 
                              if baslangic_tarihi <= giris["tarih"] <= bitis_tarihi)
            
            toplam_cikis = sum(cikis["miktar"] for cikis in self.veri.get_taraflar()[taraf]["nakit_cikislar"] 
                              if baslangic_tarihi <= cikis["tarih"] <= bitis_tarihi)
        else:
            # Tüm nakit durumunu hesapla
            toplam_giris = sum(giris["miktar"] for giris in self.veri.get_nakit_girisler() 
                              if baslangic_tarihi <= giris["tarih"] <= bitis_tarihi)
            
            toplam_cikis = sum(cikis["miktar"] for cikis in self.veri.get_nakit_cikislar() 
                              if baslangic_tarihi <= cikis["tarih"] <= bitis_tarihi)
        
        return toplam_giris - toplam_cikis
        
    def taraf_ekle(self, taraf_adi):
        """Yeni bir taraf ekler"""
        self.veri.taraf_ekle(taraf_adi)
        
    def taraf_listele(self):
        """Tüm tarafları listeler"""
        return list(self.veri.get_taraflar().keys())
        
    def taraf_bazli_nakit_durumu(self):
        """Her tarafın nakit durumunu hesaplar ve döndürür"""
        sonuc = {}
        for taraf in self.veri.get_taraflar():
            sonuc[taraf] = self.nakit_durumu_hesapla(taraf=taraf)
        return sonuc 