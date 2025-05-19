import datetime
import os
import numpy as np
# Set the matplotlib backend to Agg (non-interactive) before importing pyplot
import matplotlib
matplotlib.use('Agg')  # Must be before importing pyplot
import matplotlib.pyplot as plt
from models import NakitAkisiVeri
from analysis import NakitAnaliz

class NakitGorselleştirme:
    """
    Nakit akışı görselleştirmelerini yapan sınıf
    """
    
    def __init__(self, veri_modeli=None, nakit_analiz=None):
        if veri_modeli is None:
            self.veri = NakitAkisiVeri()
        else:
            self.veri = veri_modeli
            
        if nakit_analiz is None:
            self.nakit_analiz = NakitAnaliz(self.veri)
        else:
            self.nakit_analiz = nakit_analiz
    
    def _bos_grafik_olustur(self, baslik, mesaj="Veri bulunamadı"):
        """Veri olmadığında boş bir grafik oluşturur"""
        try:
            fig = plt.figure(figsize=(12, 6))
            plt.text(0.5, 0.5, mesaj, horizontalalignment='center', verticalalignment='center', fontsize=14)
            plt.title(baslik)
            plt.axis('off')
            return fig
        except Exception as e:
            print(f"Grafik oluşturma hatası: {e}")
            return None
    
    def grafik_olustur(self, grafik_tipi="nakit_akisi", taraf=None):
        """Nakit akışı grafiği oluşturur"""
        try:
            # Dosya adı için temel yapı oluştur
            dosya_adi_eki = ""
            if taraf:
                dosya_adi_eki = f"_{taraf}"
            dosya_adi = f"nakit_akisi_{grafik_tipi}{dosya_adi_eki}_{datetime.datetime.now().strftime('%Y%m%d')}.png"
            tam_dosya_yolu = os.path.join('static', 'img', dosya_adi)
            
            # Ana grafik oluştur
            plt.figure(figsize=(12, 6))
            
            if grafik_tipi == "nakit_akisi":
                projeksiyon_key = "aylik"
                if taraf:
                    projeksiyon_key = f"aylik_{taraf}"
                    
                if not self.veri.get_projeksiyonlar().get(projeksiyon_key):
                    self.nakit_analiz.nakit_akisi_tahmin_et(taraf=taraf)
                
                tahminler = self.veri.get_projeksiyonlar().get(projeksiyon_key, [])
                
                if not tahminler:
                    # Boş veri durumunda
                    baslik = "Nakit Akışı Tahmini" if not taraf else f"{taraf} için Nakit Akışı Tahmini"
                    plt.close()
                    self._bos_grafik_olustur(baslik, "Henüz tahmin için yeterli veri bulunmamaktadır.")
                    plt.savefig(tam_dosya_yolu)
                    plt.close()
                    return dosya_adi
                
                aylar = [f"{t['ay']}/{t['yil']}" for t in tahminler]
                bakiyeler = [t["tahmini_bakiye"] for t in tahminler]
                
                plt.plot(aylar, bakiyeler, marker='o', color='#007bff')
                
                # Sıfır çizgisi ekle
                plt.axhline(y=0, color='#dc3545', linestyle='--', alpha=0.3)
                
                baslik = "Nakit Akışı Tahmini"
                if taraf:
                    baslik = f"{taraf} için Nakit Akışı Tahmini"
                    
                plt.title(baslik)
                plt.xlabel("Ay/Yıl")
                plt.ylabel("Tahmini Bakiye")
                plt.grid(True, alpha=0.3)
                
            elif grafik_tipi == "kategori":
                analiz = self.nakit_analiz.kategori_bazli_analiz(taraf)
                
                if not analiz["girisler"] and not analiz["cikislar"]:
                    # Boş veri durumunda
                    baslik = "Kategori Bazlı Analiz" if not taraf else f"{taraf} - Kategori Bazlı Analiz"
                    plt.close()
                    self._bos_grafik_olustur(baslik, "Henüz kategori analizi için yeterli veri bulunmamaktadır.")
                    plt.savefig(tam_dosya_yolu)
                    plt.close()
                    return dosya_adi
                
                # Giriş kategorileri
                plt.subplot(1, 2, 1)
                if analiz["girisler"]:
                    kategoriler = list(analiz["girisler"].keys())
                    degerler = list(analiz["girisler"].values())
                    
                    # Renk göstergesini güvenli şekilde oluştur
                    color_range = np.linspace(0.3, 0.8, len(degerler) if len(degerler) > 0 else 1)
                    colors = plt.cm.Greens(color_range)
                    
                    plt.pie(degerler, labels=kategoriler, autopct='%1.1f%%', colors=colors)
                    
                    baslik_giris = "Nakit Girişleri (Kategori Bazlı)"
                    if taraf:
                        baslik_giris = f"{taraf} - Nakit Girişleri"
                    plt.title(baslik_giris)
                else:
                    plt.text(0.5, 0.5, "Giriş verisi bulunamadı", 
                            horizontalalignment='center', verticalalignment='center')
                    plt.title("Nakit Girişleri")
                    plt.axis('on')
                
                # Çıkış kategorileri
                plt.subplot(1, 2, 2)
                if analiz["cikislar"]:
                    kategoriler = list(analiz["cikislar"].keys())
                    degerler = list(analiz["cikislar"].values())
                    
                    # Renk göstergesini güvenli şekilde oluştur
                    color_range = np.linspace(0.3, 0.8, len(degerler) if len(degerler) > 0 else 1)
                    colors = plt.cm.Reds(color_range)
                    
                    plt.pie(degerler, labels=kategoriler, autopct='%1.1f%%', colors=colors)
                    
                    baslik_cikis = "Nakit Çıkışları (Kategori Bazlı)"
                    if taraf:
                        baslik_cikis = f"{taraf} - Nakit Çıkışları"
                    plt.title(baslik_cikis)
                else:
                    plt.text(0.5, 0.5, "Çıkış verisi bulunamadı", 
                            horizontalalignment='center', verticalalignment='center')
                    plt.title("Nakit Çıkışları")
                    plt.axis('on')
                
            elif grafik_tipi == "taraf_karsilastirma":
                # Tarafların nakit durumlarını karşılaştırma grafiği
                taraf_durumlari = {}
                
                for t in self.veri.get_taraflar():
                    taraf_durumlari[t] = self.nakit_analiz.nakit_islemleri.nakit_durumu_hesapla(taraf=t)
                
                if not taraf_durumlari:
                    # Boş veri durumunda
                    plt.close()
                    self._bos_grafik_olustur("Taraf Bazlı Nakit Durumu Karşılaştırması", 
                                        "Henüz taraf kaydı bulunmamaktadır.")
                    plt.savefig(tam_dosya_yolu)
                    plt.close()
                    return dosya_adi
                    
                taraflar = list(taraf_durumlari.keys())
                bakiyeler = list(taraf_durumlari.values())
                
                # Pozitif ve negatif değerleri ayır, farklı renklerde göster
                colors = ['#28a745' if x >= 0 else '#dc3545' for x in bakiyeler]
                
                plt.bar(taraflar, bakiyeler, color=colors)
                plt.title("Taraf Bazlı Nakit Durumu Karşılaştırması")
                plt.xlabel("Taraflar")
                plt.ylabel("Nakit Durumu")
                plt.grid(True, axis='y', alpha=0.3)
                
                # Sıfır çizgisi ekle
                plt.axhline(y=0, color='gray', linestyle='--', alpha=0.3)
            
            # Grafiği kaydet ve kapat
            plt.tight_layout()  # İçeriğin düzgün yerleşmesi için
            plt.savefig(tam_dosya_yolu, dpi=100, bbox_inches='tight')
            plt.close()
            
            return dosya_adi
            
        except Exception as e:
            print(f"Grafik oluşturma hatası: {e}")
            # Hata durumunda boş bir grafik oluştur
            try:
                plt.figure(figsize=(12, 6))
                plt.text(0.5, 0.5, f"Grafik oluşturulurken hata: {str(e)}", 
                      horizontalalignment='center', verticalalignment='center')
                plt.axis('off')
                plt.savefig(tam_dosya_yolu)
                plt.close()
            except:
                pass
            return dosya_adi 