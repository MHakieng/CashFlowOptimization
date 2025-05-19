import os
import datetime
import json
import shutil
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from main import NakitAkisiPlatformu

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_FOLDER'] = 'static'
app.config['DATA_FOLDER'] = 'data'
app.config['BACKUP_FOLDER'] = os.path.join('data', 'backups')

# Klasörler yoksa oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['STATIC_FOLDER'], 'img'), exist_ok=True)
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
os.makedirs(app.config['BACKUP_FOLDER'], exist_ok=True)

# Platform örneğini oluştur
platform = NakitAkisiPlatformu()

# Veri dosyası yolları
TARAFLAR_DOSYA = os.path.join(app.config['DATA_FOLDER'], 'taraflar.json')
NAKIT_GIRISLER_DOSYA = os.path.join(app.config['DATA_FOLDER'], 'nakit_girisler.json')
NAKIT_CIKISLAR_DOSYA = os.path.join(app.config['DATA_FOLDER'], 'nakit_cikislar.json')

# Otomatik yedekleme fonksiyonu
def veri_yedekle():
    """Tüm veri dosyalarını tarih damgalı bir yedek klasörüne kopyalar"""
    try:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(app.config['BACKUP_FOLDER'], timestamp)
        os.makedirs(backup_dir, exist_ok=True)
        
        # Her bir veri dosyasını yedekle
        for dosya in [TARAFLAR_DOSYA, NAKIT_GIRISLER_DOSYA, NAKIT_CIKISLAR_DOSYA]:
            if os.path.exists(dosya):
                shutil.copy2(dosya, backup_dir)
        
        # Yedek klasörlerini sınırla (en son 10 yedek tutulur)
        tum_yedekler = sorted([d for d in os.listdir(app.config['BACKUP_FOLDER']) 
                              if os.path.isdir(os.path.join(app.config['BACKUP_FOLDER'], d))])
        
        if len(tum_yedekler) > 10:
            for eski_yedek in tum_yedekler[:-10]:
                shutil.rmtree(os.path.join(app.config['BACKUP_FOLDER'], eski_yedek))
                
        return True
    except Exception as e:
        print(f"Yedekleme hatası: {e}")
        return False

# Kaydedilen verileri yükle
def verileri_yukle():
    # Tarafları yükle
    if os.path.exists(TARAFLAR_DOSYA):
        try:
            with open(TARAFLAR_DOSYA, 'r', encoding='utf-8') as f:
                taraflar = json.load(f)
                for taraf in taraflar:
                    if taraf not in platform.taraf_listele():
                        platform.taraf_ekle(taraf)
        except Exception as e:
            print(f"Taraflar yüklenirken hata: {e}")
    
    # Nakit girişlerini yükle
    if os.path.exists(NAKIT_GIRISLER_DOSYA):
        try:
            with open(NAKIT_GIRISLER_DOSYA, 'r', encoding='utf-8') as f:
                girisler = json.load(f)
                for giris in girisler:
                    tarih = datetime.datetime.fromisoformat(giris['tarih'])
                    platform.nakit_girisi_ekle(
                        giris['miktar'],
                        tarih,
                        giris['kategori'],
                        giris['aciklama'],
                        giris['taraf']
                    )
        except Exception as e:
            print(f"Nakit girişleri yüklenirken hata: {e}")
    
    # Nakit çıkışlarını yükle
    if os.path.exists(NAKIT_CIKISLAR_DOSYA):
        try:
            with open(NAKIT_CIKISLAR_DOSYA, 'r', encoding='utf-8') as f:
                cikislar = json.load(f)
                for cikis in cikislar:
                    tarih = datetime.datetime.fromisoformat(cikis['tarih'])
                    platform.nakit_cikisi_ekle(
                        cikis['miktar'],
                        tarih,
                        cikis['kategori'],
                        cikis['aciklama'],
                        cikis['taraf']
                    )
        except Exception as e:
            print(f"Nakit çıkışları yüklenirken hata: {e}")

