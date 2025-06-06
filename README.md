# Nakit Akışı Modülü

Bu modül, nakit akışlarını izlemek, tahmin etmek, optimize etmek ve raporlamak için kullanılan bir Python platformudur.

## Modüller

1. **models.py**: Veri yapılarını içeren temel sınıflar
2. **cash_operations.py**: Nakit giriş/çıkış işlemleri
3. **analysis.py**: Nakit akışı analiz fonksiyonları
4. **visualization.py**: Grafikler ve görselleştirmeler
5. **reports.py**: Raporlama fonksiyonları 
6. **optimization.py**: Nakit akışı optimizasyon algoritmaları
7. **main.py**: Ana platform sınıfı
8. **app.py**: Web tabanlı kullanıcı arayüzü
9. **run.py**: Uygulamayı başlatmak için çalıştırıcı

## Kurulum

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt
```

## Kullanım

### Web Uygulamasını Başlatma

Web arayüzünü başlatmak için:

```bash
# Normal başlatma
python run.py

# Örnek verilerle başlatma (demo modu)
python run.py --demo

# Farklı port numarasıyla başlatma
python run.py --port 8080
```

Ardından tarayıcınızda http://127.0.0.1:5000 adresini açarak web arayüzüne erişebilirsiniz.

### Uygulama Kullanımı

1. **Taraf Ekleme**: 
   - Sol menüden "Taraflar" sayfasına gidin
   - "Yeni Taraf Ekle" bölümünden müşteri, tedarikçi gibi tarafları ekleyin
   
2. **İşlem Ekleme**:
   - Sol menüden "İşlemler" sayfasına gidin
   - Yeni nakit girişi veya çıkışı ekleyin
   - Kategori ve taraf (isteğe bağlı) belirtin

3. **Tahmin ve Analiz**:
   - Gösterge panelinde genel görünümü inceleyin
   - Grafikler ve tablolar üzerinden nakit akışını takip edin
   - "Simülasyon" sayfasından gelecek tahminleri oluşturun

4. **Optimizasyon**:
   - "Optimizasyon" sayfasından nakit akışınızı optimize edin
   - İşlem sayısını ve maliyetleri minimize edin

5. **Raporlama**:
   - "Raporlar" sayfasından aylık veya yıllık raporlar oluşturun
   - Excel formatında dışa aktarın

6. **Veri Yönetimi**:
   - "Veri Yedekleri" sayfasından otomatik ve manuel yedekleri yönetin
   - "Veri Aktarımı" sayfasından verileri dışa/içe aktarın
   - CSV ve JSON formatlarında dışa aktarma seçenekleri

### Veri Yedekleme ve Aktarım

Uygulamada veri yönetimi için aşağıdaki özellikler bulunur:

1. **Otomatik Yedekleme**: Her veri değişikliğinde sistem otomatik olarak yedek oluşturur (son 10 yedek saklanır)
2. **Manuel Yedekleme**: "Veri Yedekleri" sayfasından manuel yedek oluşturabilirsiniz
3. **Yedeği Geri Yükleme**: Eski bir yedeğe dönmek isterseniz, yedekler listesinden geri yükleme yapabilirsiniz
4. **JSON Dışa Aktarma**: Tüm verileri JSON formatında dışa aktarabilirsiniz
5. **CSV Dışa Aktarma**: Nakit girişleri, çıkışları ve tarafları CSV formatında dışa aktarabilirsiniz
6. **JSON İçe Aktarma**: Daha önce dışa aktarılmış JSON verilerini geri yükleyebilirsiniz

### Demo Modu

Uygulamayı örnek verilerle başlatmak için demo modunu kullanabilirsiniz:

```bash
python run.py --demo
```

Demo modu aşağıdakileri otomatik olarak ekler:
- Örnek taraflar (müşteriler ve tedarikçiler)
- Son üç aya ait düzenli nakit giriş/çıkışları
- Taraf bazlı işlemler
- Kategori ve tarih bazlı çeşitli veriler

Bu, uygulamayı test etmek veya özelliklerini görmek için idealdir.

## Hata Giderme

Eğer uygulama çalışırken hata alırsanız:

1. Bağımlılıkların tam olarak yüklendiğinden emin olun:
   ```bash
   pip install -r requirements.txt
   ```

2. `static/img` klasörünün yazılabilir olduğunu kontrol edin:
   ```bash
   mkdir -p static/img
   ```

3. Matplotlib ile ilgili hatalar için:
   ```python
   # visualization.py dosyasında backend ayarı doğru yapılmalıdır
   import matplotlib
   matplotlib.use('Agg')  # Non-interactive backend
   import matplotlib.pyplot as plt
   ```

4. Veri kaydetme/yükleme sorunları için:
   ```bash
   # data klasörünün varlığını kontrol edin
   mkdir -p data
   # data klasörünün yazılabilir olduğundan emin olun
   ```

5. Yedekleme sorunları için data/backups klasörünün varlığını kontrol edin:
   ```bash
   mkdir -p data/backups
   ```

## Özellikler

- **Temel Nakit Akışı İşlemleri**
  - Nakit giriş ve çıkışlarının takibi ve kayıtları
  - Kategori bazlı gelir-gider izleme
  - Bakiye görüntüleme ve raporlama

- **Tahmin ve Analiz**
  - Gelecek dönem nakit akışı tahminleri
  - Kategori bazlı nakit akışı analizi
  - Grafikler ve görselleştirmeler

- **Taraf Yönetimi**
  - Müşteriler, tedarikçiler ve diğer tarafları izleme
  - Taraf bazlı nakit akışı takibi
  - Taraf performans analizi

- **Optimizasyon**
  - İşlem sayısını azaltma optimizasyonu
  - İşlem maliyetlerini minimize etme
  - Monte Carlo simülasyonu ile nakit akışı senaryoları

- **Veri Yönetimi**
  - Otomatik ve manuel veri yedekleme
  - Yedekleri geri yükleme
  - CSV ve JSON formatlarında dışa/içe aktarma
  - Veri sıfırlama ve temizleme

- **Web Arayüzü**
  - Modern ve duyarlı tasarım
  - Kolay kullanımlı formlar ve grafikler
  - Otomatik grafik oluşturma ve raporlama
  - Boş veri durumlarında kullanıcı dostu arayüz

## Katkıda Bulunma

Projeye katkıda bulunmak için:

1. Bu repoyu fork edin
2. Özellik dalınızı oluşturun: `git checkout -b yeni-ozellik`
3. Değişikliklerinizi commit edin: `git commit -am 'Yeni özellik: detaylar'`
4. Dalınızı push edin: `git push origin yeni-ozellik`
5. Pull Request gönderin #   C a s h F l o w O p t i m i z a t i o n  
 