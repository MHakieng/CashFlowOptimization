import datetime

class NakitAkisiVeri:
    """
    Nakit akışı için veri yapılarını içeren sınıf
    """
    
    def __init__(self):
        self.nakit_girisler = []
        self.nakit_cikislar = []
        self.taraflar = {}  # Taraflara göre nakit akışı verilerini saklar
        self.projeksiyonlar = {}
        self.raporlar = {}
    
    def get_nakit_girisler(self):
        return self.nakit_girisler
    
    def get_nakit_cikislar(self):
        return self.nakit_cikislar
    
    def get_projeksiyonlar(self):
        return self.projeksiyonlar
    
    def set_projeksiyonlar(self, key, value):
        self.projeksiyonlar[key] = value
    
    def get_raporlar(self):
        return self.raporlar
    
    def set_rapor(self, key, value):
        self.raporlar[key] = value
        
    def get_taraflar(self):
        return self.taraflar
        
    def taraf_ekle(self, taraf_adi):
        """Yeni bir taraf ekler"""
        if taraf_adi not in self.taraflar:
            self.taraflar[taraf_adi] = {
                "nakit_girisler": [],
                "nakit_cikislar": []
            }
            
    def taraf_varmi(self, taraf_adi):
        """Tarafın var olup olmadığını kontrol eder"""
        return taraf_adi in self.taraflar 