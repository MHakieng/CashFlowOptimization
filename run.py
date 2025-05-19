#!/usr/bin/env python
"""
Nakit Akışı Platformu Çalıştırıcısı
"""

import sys
import os
import argparse
from app import app
import datetime
from main import NakitAkisiPlatformu

# Dizin yapılandırması
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MODULE_DIR)
sys.path.insert(0, os.path.dirname(MODULE_DIR))

def ornek_veriler_yukle(platform):
    """Örnek veriler ekler - test için"""
    print("Örnek veriler ekleniyor...")
    
    # Taraflar
    for taraf in ["Müşteri A", "Müşteri B", "Tedarikçi X", "Tedarikçi Y"]:
        if taraf not in platform.taraf_listele():
            platform.taraf_ekle(taraf)
    
    # Geçerli ay ve yıl bilgisi
    su_an = datetime.datetime.now()
    su_anki_yil = su_an.year
    su_anki_ay = su_an.month
    
    # Son 3 aya ait veriler oluştur
    for i in range(3):
        ay = su_anki_ay - i
        yil = su_anki_yil
        if ay <= 0:
            ay += 12
            yil -= 1
        
        # Nakit girişleri - maaş ve ek gelir
        platform.nakit_girisi_ekle(5000, datetime.datetime(yil, ay, 15), "Maaş", f"{ay}/{yil} maaşı")
        
        # Nakit çıkışları - kira, market ve faturalar
        platform.nakit_cikisi_ekle(2000, datetime.datetime(yil, ay, 5), "Kira", f"{ay}/{yil} kirası")
        platform.nakit_cikisi_ekle(1000, datetime.datetime(yil, ay, 10), "Market", "Aylık alışveriş")
        platform.nakit_cikisi_ekle(500, datetime.datetime(yil, ay, 12), "Faturalar", "Elektrik, su, doğalgaz")
    
    # Taraf bazlı nakit hareketleri
    platform.nakit_girisi_ekle(3000, datetime.datetime(su_anki_yil, su_anki_ay, 10), "Satış", "Ürün satışı", "Müşteri A")
    platform.nakit_girisi_ekle(2500, datetime.datetime(su_anki_yil, su_anki_ay, 25), "Satış", "Hizmet bedeli", "Müşteri B")
    
    platform.nakit_cikisi_ekle(1500, datetime.datetime(su_anki_yil, su_anki_ay, 8), "Malzeme", "Hammadde alımı", "Tedarikçi X")
    platform.nakit_cikisi_ekle(800, datetime.datetime(su_anki_yil, su_anki_ay, 15), "Hizmet", "Bakım hizmeti", "Tedarikçi Y")
    
    print("Örnek veriler eklendi.")

def main():
    parser = argparse.ArgumentParser(description='Nakit Akışı Platformu')
    parser.add_argument('--demo', action='store_true', help='Örnek verilerle başlat')
    parser.add_argument('--port', type=int, default=5000, help='Web uygulaması için port numarası')
    args = parser.parse_args()
    
    if args.demo:
        from app import platform
        ornek_veriler_yukle(platform)
    
    # Web klasörlerinin varlığını kontrol et
    os.makedirs('static/img', exist_ok=True)
    
    # Web uygulamasını çalıştır
    print("Nakit Akışı Platformu başlatılıyor...")
    print(f"Tarayıcıdan http://127.0.0.1:{args.port} adresine gidin.")
    print("Uygulamayı durdurmak için Ctrl+C tuşlarına basın.")
    
    app.run(debug=True, port=args.port)

if __name__ == "__main__":
    main()