# Verileri kaydet
def verileri_kaydet():
    # Önce yedekleme yap
    veri_yedekle()
    
    # Tarafları kaydet
    try:
        with open(TARAFLAR_DOSYA, 'w', encoding='utf-8') as f:
            json.dump(platform.taraf_listele(), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Taraflar kaydedilirken hata: {e}")
    
    # Nakit girişlerini kaydet
    try:
        girisler = []
        for giris in platform.veri.get_nakit_girisler():
            giris_kopya = giris.copy()
            giris_kopya['tarih'] = giris_kopya['tarih'].isoformat()
            girisler.append(giris_kopya)
        
        with open(NAKIT_GIRISLER_DOSYA, 'w', encoding='utf-8') as f:
            json.dump(girisler, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Nakit girişleri kaydedilirken hata: {e}")
    
    # Nakit çıkışlarını kaydet
    try:
        cikislar = []
        for cikis in platform.veri.get_nakit_cikislar():
            cikis_kopya = cikis.copy()
            cikis_kopya['tarih'] = cikis_kopya['tarih'].isoformat()
            cikislar.append(cikis_kopya)
        
        with open(NAKIT_CIKISLAR_DOSYA, 'w', encoding='utf-8') as f:
            json.dump(cikislar, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Nakit çıkışları kaydedilirken hata: {e}")

# Uygulama başlatıldığında verileri yükle
verileri_yukle()

# Her istek için güncel tarihi geçir
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}

@app.route('/')
def home():
    # Genel nakit durumu
    genel_durum = platform.nakit_durumu_hesapla()
    
    # Taraf bazlı nakit durumları
    taraf_durumlari = platform.taraf_bazli_nakit_durumu()
    
    # Kategoriler
    kategoriler = {}
    analiz = platform.kategori_bazli_analiz()
    kategoriler["girisler"] = analiz["girisler"]
    kategoriler["cikislar"] = analiz["cikislar"]
    
    # Taraflar
    taraflar = platform.taraf_listele()
    
    # Temel nakit akışı grafiğini oluştur (static/img klasörüne kaydedilir)
    nakit_akisi_grafik = platform.grafik_olustur("nakit_akisi")
    kategori_grafik = platform.grafik_olustur("kategori")
    taraf_karsilastirma_grafik = platform.grafik_olustur("taraf_karsilastirma")
    
    # Grafik dosya yollarını, sadece dosya adlarını alarak düzelt
    nakit_akisi_grafik = os.path.basename(nakit_akisi_grafik)
    kategori_grafik = os.path.basename(kategori_grafik)
    taraf_karsilastirma_grafik = os.path.basename(taraf_karsilastirma_grafik)
    
    # Tahminler
    tahminler = platform.nakit_akisi_tahmin_et(6)
    
    return render_template('index.html', 
                           genel_durum=genel_durum,
                           taraf_durumlari=taraf_durumlari,
                           kategoriler=kategoriler,
                           taraflar=taraflar,
                           nakit_akisi_grafik=nakit_akisi_grafik,
                           kategori_grafik=kategori_grafik,
                           taraf_karsilastirma_grafik=taraf_karsilastirma_grafik,
                           tahminler=tahminler)

@app.route('/taraflar')
def taraflar_sayfasi():
    taraflar = platform.taraf_listele()
    taraf_durumlari = platform.taraf_bazli_nakit_durumu()
    taraf_performans = platform.taraf_performans_analizi()
    
    return render_template('taraflar.html', 
                           taraflar=taraflar,
                           taraf_durumlari=taraf_durumlari,
                           taraf_performans=taraf_performans)

@app.route('/taraf_ekle', methods=['POST'])
def taraf_ekle():
    taraf_adi = request.form.get('taraf_adi')
    if taraf_adi and taraf_adi not in platform.taraf_listele():
        platform.taraf_ekle(taraf_adi)
        verileri_kaydet()  # Veriyi kaydet
    return redirect(url_for('taraflar_sayfasi'))

@app.route('/taraf/<taraf_adi>')
def taraf_detay(taraf_adi):
    if taraf_adi not in platform.taraf_listele():
        return redirect(url_for('taraflar_sayfasi'))
    
    taraf_durumu = platform.nakit_durumu_hesapla(taraf=taraf_adi)
    taraf_analiz = platform.kategori_bazli_analiz(taraf=taraf_adi)
    taraf_tahminleri = platform.nakit_akisi_tahmin_et(6, taraf=taraf_adi)
    
    # Taraf için grafik oluştur
    taraf_nakit_akisi_grafik = platform.grafik_olustur("nakit_akisi", taraf_adi)
    taraf_kategori_grafik = platform.grafik_olustur("kategori", taraf_adi)
    
    taraf_nakit_akisi_grafik = os.path.basename(taraf_nakit_akisi_grafik)
    taraf_kategori_grafik = os.path.basename(taraf_kategori_grafik)
    
    return render_template('taraf_detay.html',
                           taraf_adi=taraf_adi,
                           taraf_durumu=taraf_durumu,
                           taraf_analiz=taraf_analiz,
                           tahminler=taraf_tahminleri,
                           nakit_akisi_grafik=taraf_nakit_akisi_grafik,
                           kategori_grafik=taraf_kategori_grafik)

@app.route('/islemler')
def islemler_sayfasi():
    taraflar = platform.taraf_listele()
    
    # Tüm nakit girişleri
    nakit_girisler = platform.veri.get_nakit_girisler()
    # Tüm nakit çıkışları
    nakit_cikislar = platform.veri.get_nakit_cikislar()
    
    return render_template('islemler.html',
                           taraflar=taraflar,
                           nakit_girisler=nakit_girisler,
                           nakit_cikislar=nakit_cikislar)

@app.route('/islem_ekle', methods=['POST'])
def islem_ekle():
    islem_tipi = request.form.get('islem_tipi')
    miktar = float(request.form.get('miktar'))
    tarih_str = request.form.get('tarih')
    tarih = datetime.datetime.strptime(tarih_str, '%Y-%m-%d')
    kategori = request.form.get('kategori')
    aciklama = request.form.get('aciklama')
    taraf = request.form.get('taraf')
    
    if taraf == "":
        taraf = None
    
    if islem_tipi == 'giris':
        platform.nakit_girisi_ekle(miktar, tarih, kategori, aciklama, taraf)
    elif islem_tipi == 'cikis':
        platform.nakit_cikisi_ekle(miktar, tarih, kategori, aciklama, taraf)
    
    # Veriyi kaydet
    verileri_kaydet()
    
    return redirect(url_for('islemler_sayfasi'))

@app.route('/optimizasyon')
def optimizasyon_sayfasi():
    taraflar = platform.taraf_listele()
    return render_template('optimizasyon.html', taraflar=taraflar)

@app.route('/islem_sayisi_optimize', methods=['POST'])
def islem_sayisi_optimize():
    taraf = request.form.get('taraf')
    min_islem_tutari = float(request.form.get('min_islem_tutari', 500))
    
    sonuc = platform.islem_sayisi_optimize_et(taraf, min_islem_tutari=min_islem_tutari)
    
    return render_template('optimizasyon_sonuc.html',
                          optimizasyon_tipi="İşlem Sayısı Optimizasyonu",
                          sonuc=sonuc)

@app.route('/maliyet_optimize', methods=['POST'])
def maliyet_optimize():
    taraf = request.form.get('taraf')
    hedef_bakiye = float(request.form.get('hedef_bakiye', 0))
    
    sonuc = platform.maliyet_optimize_et(taraf, hedef_bakiye=hedef_bakiye)
    
    return render_template('optimizasyon_sonuc.html',
                          optimizasyon_tipi="Maliyet Optimizasyonu",
                          sonuc=sonuc)

@app.route('/simulasyon')
def simulasyon_sayfasi():
    taraflar = platform.taraf_listele()
    return render_template('simulasyon.html', taraflar=taraflar)

@app.route('/nakit_akisi_simulasyonu', methods=['POST'])
def nakit_akisi_simulasyonu():
    taraf = request.form.get('taraf')
    simulasyon_sayisi = int(request.form.get('simulasyon_sayisi', 100))
    giris_degiskenligi = float(request.form.get('giris_degiskenligi', 0.2))
    cikis_degiskenligi = float(request.form.get('cikis_degiskenligi', 0.15))
    gecikme_olasiligi = float(request.form.get('gecikme_olasiligi', 0.1))
    ay_sayisi = int(request.form.get('ay_sayisi', 6))
    
    senaryo_parametreleri = {
        "giriş_değişkenliği": giris_degiskenligi,
        "çıkış_değişkenliği": cikis_degiskenligi,
        "gecikme_olasılığı": gecikme_olasiligi,
        "ay_sayısı": ay_sayisi
    }
    
    sonuc = platform.nakit_akisi_simulasyonu(taraf, senaryo_parametreleri, simulasyon_sayisi)
    
    return render_template('simulasyon_sonuc.html',
                          simulasyon_tipi="Nakit Akışı Simülasyonu",
                          sonuc=sonuc)

@app.route('/what_if_analizi', methods=['POST'])
def what_if_analizi():
    taraf = request.form.get('taraf')
    senaryo_tipi = request.form.get('senaryo_tipi')
    oran = float(request.form.get('oran', 0.2))
    aciklama = request.form.get('aciklama', '')
    
    senaryo = {
        "tip": senaryo_tipi,
        "oran": oran,
        "aciklama": aciklama
    }
    
    sonuc = platform.what_if_analizi(senaryo, taraf)
    
    return render_template('simulasyon_sonuc.html',
                          simulasyon_tipi="What-If Analizi",
                          sonuc=sonuc)

@app.route('/raporlar')
def raporlar_sayfasi():
    return render_template('raporlar.html')

@app.route('/rapor_olustur', methods=['POST'])
def rapor_olustur():
    rapor_tipi = request.form.get('rapor_tipi', 'aylik')
    
    rapor = platform.rapor_olustur(rapor_tipi)
    
    return render_template('rapor_sonuc.html', rapor=rapor)

@app.route('/excel_rapor_olustur', methods=['POST'])
def excel_rapor_olustur():
    dosya_adi = platform.excel_rapor_olustur()
    
    return send_file(dosya_adi, as_attachment=True)

@app.route('/verileri_sil', methods=['POST'])
def verileri_sil():
    # Modelden verileri sil
    platform.veri.nakit_girisler = []
    platform.veri.nakit_cikislar = []
    platform.veri.taraflar = {}
    platform.veri.projeksiyonlar = {}
    platform.veri.raporlar = {}
    
    # JSON dosyalarını temizle
    for dosya in [TARAFLAR_DOSYA, NAKIT_GIRISLER_DOSYA, NAKIT_CIKISLAR_DOSYA]:
        if os.path.exists(dosya):
            with open(dosya, 'w') as f:
                json.dump([], f)
    
    return redirect(url_for('home'))

@app.route('/veri_export')
def veri_export_sayfasi():
    """Veri dışa aktarma sayfası"""
    return render_template('veri_export.html')

@app.route('/export_json')
def export_json():
    """Tüm verileri JSON formatında dışa aktar"""
    try:
        # Tüm verileri bir sözlük içinde topla
        export_data = {
            "taraflar": platform.taraf_listele(),
            "nakit_girisler": [],
            "nakit_cikislar": []
        }
        
        # Nakit girişlerini düzenle (tarih ISO formatında olmalı)
        for giris in platform.veri.get_nakit_girisler():
            giris_kopya = giris.copy()
            if isinstance(giris_kopya['tarih'], datetime.datetime):
                giris_kopya['tarih'] = giris_kopya['tarih'].isoformat()
            export_data["nakit_girisler"].append(giris_kopya)
        
        # Nakit çıkışlarını düzenle
        for cikis in platform.veri.get_nakit_cikislar():
            cikis_kopya = cikis.copy()
            if isinstance(cikis_kopya['tarih'], datetime.datetime):
                cikis_kopya['tarih'] = cikis_kopya['tarih'].isoformat()
            export_data["nakit_cikislar"].append(cikis_kopya)
        
        # Geçici dosya oluştur
        dosya_adi = f"nakit_akisi_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        dosya_yolu = os.path.join(app.config['UPLOAD_FOLDER'], dosya_adi)
        
        with open(dosya_yolu, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return send_file(dosya_yolu, as_attachment=True, download_name=dosya_adi)
        
    except Exception as e:
        print(f"JSON dışa aktarma hatası: {e}")
        return redirect(url_for('veri_export_sayfasi'))

@app.route('/export_csv/<veri_tipi>')
def export_csv(veri_tipi):
    """Belirli bir veri türünü CSV formatında dışa aktar"""
    try:
        import csv
        
        # CSV dosya adını belirle
        dosya_adi = f"nakit_akisi_{veri_tipi}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        dosya_yolu = os.path.join(app.config['UPLOAD_FOLDER'], dosya_adi)
        
        with open(dosya_yolu, 'w', encoding='utf-8', newline='') as f:
            csv_writer = csv.writer(f)
            
            if veri_tipi == "nakit_girisler":
                # CSV başlık satırı
                csv_writer.writerow(['Miktar', 'Tarih', 'Kategori', 'Açıklama', 'Taraf'])
                
                # Nakit girişlerini yaz
                for giris in platform.veri.get_nakit_girisler():
                    tarih_str = giris['tarih'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(giris['tarih'], datetime.datetime) else str(giris['tarih'])
                    csv_writer.writerow([
                        giris['miktar'],
                        tarih_str,
                        giris['kategori'],
                        giris['aciklama'],
                        giris['taraf'] or ''
                    ])
                    
            elif veri_tipi == "nakit_cikislar":
                # CSV başlık satırı
                csv_writer.writerow(['Miktar', 'Tarih', 'Kategori', 'Açıklama', 'Taraf'])
                
                # Nakit çıkışlarını yaz
                for cikis in platform.veri.get_nakit_cikislar():
                    tarih_str = cikis['tarih'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(cikis['tarih'], datetime.datetime) else str(cikis['tarih'])
                    csv_writer.writerow([
                        cikis['miktar'],
                        tarih_str,
                        cikis['kategori'],
                        cikis['aciklama'],
                        cikis['taraf'] or ''
                    ])
                    
            elif veri_tipi == "taraflar":
                # CSV başlık satırı
                csv_writer.writerow(['Taraf Adı', 'Toplam Nakit Girişi', 'Toplam Nakit Çıkışı', 'Bakiye'])
                
                # Taraf durumlarını hesapla
                taraf_durumlari = platform.taraf_bazli_nakit_durumu()
                
                # Tarafları yaz
                for taraf in platform.taraf_listele():
                    durum = taraf_durumlari.get(taraf, 0)
                    
                    # Toplam giriş ve çıkışları hesapla
                    toplam_giris = sum(giris['miktar'] for giris in platform.veri.get_nakit_girisler() 
                                      if giris.get('taraf') == taraf)
                    toplam_cikis = sum(cikis['miktar'] for cikis in platform.veri.get_nakit_cikislar() 
                                      if cikis.get('taraf') == taraf)
                    
                    csv_writer.writerow([
                        taraf,
                        toplam_giris,
                        toplam_cikis,
                        durum
                    ])
        
        return send_file(dosya_yolu, as_attachment=True, download_name=dosya_adi)
        
    except Exception as e:
        print(f"CSV dışa aktarma hatası: {e}")
        return redirect(url_for('veri_export_sayfasi'))

@app.route('/import_json', methods=['POST'])
def import_json():
    """JSON dosyasından veri içe aktar"""
    try:
        # Dosya kontrolü
        if 'import_file' not in request.files:
            return redirect(url_for('veri_export_sayfasi'))
        
        file = request.files['import_file']
        if file.filename == '':
            return redirect(url_for('veri_export_sayfasi'))
        
        # Yedek al
        veri_yedekle()
        
        # JSON dosyasını oku
        import_data = json.load(file)
        
        # Mevcut verileri temizle
        platform.veri.nakit_girisler = []
        platform.veri.nakit_cikislar = []
        platform.veri.taraflar = {}
        platform.veri.projeksiyonlar = {}
        platform.veri.raporlar = {}
        
        # Tarafları içe aktar
        if "taraflar" in import_data:
            for taraf in import_data["taraflar"]:
                if taraf not in platform.taraf_listele():
                    platform.taraf_ekle(taraf)
        
        # Nakit girişlerini içe aktar
        if "nakit_girisler" in import_data:
            for giris in import_data["nakit_girisler"]:
                try:
                    tarih = datetime.datetime.fromisoformat(giris['tarih']) if isinstance(giris['tarih'], str) else giris['tarih']
                    platform.nakit_girisi_ekle(
                        float(giris['miktar']),
                        tarih,
                        giris['kategori'],
                        giris['aciklama'],
                        giris['taraf']
                    )
                except Exception as e:
                    print(f"Giriş içe aktarma hatası: {e}")
        
        # Nakit çıkışlarını içe aktar
        if "nakit_cikislar" in import_data:
            for cikis in import_data["nakit_cikislar"]:
                try:
                    tarih = datetime.datetime.fromisoformat(cikis['tarih']) if isinstance(cikis['tarih'], str) else cikis['tarih']
                    platform.nakit_cikisi_ekle(
                        float(cikis['miktar']),
                        tarih,
                        cikis['kategori'],
                        cikis['aciklama'],
                        cikis['taraf']
                    )
                except Exception as e:
                    print(f"Çıkış içe aktarma hatası: {e}")
        
        # Verileri kaydet
        verileri_kaydet()
        
        return redirect(url_for('home'))
        
    except Exception as e:
        print(f"İçe aktarma hatası: {e}")
        return redirect(url_for('veri_export_sayfasi'))

@app.route('/yedekler')
def yedekler_sayfasi():
    """Mevcut yedekleri listele"""
    yedekler = []
    
    # Yedek klasörlerini listele
    try:
        if os.path.exists(app.config['BACKUP_FOLDER']):
            yedek_klasorler = sorted([d for d in os.listdir(app.config['BACKUP_FOLDER']) 
                                    if os.path.isdir(os.path.join(app.config['BACKUP_FOLDER'], d))], 
                                   reverse=True)  # En son yedekler üstte
            
            for klasor in yedek_klasorler:
                # Yedekleme zamanını daha okunabilir biçime çevir
                try:
                    timestamp = datetime.datetime.strptime(klasor, '%Y%m%d_%H%M%S')
                    okunabilir_tarih = timestamp.strftime('%d.%m.%Y %H:%M:%S')
                except:
                    okunabilir_tarih = klasor
                
                # Yedeklenen dosya sayısını kontrol et
                yedek_yolu = os.path.join(app.config['BACKUP_FOLDER'], klasor)
                dosya_sayisi = len([f for f in os.listdir(yedek_yolu) if os.path.isfile(os.path.join(yedek_yolu, f))])
                
                yedekler.append({
                    'id': klasor,
                    'tarih': okunabilir_tarih,
                    'dosya_sayisi': dosya_sayisi
                })
    except Exception as e:
        print(f"Yedekler listelenirken hata: {e}")
    
    return render_template('yedekler.html', yedekler=yedekler)

@app.route('/yedek_geri_yukle/<yedek_id>', methods=['POST'])
def yedek_geri_yukle(yedek_id):
    """Seçilen yedeği geri yükle"""
    try:
        # Yedeğin var olduğunu kontrol et
        yedek_yolu = os.path.join(app.config['BACKUP_FOLDER'], yedek_id)
        if not os.path.isdir(yedek_yolu):
            return redirect(url_for('yedekler_sayfasi'))
        
        # Mevcut verinin yedeğini al (işlem başarısız olursa geri dönebilmek için)
        veri_yedekle()
        
        # Her dosyayı geri yükle
        for dosya_adi in os.listdir(yedek_yolu):
            kaynak_dosya = os.path.join(yedek_yolu, dosya_adi)
            
            # Dosya türüne göre hedef belirle
            if dosya_adi == 'taraflar.json':
                hedef_dosya = TARAFLAR_DOSYA
            elif dosya_adi == 'nakit_girisler.json':
                hedef_dosya = NAKIT_GIRISLER_DOSYA
            elif dosya_adi == 'nakit_cikislar.json':
                hedef_dosya = NAKIT_CIKISLAR_DOSYA
            else:
                continue  # Bilinmeyen dosyaları atla
            
            # Dosyayı kopyala
            shutil.copy2(kaynak_dosya, hedef_dosya)
        
        # Platformu sıfırla ve verileri yükle
        platform.veri.nakit_girisler = []
        platform.veri.nakit_cikislar = []
        platform.veri.taraflar = {}
        platform.veri.projeksiyonlar = {}
        platform.veri.raporlar = {}
        
        # Verileri yeniden yükle
        verileri_yukle()
        
        return redirect(url_for('home'))
        
    except Exception as e:
        print(f"Yedek geri yükleme hatası: {e}")
        return redirect(url_for('yedekler_sayfasi'))

@app.route('/manuel_yedekle', methods=['POST'])
def manuel_yedekle():
    """Manuel yedekleme işlemi başlat"""
    veri_yedekle()
    return redirect(url_for('yedekler_sayfasi'))

if __name__ == '__main__':
    # templates ve static klasörlerini oluştur
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/img', exist_ok=True)
    
    app.run(debug=True) 