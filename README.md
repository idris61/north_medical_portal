# North Medical - ERPNext E-Commerce & Dealer Portal Platform

**Kapsamlı ERPNext tabanlı e-ticaret ve bayi portal sistemi**

North Medical Germany için geliştirilmiş, ERPNext v15 üzerine kurulu, profesyonel e-ticaret platformu ve dealer portal yönetim sistemi. Sistem, ana şirket ve bayiler arasında dinamik stok takibi, otomatik sipariş akışı ve kapsamlı portal yönetimi sağlar.

---

## 📋 İçindekiler

- [Genel Bakış](#genel-bakış)
- [Mimari Yapı](#mimari-yapı)
- [Uygulamalar](#uygulamalar)
- [Özellikler](#özellikler)
- [Kurulum](#kurulum)
- [Yapılandırma](#yapılandırma)
- [Geliştirme](#geliştirme)
- [Dokümantasyon](#dokümantasyon)

---

## 🎯 Genel Bakış

North Medical platformu, iki ana uygulamadan oluşur:

1. **Webshop App**: Genel e-ticaret özellikleri (tüm projelerde ortak kullanılır)
   - Ürün kataloğu ve listeleme
   - Sepet yönetimi
   - Sipariş işlemleri
   - Arama ve filtreleme
   - Çoklu dil desteği

2. **North Medical Portal**: North Medical'e özel geliştirmeler
   - Dealer portal sistemi
   - Stok takibi ve otomasyonu
   - Malzeme talepleri yönetimi
   - Satış siparişleri ve faturalar
   - Brand-specific styling

### Teknik Özellikler

- **Framework**: Frappe Framework v15
- **ERP Sistemi**: ERPNext v15
- **Veritabanı**: MariaDB
- **Cache**: Redis
- **Frontend**: JavaScript ES6+, jQuery, Bootstrap 4
- **Backend**: Python 3.12
- **Arama**: RediSearch (opsiyonel)

---

## 🏗️ Mimari Yapı

### Proje Yapısı

```
north_medical/
├── apps/
│   ├── frappe/                    # Frappe Framework core
│   ├── erpnext/                   # ERPNext core
│   ├── payments/                  # Payment gateway entegrasyonu
│   ├── webshop/                   # E-ticaret uygulaması (GENEL)
│   └── north_medical_portal/      # Dealer portal uygulaması (ÖZEL)
├── sites/                         # Site yapılandırmaları
├── config/                        # Sistem yapılandırmaları
├── env/                           # Python virtual environment
├── logs/                          # Log dosyaları
└── assets/                        # Statik dosyalar
```

### Mimari Prensip

**Separation of Concerns (SoC)** prensibi uygulanmıştır:

- **Webshop App**: Genel e-ticaret özellikleri - Tüm projelerde ortak kullanılır
  - Cart, Wishlist, Order sayfaları
  - Ürün listeleme ve filtreleme
  - Arama ve sıralama
  - Sepet yönetimi
  - Dil seçici

- **North Medical Portal**: Sadece North Medical'e özel geliştirmeler
  - Dealer portal sayfaları
  - Brand styling (navbar, footer)
  - Stok otomasyonu
  - Product badges
  - Custom fields

### Şirket Yapısı

```
North Medical (Ana Şirket)
├── Warehouse: North Medical - Ana Depo
├── Ürün Master Data
└── Bayiler
    ├── Bayi 1 (Ayrı Şirket)
    │   ├── Warehouse: Bayi 1 - Depo
    │   └── Portal Kullanıcıları
    └── Bayi 2 (Ayrı Şirket)
        ├── Warehouse: Bayi 2 - Depo
        └── Portal Kullanıcıları
```

---

## 📦 Uygulamalar

### 1. Webshop App

**Genel e-ticaret platformu - Tüm projelerde ortak kullanılır**

#### Özellikler

**Performans Optimizasyonları**
- **Arama Performansı**: 200ms debounce mekanizması ile RediSearch entegrasyonu
- **API Caching**: 5 dakikalık Redis cache ile ürün filtre sorguları (%95 daha hızlı)
- **Batch Queries**: Custom field'lar için optimize edilmiş veritabanı sorguları
- **Frontend Optimizasyonu**: Küçültülmüş bundle boyutu (33.07 KB)

**UI/UX İyileştirmeleri**
- **Profesyonel Toolbar**: Özel Sort By ve Show kontrolleri ile responsive tasarım
- **Gelişmiş Arama**: Ürün ve kategori önerileri ile gerçek zamanlı autocomplete
- **Fiyat Aralığı Filtresi**: Min/max input'ları ile özel fiyat filtreleme
- **Görünüm Değiştirme**: localStorage kalıcılığı ile sorunsuz Grid/List görünüm değiştirme
- **Responsive Tasarım**: Mobile-first yaklaşım ile optimize edilmiş layout'lar

**Yeni Özellikler**
- **Custom Short Description**: Liste sayfalarında ürün detay kartları
- **Kitchen Product Filter**: Optimize edilmiş UI ile boolean filtre
- **Supplier Filter**: Çoklu seçim tedarikçi filtreleme
- **Stock Unit Filter**: UOM tabanlı ürün filtreleme
- **MutationObserver**: Filtre değişikliklerinde otomatik toolbar kontrolü geri yükleme

**Sepet Yönetimi**
- **Miktar Senkronizasyonu**: Tüm sayfalarda senkronize sepet miktarları
- **Single Source of Truth**: Backend Quotation ile sepet durumu
- **Akıllı "View in Cart"**: Yönlendirmeden önce sepeti otomatik güncelleme
- **Profesyonel Miktar Seçici**: Tarayıcı spinner'ları olmadan temiz integer-only input'lar

**Varyant Ürün Desteği**
- **Varyant Seçimi**: Görsel geri bildirim ile interaktif boyut/renk/özellik butonları
- **Gerçek Zamanlı Varyant Eşleştirme**: Tüm özellikler seçildiğinde otomatik varyant bulma
- **UOM Desteği**: Dinamik UOM seçici ile fiyat dönüşümü
- **Miktar Yönetimi**: Profesyonel +/- butonları ile miktar seçimi

#### Yapı

```
webshop/
├── webshop/
│   ├── api.py                      # Core API endpoint
│   ├── shopping_cart/              # Sepet yönetimi
│   │   ├── cart.py                 # Sepet CRUD işlemleri
│   │   ├── product_info.py         # Ürün fiyat/stok bilgisi
│   │   └── utils.py                # Sepet yardımcı fonksiyonları
│   ├── product_data_engine/         # Ürün veri motoru
│   │   ├── query.py                # Ürün sorgu motoru
│   │   └── filters.py              # Dinamik filtre oluşturma
│   ├── variant_selector/           # Varyant seçici
│   ├── utils/                      # Yardımcı modüller
│   │   ├── product.py              # Ürün yardımcıları
│   │   ├── translation.py           # Çeviri yönetimi
│   │   └── portal.py               # Portal yardımcıları
│   └── crud_events/                # CRUD event handler'ları
├── public/
│   ├── js/
│   │   ├── product_ui/             # Ürün UI modülleri
│   │   │   ├── views.js             # Ana görünüm kontrolcüsü
│   │   │   ├── grid.js              # Grid görünüm
│   │   │   ├── list.js              # List görünüm
│   │   │   ├── search.js            # Arama autocomplete
│   │   │   └── product_card_base.js  # Ortak kart fonksiyonları
│   │   ├── shopping_cart.js         # Sepet yönetimi
│   │   └── wishlist.js              # İstek listesi
│   └── scss/                       # Stil dosyaları
├── templates/                      # Jinja2 şablonları
└── translations/                   # Çeviri dosyaları
```

#### Performans Metrikleri

| Özellik | Önce | Sonra | İyileştirme |
|---------|------|-------|-------------|
| Arama Yanıtı | Her tuş vuruşu | 200ms debounce | %80 daha az istek |
| Filtre API | 500ms | 10-20ms (cache'li) | %95 daha hızlı |
| Bundle Boyutu | 33.69 KB | 33.02 KB | -400 bytes |
| Kod Tekrarı | ~100 satır | 0 satır | %100 kaldırıldı |

**Detaylı dokümantasyon için**: [apps/webshop/README.md](apps/webshop/README.md)

---

### 2. North Medical Portal

**North Medical Germany'ye özel dealer portal sistemi**

#### Özellikler

**Website Yapılandırması**
- **Navbar Styling**: North Medical brand renklerine özel navbar (beyaz arka plan, turkuaz alt çizgi, koyu mavi menü)
- **Footer Styling**: Brand renklerine özel footer tasarımı
- **Back to Top Button**: Sayfa scroll için buton
- **Portal Navigation**: Dealer portal sayfalarına özel navigasyon linkleri

**Dealer Portal Sistemi**

**Portal Sayfaları:**
- **Stok Durumu** (`/portal/stock`): Bayilerin anlık stok durumlarını görüntüleme, reorder level düzenleme, minimum stok kontrolü
- **Stok Özeti Print** (`/portal/stock-summary-print`): Stok özeti yazdırma sayfası
- **Satış Siparişleri** (`/portal/sales-orders`): Bayi satış siparişlerini listeleme ve görüntüleme
- **Faturalar** (`/portal/invoices`): Bayi faturalarını görüntüleme
- **Malzeme Talepleri** (`/portal/material-requests`): Material Request listeleme, sepete ekleme ve yönetimi
- **Malzeme Talebi Detay** (`/portal/material-request/<name>`): Material Request detay sayfası
- **Stok Hareketleri** (`/portal/stock-entries`): Stock Entry listeleme
- **Malzeme Çıkışı** (`/portal/material-issue`): Material Issue (Stock Entry) listeleme ve yönetimi
- **Malzeme Çıkışı Oluştur** (`/portal/material-issue/new`): Yeni Material Issue oluşturma formu
- **Malzeme Çıkışı Düzenle** (`/portal/material-issue/edit/<name>`): Material Issue düzenleme formu
- **Malzeme Çıkışı Detay** (`/portal/stock-entry/<name>`): Stock Entry detay sayfası

**API Endpoints:**
- **Stock API**: Stok durumu sorgulama, ürün arama, reorder level güncelleme
- **Sales Orders API**: Satış siparişleri listeleme
- **Invoices API**: Fatura listeleme
- **Material Request API**: Material Request oluşturma, listeleme, sepete ekleme
- **Stock Entry API**: Stock Entry CRUD işlemleri

**Otomatik Stok Yönetimi**
- **Delivery Note Otomasyonu**: Delivery Note submit edildiğinde müşterinin deposuna otomatik stok transferi
- **Reorder Level Kontrolü**: Günlük scheduler ile otomatik reorder level kontrolü ve Material Request oluşturma
- **Material Request Durum Güncelleme**: Sales Order oluşturulduğunda Material Request durumu otomatik güncellenir

**Product Badges**
- Ürün badge sistemi (Item ve Website Item'da)
- Badge görseli, link ve sıralama desteği
- Product Badge DocType ile badge yönetimi

**Custom Fields**
- **Item DocType**: `short_description` (Text Editor), `product_badges` (Table)
- **Website Item DocType**: `product_badges` (Table)

**Güvenlik & İzinler**
- **Dealer Access Validation**: Kullanıcının bayi erişim yetkisini kontrol eder
- **Company-based Access**: Her bayi sadece kendi şirket verilerine erişebilir
- **User Company Detection**: Kullanıcının bağlı olduğu şirketi otomatik bulur
- **Warehouse Filtering**: Şirkete özel warehouse listesi

**Çoklu Dil Desteği**
- **5 Dil**: Türkçe (TR), İngilizce (EN), Almanca (DE), Fransızca (FR), İtalyanca (IT)
- **Çeviri Dosyaları**: CSV formatında (`translations/tr.csv`, `en.csv`, `de.csv`, `fr.csv`, `it.csv`)
- **Kapsamlı Çeviri**: Tüm butonlar, alanlar, etiketler, filtreler ve mesajlar çevrilmiş

**Print Formatlar**
- **Sales Order Portal**: Satış siparişleri için özel print format
- **Sales Invoice Portal**: Faturalar için özel print format
- **Delivery Note Portal**: Teslimat notları için özel print format
- **Material Request Portal**: Malzeme talepleri için özel print format
- **Stock Entry Portal**: Stok hareketleri için özel print format
- **Stock Summary Print**: Stok özeti için özel print sayfası
- **Dil Seçimi**: Print preview'da dil dropdown'u (TR, EN, DE, FR, IT)

#### Yapı

```
north_medical_portal/
├── hooks.py                        # Hook tanımları (scheduler, website context, doc events)
├── utils/
│   ├── website.py                 # Website yapılandırması (CSS, styling) - ÖZEL
│   ├── stock.py                   # Stok kontrolü ve Material Request - ÖZEL
│   ├── delivery_note.py            # Delivery Note otomasyonu - ÖZEL
│   ├── sales_order.py             # Sales Order Material Request güncelleme - ÖZEL
│   ├── helpers.py                 # Ortak helper fonksiyonlar
│   ├── bulk_pricing_and_stock.py  # Toplu fiyat ve stok ayarları
│   ├── portal_permissions.py      # Portal izin yönetimi
│   ├── material_request_permission.py # Material Request izinleri
│   └── override_erpnext_permissions.py # ERPNext izin override'ları
├── www/
│   ├── api/                       # API endpoint'leri - ÖZEL
│   │   ├── stock.py               # Stok durumu API
│   │   ├── sales_orders.py        # Satış siparişleri API
│   │   ├── invoices.py            # Faturalar API
│   │   ├── material_request.py    # Material Request API
│   │   └── stock_entry.py         # Stock Entry API
│   ├── portal/                    # Portal sayfaları - ÖZEL
│   │   ├── stock/                 # Stok durumu sayfası
│   │   ├── stock-summary-print/   # Stok özeti print sayfası
│   │   ├── sales-orders/          # Satış siparişleri sayfası
│   │   ├── invoices/              # Faturalar sayfası
│   │   ├── material-requests/     # Malzeme talepleri sayfası
│   │   ├── material-request-detail/ # Malzeme talebi detay sayfası
│   │   ├── material-issue/        # Malzeme çıkışı sayfaları
│   │   ├── stock-entry/           # Stock Entry detay sayfası
│   │   └── stock-entries/         # Stok hareketleri sayfası
│   ├── printview.html             # Print preview override (dil seçimi)
│   ├── printview.py               # Print preview context override
│   └── home/                      # Ana sayfa override
├── templates/
│   └── pages/
│       └── order.html             # Order detail page override
├── translations/                  # Çeviri dosyaları - ÖZEL
│   ├── tr.csv                     # Türkçe çeviriler
│   ├── en.csv                     # İngilizce çeviriler
│   ├── de.csv                     # Almanca çeviriler
│   ├── fr.csv                     # Fransızca çeviriler
│   └── it.csv                     # İtalyanca çeviriler
├── dealer_portal/
│   └── doctype/
│       └── dealer_settings/       # Dealer Settings DocType
├── portal/
│   └── doctype/
│       └── product_badge/         # Product Badge DocType - ÖZEL
├── templates/                     # Footer extensions - ÖZEL
└── fixtures/
    └── custom_field.json           # Custom field'lar - ÖZEL
```

**Detaylı dokümantasyon için**: [apps/north_medical_portal/README.md](apps/north_medical_portal/README.md)

---

## 🚀 Özellikler

### E-Ticaret Özellikleri (Webshop)

- ✅ Ürün kataloğu ve varyant desteği
- ✅ Gelişmiş arama ve filtreleme (RediSearch entegrasyonu)
- ✅ Sepet yönetimi (senkronize miktarlar)
- ✅ İstek listesi (Wishlist)
- ✅ Sipariş yönetimi
- ✅ Çoklu dil desteği (TR, EN, DE, FR, IT)
- ✅ Responsive tasarım
- ✅ Grid/List görünüm değiştirme
- ✅ Fiyat aralığı filtreleme
- ✅ Tedarikçi ve UOM filtreleme
- ✅ Ürün önerileri
- ✅ Müşteri yorumları ve puanlama

### Dealer Portal Özellikleri (North Medical Portal)

- ✅ **Stok Yönetimi**
  - Gerçek zamanlı stok durumu görüntüleme
  - Reorder level düzenleme
  - Minimum stok kontrolü
  - Otomatik Material Request oluşturma
  - Stok özeti yazdırma

- ✅ **Malzeme Talepleri**
  - Material Request listeleme ve görüntüleme
  - Material Request'i sepete ekleme
  - Otomatik durum güncelleme
  - Durum ilerlemesi: Draft → Pending → Partially Ordered → Ordered

- ✅ **Satış Siparişleri**
  - Satış siparişleri listeleme ve görüntüleme
  - Sipariş durumu takibi
  - Material Request entegrasyonu
  - Özel print format

- ✅ **Faturalar**
  - Fatura listeleme ve görüntüleme
  - Ödeme durumu takibi
  - Özel print format

- ✅ **Stok Hareketleri**
  - Stock Entry listeleme ve görüntüleme
  - Material Issue (Stock Entry) oluşturma, düzenleme, iptal etme
  - Otomatik warehouse seçimi
  - Gerçek zamanlı stok miktarı gösterimi
  - Özel print format

- ✅ **Otomasyonlar**
  - Delivery Note submit'te otomatik stok transferi
  - Günlük reorder level kontrolü
  - Material Request durum güncelleme
  - Sales Order'dan Material Request güncelleme

---

## 📦 Kurulum

### Gereksinimler

- **Python**: 3.12+
- **Node.js**: v20.19.2+
- **MariaDB**: 10.6+
- **Redis**: 6.0+ (opsiyonel, arama optimizasyonu için)
- **Frappe Bench**: v5.0+

### Adım Adım Kurulum

#### 1. Frappe Bench Kurulumu

```bash
# Bench kurulumu (ilk kez)
pip3 install frappe-bench

# Bench başlatma
bench init north_medical
cd north_medical
```

#### 2. ERPNext ve Gerekli App'leri Yükleme

```bash
# ERPNext yükleme
bench get-app erpnext

# Payments app yükleme
bench get-app payments

# Webshop app yükleme
bench get-app https://github.com/idris61/webshop.git

# North Medical Portal app yükleme
bench get-app https://github.com/idris61/north_medical_portal.git
```

#### 3. Site Oluşturma ve App'leri Yükleme

```bash
# Site oluşturma
bench new-site north_medical.local

# App'leri yükleme
bench --site north_medical.local install-app erpnext
bench --site north_medical.local install-app payments
bench --site north_medical.local install-app webshop
bench --site north_medical.local install-app north_medical_portal
```

#### 4. Asset'leri Build Etme

```bash
# Tüm app'ler için asset build
bench build --app webshop
bench build --app north_medical_portal

# Veya tüm app'ler için
bench build
```

#### 5. Cache Temizleme

```bash
bench --site north_medical.local clear-cache
bench --site north_medical.local clear-website-cache
```

#### 6. Scheduler ve Worker Başlatma

```bash
# Scheduler başlatma (otomatik stok kontrolü için)
bench --site north_medical.local schedule

# Worker başlatma (background job'lar için)
bench --site north_medical.local worker
```

#### 7. Development Server Başlatma

```bash
# Development server
bench start

# Veya production için
bench serve --port 8006
```

### Production Deployment

Production ortamı için `Procfile` kullanılabilir:

```bash
# Production için tüm servisleri başlat
foreman start
```

---

## ⚙️ Yapılandırma

### 1. Webshop Yapılandırması

**Webshop Settings** (`/app/webshop-settings`) üzerinden:

- Ürünler sayfa başına (varsayılan: 20)
- RediSearch'i etkinleştir (daha hızlı arama için)
- Filtre alanları yapılandırması
- Alışveriş sepeti ayarları

**Custom Fields:**
- **Item DocType**: `custom_short_description` (Text Editor)
- **Website Item DocType**: `custom_short_description` (Small Text)

### 2. North Medical Portal Yapılandırması

**Dealer Settings** (`/app/dealer-settings`) üzerinden:

- Stok transferleri için kaynak warehouse
- Dealer operasyonları için varsayılan ayarlar

**Kullanıcı Şirket Kurulumu:**
- Kullanıcıların `company` alanı bayi şirketlerine ayarlanmalı
- Veya role-based şirket algılama (örn: "Dealer Manager - Bayi 1")

**Warehouse Kurulumu:**
- Her bayi şirketi için warehouse'lar yapılandırılmalı
- Warehouse isimleri naming convention'a uymalı (örn: "Bayi-1 - NM")

### 3. Şirket Yapısı Kurulumu

1. **Ana Şirket Oluşturma**
   - Company: "North Medical"
   - Warehouse: "North Medical - Ana Depo"

2. **Bayi Şirketleri Oluşturma**
   - Company: "Bayi 1", "Bayi 2", vb.
   - Her bayi için warehouse oluşturma
   - Warehouse isimleri: "Bayi-1 - NM", "Bayi-2 - NM", vb.

3. **Kullanıcı Kurulumu**
   - Her bayi için portal kullanıcıları oluşturma
   - Kullanıcılara `company` alanı atama
   - Role: "Customer" veya "Dealer Manager"

### 4. Item Reorder Level Yapılandırması

Her ürün için minimum stok seviyesi belirlenmelidir:

1. **Item** DocType'ı aç
2. **Reorder Levels** tab'ına git
3. Her warehouse için:
   - **Warehouse**: Warehouse seç
   - **Material Request Type**: "Purchase" seç
   - **Warehouse Reorder Level**: Minimum stok seviyesi
   - **Warehouse Reorder Qty**: Yeniden sipariş miktarı

### 5. Redis Yapılandırması (Opsiyonel)

Arama performansı için Redis kurulumu:

```bash
# Redis kurulumu (Ubuntu/Debian)
sudo apt-get install redis-server

# Redis başlatma
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Bench'te Redis yapılandırması
bench set-config -g redis_cache redis://localhost:6379
bench set-config -g redis_queue redis://localhost:6379
```

---

## 🔧 Geliştirme

### Geliştirme Ortamı Kurulumu

```bash
# Development mode'da başlat
bench start

# Watch mode (otomatik reload)
bench watch

# Worker (background jobs)
bench --site north_medical.local worker
```

### Kod Stili

- **Yorumlar**: İngilizce
- **Türkçe Çeviriler**: Sadece çeviri dosyalarında (`translations/*.csv`)
- **Clean Code**: DRY, Single Responsibility prensipleri
- **Anlamlı İsimler**: Fonksiyon ve değişken isimleri açıklayıcı olmalı

### API Geliştirme

```python
# Tüm API'ler @frappe.whitelist() decorator kullanmalı
@frappe.whitelist()
def my_api():
    # Permission kontrolü
    validate_dealer_access()
    
    # Company-based data filtering
    company = get_user_company()
    
    # Error handling
    try:
        # API logic
        pass
    except Exception as e:
        frappe.throw(str(e))
```

### Portal Sayfası Geliştirme

```python
# Portal sayfası context
def get_context(context):
    # Permission kontrolü
    validate_dealer_access()
    
    # Company detection
    company = get_user_company()
    
    # Dynamic content için cache'i kapat
    context.no_cache = 1
    
    # Translations
    context.title = _("Stock Status")
    
    return context
```

### Çeviri Ekleme

1. **Çeviri Dosyasına Ekle** (`translations/tr.csv`):
   ```csv
   Source Text,Translated Text,
   Stock Status,Stok Durumu,
   ```

2. **Python'da Kullan**:
   ```python
   title = _("Stock Status")
   ```

3. **JavaScript'te Kullan**:
   ```javascript
   title = __("Stock Status");
   ```

4. **Build ve Cache Temizle**:
   ```bash
   bench build
   bench --site all clear-cache
   bench restart
   ```

### Test

```bash
# App testleri çalıştır
bench --site north_medical.local run-tests --app webshop
bench --site north_medical.local run-tests --app north_medical_portal

# Cache temizle (test için)
bench --site north_medical.local clear-cache
bench --site north_medical.local clear-website-cache
```

---

## 📚 Dokümantasyon

### Ana Dokümantasyon

- **Webshop App**: [apps/webshop/README.md](apps/webshop/README.md)
- **North Medical Portal**: [apps/north_medical_portal/README.md](apps/north_medical_portal/README.md)
- **Proje Planı**: [PLAN.md](PLAN.md)
- **Webshop Analiz Raporu**: [WEBSHOP_APP_ANALIZ_RAPORU.md](WEBSHOP_APP_ANALIZ_RAPORU.md)

### Ek Dokümantasyon

- **Navbar Menu Ekleme**: [NAVBAR_MENU_EKLEME.md](NAVBAR_MENU_EKLEME.md)
- **Sepet Kodları Analiz**: [SEPET_KODLARI_ANALIZ_RAPORU.md](SEPET_KODLARI_ANALIZ_RAPORU.md)
- **Product UOM Değişiklikleri**: [PRODUCT_UOM_CHANGES_REPORT.md](PRODUCT_UOM_CHANGES_REPORT.md)

### Harici Dokümantasyon

- **ERPNext**: [https://docs.erpnext.com](https://docs.erpnext.com)
- **Frappe Framework**: [https://frappeframework.com/docs](https://frappeframework.com/docs)
- **ERPNext E-Commerce**: [https://docs.erpnext.com/docs/user/manual/en/set_up_e_commerce](https://docs.erpnext.com/docs/user/manual/en/set_up_e_commerce)

---

## 🔐 Güvenlik

### Erişim Kontrolü

- Tüm portal sayfaları ve API'ler dealer erişim yetkisini kontrol eder
- Kullanıcılar sadece kendi şirket verilerine erişebilir
- Guest kullanıcılar portal sayfalarına erişemez

### İzin Doğrulama

- `validate_dealer_access()`: Kullanıcı izinlerini kontrol eder
- Company-based data filtering: Şirket bazlı veri filtreleme
- Warehouse filtering: Şirkete özel warehouse listesi

### API Güvenliği

- Tüm API'ler `@frappe.whitelist()` decorator kullanır
- Permission kontrolleri her API'de mevcuttur
- CSRF koruması Frappe Framework tarafından sağlanır
- Input validation Frappe ORM ile otomatik yapılır

---

## 🌐 Çoklu Dil Desteği

### Desteklenen Diller

- **Türkçe (TR)**: Tam destek
- **İngilizce (EN)**: Full support
- **Almanca (DE)**: Vollständige Unterstützung
- **Fransızca (FR)**: Support complet
- **İtalyanca (IT)**: Supporto completo

### Çeviri Kapsamı

- ✅ Tüm portal sayfaları
- ✅ Tüm print formatlar
- ✅ Tüm butonlar ve aksiyon etiketleri
- ✅ Tüm form alanları ve etiketleri
- ✅ Tüm filtre seçenekleri ve etiketleri
- ✅ Tüm ürün sayfası elementleri
- ✅ Tüm hata ve başarı mesajları

---

## 📊 Performans

### Optimizasyonlar

- **Redis Caching**: 5 dakikalık TTL ile API cache
- **Debounced Search**: 200ms debounce ile arama optimizasyonu
- **Batch Queries**: Toplu veritabanı sorguları
- **Lazy Loading**: Görüntü lazy loading
- **Optimized Bundles**: Küçültülmüş CSS/JS bundle'ları

### Performans Metrikleri

| Özellik | Önce | Sonra | İyileştirme |
|---------|------|-------|-------------|
| Arama Yanıtı | Her tuş vuruşu | 200ms debounce | %80 daha az istek |
| Filtre API | 500ms | 10-20ms (cache'li) | %95 daha hızlı |
| Bundle Boyutu | 33.69 KB | 33.02 KB | -400 bytes |

---

## 🐛 Sorun Giderme

### Yaygın Sorunlar

**1. Cache Sorunları**
```bash
bench --site north_medical.local clear-cache
bench --site north_medical.local clear-website-cache
bench restart
```

**2. Asset Build Sorunları**
```bash
bench build --app webshop
bench build --app north_medical_portal
bench restart
```

**3. Permission Sorunları**
- Kullanıcının `company` alanını kontrol et
- Role'lerin doğru atandığını kontrol et
- `validate_dealer_access()` fonksiyonunu kontrol et

**4. Scheduler Çalışmıyor**
```bash
# Scheduler'ı kontrol et
bench --site north_medical.local schedule

# Worker'ı kontrol et
bench --site north_medical.local worker
```

**5. Redis Bağlantı Sorunları**
```bash
# Redis durumunu kontrol et
redis-cli ping

# Redis yapılandırmasını kontrol et
bench get-config redis_cache
bench get-config redis_queue
```

---

## 🤝 Katkıda Bulunma

1. Repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

### Commit Mesajları

- İngilizce yazın
- Açıklayıcı ve kısa olun
- Örnek: `feat: Add stock status API endpoint`

---

## 📄 Lisans

- **Webshop App**: GNU General Public License v3.0
- **North Medical Portal**: MIT License

---

## 🙏 Teşekkürler

- **Frappe Technologies**: Frappe Framework ve ERPNext için
- **North Medical Germany**: Projeye verdiği destek için

---

## 📞 İletişim

- **Email**: info@north-medical-germany.com
- **GitHub**: 
  - [Webshop](https://github.com/idris61/webshop)
  - [North Medical Portal](https://github.com/idris61/north_medical_portal)

---

**Developed with ❤️ for North Medical Germany**

*Son Güncelleme: 2024*

