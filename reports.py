import datetime
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from models import NakitAkisiVeri
from analysis import NakitAnaliz
from visualization import NakitGorselleştirme

class NakitRaporlama:
    """
    Nakit akışı raporlarını oluşturan sınıf
    """
    
    def __init__(self, veri_modeli=None, nakit_analiz=None, nakit_gorsel=None):
        if veri_modeli is None:
            self.veri = NakitAkisiVeri()
        else:
            self.veri = veri_modeli
            
        if nakit_analiz is None:
            self.nakit_analiz = NakitAnaliz(self.veri)
        else:
            self.nakit_analiz = nakit_analiz
            
        if nakit_gorsel is None:
            self.nakit_gorsel = NakitGorselleştirme(self.veri, self.nakit_analiz)
        else:
            self.nakit_gorsel = nakit_gorsel
    
    def rapor_olustur(self, rapor_tipi="aylik"):
        """Nakit akışı raporu oluşturur"""
        bugun = datetime.datetime.now()
        
        if rapor_tipi == "aylik":
            ay_basi = datetime.datetime(bugun.year, bugun.month, 1)
            if bugun.month == 12:
                ay_sonu = datetime.datetime(bugun.year + 1, 1, 1) - datetime.timedelta(days=1)
            else:
                ay_sonu = datetime.datetime(bugun.year, bugun.month + 1, 1) - datetime.timedelta(days=1)
            
            aylik_girisler = [giris for giris in self.veri.get_nakit_girisler() if ay_basi <= giris["tarih"] <= ay_sonu]
            aylik_cikislar = [cikis for cikis in self.veri.get_nakit_cikislar() if ay_basi <= cikis["tarih"] <= ay_sonu]
            
            rapor = {
                "donem": f"{bugun.month}/{bugun.year}",
                "toplam_giris": sum(giris["miktar"] for giris in aylik_girisler),
                "toplam_cikis": sum(cikis["miktar"] for cikis in aylik_cikislar),
                "net_nakit_akisi": sum(giris["miktar"] for giris in aylik_girisler) - sum(cikis["miktar"] for cikis in aylik_cikislar),
                "girisler": aylik_girisler,
                "cikislar": aylik_cikislar
            }
            
            self.veri.set_rapor(f"aylik_{bugun.month}_{bugun.year}", rapor)
            return rapor
        
        elif rapor_tipi == "yillik":
            yil_basi = datetime.datetime(bugun.year, 1, 1)
            yil_sonu = datetime.datetime(bugun.year, 12, 31)
            
            yillik_girisler = [giris for giris in self.veri.get_nakit_girisler() if yil_basi <= giris["tarih"] <= yil_sonu]
            yillik_cikislar = [cikis for cikis in self.veri.get_nakit_cikislar() if yil_basi <= cikis["tarih"] <= yil_sonu]
            
            rapor = {
                "donem": str(bugun.year),
                "toplam_giris": sum(giris["miktar"] for giris in yillik_girisler),
                "toplam_cikis": sum(cikis["miktar"] for cikis in yillik_cikislar),
                "net_nakit_akisi": sum(giris["miktar"] for giris in yillik_girisler) - sum(cikis["miktar"] for cikis in yillik_cikislar),
                "girisler": yillik_girisler,
                "cikislar": yillik_cikislar
            }
            
            self.veri.set_rapor(f"yillik_{bugun.year}", rapor)
            return rapor
    
    def rapor_gonder(self, email, rapor_tipi="aylik"):
        """Oluşturulan raporu e-posta ile gönderir"""
        rapor = self.veri.get_raporlar().get(f"{rapor_tipi}_{datetime.datetime.now().month}_{datetime.datetime.now().year}")
        
        if not rapor:
            rapor = self.rapor_olustur(rapor_tipi)
        
        grafik_dosyasi = self.nakit_gorsel.grafik_olustur("nakit_akisi")
        
        konu = f"Nakit Akışı Raporu - {rapor['donem']}"
        mesaj = f"""
        Nakit Akışı Raporu - {rapor['donem']}
        
        Toplam Nakit Girişi: {rapor['toplam_giris']} TL
        Toplam Nakit Çıkışı: {rapor['toplam_cikis']} TL
        Net Nakit Akışı: {rapor['net_nakit_akisi']} TL
        
        Detaylı rapor ekte bulunmaktadır.
        """
        
        try:
            # E-posta gönderme işlemi burada yapılacak
            # Kullanıcı kendi SMTP sunucusu ve kimlik bilgilerini kullanmalı
            print(f"E-posta gönderme işlemi simüle edildi. Alıcı: {email}")
            print(f"Konu: {konu}")
            print(f"Mesaj: {mesaj}")
            return True
        except Exception as e:
            print(f"E-posta gönderilirken hata oluştu: {e}")
            return False

    def excel_rapor_olustur(self, dosya_adi=None):
        """Nakit akışı verilerini Excel dosyasına aktarır"""
        if not dosya_adi:
            dosya_adi = f"nakit_akisi_raporu_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx"
        
        # Excel dosyası oluştur
        with pd.ExcelWriter(dosya_adi) as writer:
            # Nakit girişleri
            girisler_df = pd.DataFrame(self.veri.get_nakit_girisler())
            girisler_df.to_excel(writer, sheet_name='Nakit Girişleri', index=False)
            
            # Nakit çıkışları
            cikislar_df = pd.DataFrame(self.veri.get_nakit_cikislar())
            cikislar_df.to_excel(writer, sheet_name='Nakit Çıkışları', index=False)
            
            # Projeksiyonlar
            if self.veri.get_projeksiyonlar().get("aylik"):
                projeksiyonlar_df = pd.DataFrame(self.veri.get_projeksiyonlar()["aylik"])
                projeksiyonlar_df.to_excel(writer, sheet_name='Nakit Akışı Tahminleri', index=False)
            
            # Kategori analizi
            analiz = self.nakit_analiz.kategori_bazli_analiz()
            giris_kategorileri = pd.DataFrame(list(analiz["girisler"].items()), columns=['Kategori', 'Toplam'])
            cikis_kategorileri = pd.DataFrame(list(analiz["cikislar"].items()), columns=['Kategori', 'Toplam'])
            
            giris_kategorileri.to_excel(writer, sheet_name='Kategori Analizi', startrow=0, index=False)
            cikis_kategorileri.to_excel(writer, sheet_name='Kategori Analizi', startrow=len(giris_kategorileri) + 3, index=False)
        
        return dosya_adi 