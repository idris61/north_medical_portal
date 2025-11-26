# Website Settings Yapılandırma Kılavuzu

Tüm navbar, header ve footer yapılandırmaları **Website Settings** formundan yapılır. Kod tarafında hard-coded değer yoktur.

## 📋 Website Settings'e Erişim

**Website → Web Sitesi Ayarları** (Website → Website Settings)

## 🔧 Yapılandırma Alanları

### 1. Footer (Alt Bilgi) Tab

#### Footer Items
- **Footer Items** tablosuna linkler ekleyebilirsiniz
- Örnek: Hakkımızda, İletişim, Gizlilik Politikası vb.

#### Altbilgi Ayrıntıları (Footer Details)

**Copyright:**
```
Copyright 2019 - 2025 | North Medical Germany | All Rights Reserved
```

**Adres (Address):**
```
North Medical Germany
Medzenith GmbH
Mühlenweg 131-139, 22844 Norderstedt
```

**Footer Logo:**
- Footer'da gösterilecek logo ekleyebilirsiniz

**Alt Bilgi "Tarafından desteklenmektedir" (Footer Powered):**
- İsteğe bağlı: Footer'da "Powered by" metni

#### Footer Contact Information (Yeni Alan)

**Contact Information (HTML):**
Footer'da gösterilecek iletişim bilgileri (HTML formatında):

```html
<p><strong>North Medical Germany</strong></p>
<p>Medzenith GmbH</p>
<p>Mühlenweg 131-139, 22844 Norderstedt</p>
<p><a href="mailto:info@north-medical-germany.com" class="footer-link">E-Mail: info@north-medical-germany.com</a></p>
<p><a href="tel:+494021995055" class="footer-link">Tel: +49 40 21 99 50 55</a></p>
```

**Not:** Bu alan boşsa, "Adres" alanı kullanılır.

### 2. Gezinti Çubuğu (Navbar) Tab

**Navbar Template:**
- Custom navbar template seçebilirsiniz (varsayılan: Standard Navbar)

**Show Language Picker:**
- Dil seçiciyi açıp kapatabilirsiniz (✅ işaretli olmalı)

**Navbar Search:**
- Navbar'da arama kutusunu açıp kapatabilirsiniz

### 3. Ana Sayfa (Home Page) Tab

**Brand HTML:**
- Logo ve marka HTML'i

**Banner Image:**
- Ana sayfa banner görseli

**App Logo:**
- Uygulama logosu

**Favicon:**
- Site favicon'u

## 🎨 CSS Stilleri

CSS stilleri (renkler, fontlar) kod tarafında tanımlıdır ve Website Settings'ten değiştirilemez:
- Navbar: Beyaz arka plan, turkuaz alt çizgi, kırmızı menü
- Footer: Koyu mavi arka plan, turkuaz üst çizgi, beyaz metin

## 📝 Örnek Yapılandırma

### Footer Contact Information (HTML):
```html
<h5 class="footer-group-label mb-3">Kontakt</h5>
<p><strong>North Medical Germany</strong></p>
<p>Medzenith GmbH</p>
<p>Mühlenweg 131-139, 22844 Norderstedt</p>
<p><a href="mailto:info@north-medical-germany.com">E-Mail: info@north-medical-germany.com</a></p>
<p><a href="tel:+494021995055">Tel: +49 40 21 99 50 55</a></p>
```

### Copyright:
```
Copyright 2019 - 2025 | North Medical Germany | All Rights Reserved
```

## ✅ Avantajlar

1. **Kod Değişikliği Yok:** Tüm içerikler Website Settings'ten yönetilir
2. **ERPNext Standart:** ERPNext'in temel formları kullanılır
3. **Kolay Yönetim:** Tek yerden tüm yapılandırmalar
4. **Çoklu Proje:** Her projede aynı yapı kullanılabilir

## 🔄 Cache Temizleme

Değişikliklerden sonra:
```
bench --site [site_name] clear-cache
bench --site [site_name] clear-website-cache
```
