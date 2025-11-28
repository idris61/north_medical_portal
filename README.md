# North Medical Portal

North Medical Germany'ye özel dealer portal sistemi - Stok takibi, malzeme talepleri, satış siparişleri ve stok hareketleri yönetimi.

## 🏗️ Mimari Prensip

- **Webshop App**: Genel e-ticaret özellikleri (cart, wishlist, order, ürün sayfaları, dil seçici) - Tüm projelerde ortak kullanılır
- **North Medical Portal**: Sadece North Medical'e özel geliştirmeler (dealer portal, brand styling, stok otomasyonu, product badges, custom fields)

## 🚀 Özellikler

### 🎨 Website Yapılandırması
- **Navbar Styling**: North Medical brand renklerine özel navbar (beyaz arka plan, turkuaz alt çizgi, koyu mavi menü)
- **Footer Styling**: Brand renklerine özel footer tasarımı
- **Back to Top Button**: Sayfa scroll için buton
- **Portal Navigation**: Dealer portal sayfalarına özel navigasyon linkleri
- Yapılandırma: `north_medical_portal/utils/website.py`

### 📦 Dealer Portal Sistemi

#### Portal Sayfaları
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

#### API Endpoints
- **Stock API** (`/api/method/north_medical_portal.www.api.stock.get_stock_status`): Stok durumu sorgulama
- **Stock API - Item Search** (`/api/method/north_medical_portal.www.api.stock.search_items_for_portal`): Ürün arama (autocomplete)
- **Stock API - Item Stock Info** (`/api/method/north_medical_portal.www.api.stock.get_item_stock_info`): Ürün stok bilgisi
- **Stock API - Update Reorder Levels** (`/api/method/north_medical_portal.www.api.stock.update_reorder_levels`): Reorder level güncelleme
- **Stock API - Trigger Reorder Check** (`/api/method/north_medical_portal.www.api.stock.trigger_reorder_check`): Manuel reorder kontrolü
- **Sales Orders API** (`/api/method/north_medical_portal.www.api.sales_orders.get_sales_orders`): Satış siparişleri listeleme
- **Invoices API** (`/api/method/north_medical_portal.www.api.invoices.get_invoices`): Fatura listeleme
- **Material Request API** (`/api/method/north_medical_portal.www.api.material_request.create_material_request`): Material Request oluşturma
- **Material Request List API** (`/api/method/north_medical_portal.www.api.material_request.get_material_requests`): Material Request listeleme
- **Material Request - Add to Cart** (`/api/method/north_medical_portal.www.api.material_request.add_material_request_to_cart`): Material Request'i sepete ekleme
- **Stock Entry API** (`/api/method/north_medical_portal.www.api.stock_entry.create_stock_entry`): Stock Entry oluşturma (Material Issue)
- **Stock Entry List API** (`/api/method/north_medical_portal.www.api.stock_entry.get_stock_entries`): Stock Entry listeleme
- **Stock Entry - Get** (`/api/method/north_medical_portal.www.api.stock_entry.get_stock_entry`): Stock Entry detay
- **Stock Entry - Update** (`/api/method/north_medical_portal.www.api.stock_entry.update_stock_entry`): Stock Entry güncelleme
- **Stock Entry - Cancel** (`/api/method/north_medical_portal.www.api.stock_entry.cancel_stock_entry`): Stock Entry iptal etme
- **Stock Entry - Delete** (`/api/method/north_medical_portal.www.api.stock_entry.delete_stock_entry`): Stock Entry silme
- **Stock Entry - Amend** (`/api/method/north_medical_portal.www.api.stock_entry.amend_stock_entry`): İptal edilmiş Stock Entry'i düzenleme için taslak yapma

#### Security & Permissions
- **Dealer Access Validation**: `validate_dealer_access()` - Kullanıcının bayi erişim yetkisini kontrol eder
- **Company-based Access**: Her bayi sadece kendi şirket verilerine erişebilir
- **User Company Detection**: `get_user_company()` - Kullanıcının bağlı olduğu şirketi otomatik bulur
- **Warehouse Filtering**: `get_company_warehouses()` - Şirkete özel warehouse listesi

### 🔄 Otomatik Stok Yönetimi

#### Delivery Note Otomasyonu
- **Otomatik Stok Transferi**: Delivery Note submit edildiğinde müşterinin deposuna otomatik stok transferi
- **Stock Entry Oluşturma**: Material Transfer tipinde Stock Entry otomatik oluşturulur
- **Valuation Rate**: Son valuation rate kullanılarak transfer edilir
- **Error Handling**: Hata durumunda log tutulur, Delivery Note submit işlemi engellenmez
- Yapılandırma: `north_medical_portal/utils/delivery_note.py`

#### Reorder Level Kontrolü
- **Günlük Scheduler**: Her gün otomatik reorder level kontrolü
- **Otomatik Material Request**: Reorder level altına düşen ürünler için Material Request oluşturma
- **Company-based Processing**: Her şirket için ayrı kontrol
- Yapılandırma: `north_medical_portal/utils/stock.py`

#### Material Request Durum Güncelleme
- **Otomatik Durum Güncelleme**: Sales Order oluşturulduğunda Material Request durumu otomatik güncellenir
- **Ordered Qty Tracking**: Material Request'ten sepete eklenen ürünler için `ordered_qty` takibi
- **Status Progression**: Material Request durumu otomatik olarak güncellenir (Pending → Partially Ordered → Ordered)
- **Purchase Type Support**: Sadece "Purchase" tipindeki Material Request'ler için çalışır
- Yapılandırma: `north_medical_portal/utils/sales_order.py`

### 🏷️ Product Badges
- **Badge Sistemi**: Ürün badge sistemi (Item ve Website Item'da)
- **Badge Görseli**: Badge görseli, link ve sıralama desteği
- **Product Badge DocType**: Özel DocType ile badge yönetimi
- Yapılandırma: `north_medical_portal/portal/doctype/product_badge/`

### 📝 Custom Fields
- **Item DocType**:
  - `short_description` (Text Editor): Kısa ürün açıklaması
  - `product_badges` (Table): Ürün badge'leri
- **Website Item DocType**:
  - `product_badges` (Table): Ürün badge'leri

### 🔧 Helper Functions
- **get_user_company()**: Kullanıcının bağlı olduğu şirketi bulur
- **get_company_warehouses()**: Şirketin warehouse'larını döndürür
- **validate_dealer_access()**: Dealer erişim yetkisini kontrol eder

## 📁 Yapı

```
north_medical_portal/
├── hooks.py                      # Hook tanımları (scheduler, website context, doc events)
├── utils/
│   ├── website.py               # Website yapılandırması (CSS, styling) - ÖZEL
│   ├── stock.py                  # Stok kontrolü ve Material Request - ÖZEL
│   ├── delivery_note.py          # Delivery Note otomasyonu - ÖZEL
│   ├── sales_order.py            # Sales Order Material Request güncelleme - ÖZEL
│   ├── helpers.py               # Ortak helper fonksiyonlar
│   └── bulk_pricing_and_stock.py # Toplu fiyat ve stok ayarları
├── www/
│   ├── api/                     # API endpoint'leri - ÖZEL
│   │   ├── stock.py             # Stok durumu API
│   │   ├── sales_orders.py       # Satış siparişleri API
│   │   ├── invoices.py          # Faturalar API
│   │   ├── material_request.py  # Material Request API
│   │   └── stock_entry.py       # Stock Entry API
│   ├── portal/                  # Portal sayfaları - ÖZEL
│   │   ├── stock/               # Stok durumu sayfası
│   │   ├── stock-summary-print/ # Stok özeti print sayfası
│   │   ├── sales-orders/        # Satış siparişleri sayfası
│   │   ├── invoices/           # Faturalar sayfası
│   │   ├── material-requests/   # Malzeme talepleri sayfası
│   │   ├── material-request-detail/ # Malzeme talebi detay sayfası
│   │   ├── material-issue/      # Malzeme çıkışı sayfaları
│   │   │   ├── index.html      # Malzeme çıkışı listesi
│   │   │   ├── index.py        # List context
│   │   │   ├── new.html        # Yeni oluşturma formu
│   │   │   ├── new.py          # Form context
│   │   │   ├── edit.html       # Düzenleme formu
│   │   │   └── edit.py         # Edit context
│   │   ├── stock-entry/         # Stock Entry detay sayfası
│   │   └── stock-entries/       # Stok hareketleri sayfası
│   ├── printview.html          # Print preview override (dil seçimi)
│   ├── printview.py            # Print preview context override
│   └── login.py                 # Login context override
├── templates/
│   └── pages/
│       └── order.html          # Order detail page override
├── translations/                # Çeviri dosyaları - ÖZEL
│   ├── tr.csv                  # Türkçe çeviriler
│   ├── en.csv                  # İngilizce çeviriler
│   ├── de.csv                  # Almanca çeviriler
│   ├── fr.csv                  # Fransızca çeviriler
│   └── it.csv                  # İtalyanca çeviriler
├── dealer_portal/
│   └── doctype/
│       └── dealer_settings/     # Dealer Settings DocType
├── portal/
│   └── doctype/
│       └── product_badge/        # Product Badge DocType - ÖZEL
├── templates/                    # Footer extensions - ÖZEL
└── fixtures/
    └── custom_field.json         # Custom field'lar - ÖZEL
```

## 🛠️ Technical Stack

- **Backend**: Python 3, Frappe Framework v15, ERPNext
- **Frontend**: JavaScript ES6+, jQuery, Bootstrap 4
- **Database**: MariaDB
- **Styling**: SCSS, Bootstrap 4

## 📦 Installation

### Prerequisites
- Frappe Bench
- ERPNext v15
- Webshop App (required dependency)

### Steps

1. **Get the app**
   ```bash
   cd /path/to/frappe-bench
   bench get-app https://github.com/idris61/north_medical_portal.git
   ```

2. **Install on site**
   ```bash
   bench --site your-site.local install-app north_medical_portal
   ```

3. **Build assets**
   ```bash
   bench build --app north_medical_portal
   ```

4. **Clear cache**
   ```bash
   bench --site your-site.local clear-cache
   bench --site your-site.local clear-website-cache
   ```

## ⚙️ Configuration

### Dealer Settings
Navigate to: **Dealer Settings** to configure:
- Source warehouse for stock transfers
- Default settings for dealer operations

### User Company Setup
- Users must have `company` field set to their dealer company
- Or role-based company detection (e.g., "Dealer Manager - Bayi 1")

### Warehouse Setup
- Each dealer company must have warehouses configured
- Warehouse names should follow naming convention (e.g., "Bayi-1 - NM")

## 🔐 Security

### Access Control
- All portal pages and APIs validate dealer access
- Users can only access data from their own company
- Guest users are blocked from portal pages

### Permission Validation
- `validate_dealer_access()` checks user permissions
- Company-based data filtering
- Warehouse filtering by company

## 📊 Features Detail

### Stock Management
- **Real-time Stock Status**: View current stock levels for all items
- **Reorder Level Monitoring**: Automatic reorder level checks
- **Stock Transfers**: Automatic stock transfers on Delivery Note submission
- **Stock Entries**: Create Material Receipt/Issue entries

### Material Request Management
- **View Requests**: List and view all Material Requests
- **Automatic Creation**: Automatic Material Request creation for low stock items (scheduled daily at midnight)
- **Manual Trigger**: Manual reorder level check button on Stock Status page
- **Add to Cart**: Add Material Request items directly to webshop cart
- **Status Auto-Update**: Material Request status automatically updates when Sales Order is created from cart
- **Status Progression**: Status changes from "Draft" → "Pending" → "Partially Ordered" → "Ordered" based on ordered quantities
- **Auto-Submit**: Material Requests are automatically submitted when items are ordered from cart
- **Print Format**: Custom print format with translations (Material Request Portal)

### Sales Order Management
- **View Orders**: List all sales orders for dealer
- **Order Details**: View detailed order information
- **Status Tracking**: Track order status
- **Material Request Integration**: Automatically updates Material Request status when Sales Order is created from Material Request items
- **Print Format**: Custom print format with translations (Sales Order Portal)
- **No Payment Button**: Payment button removed from Sales Order detail page (orders are pre-paid)
- **Actions Menu**: Simplified to only show Print button

### Invoice Management
- **View Invoices**: List all invoices for dealer
- **Invoice Details**: View detailed invoice information
- **Payment Tracking**: Track invoice payment status
- **Print Format**: Custom print format with translations (Sales Invoice Portal)

### Material Issue (Stock Entry) Management
- **Create Material Issue**: Create new Material Issue (Stock Entry) from portal
- **Edit Material Issue**: Edit existing Material Issue documents
- **List Material Issues**: View all Material Issue documents
- **View Details**: View detailed Material Issue information
- **Cancel**: Cancel submitted Material Issue documents
- **Delete**: Delete cancelled Material Issue documents
- **Amend**: Revert cancelled Material Issue to Draft status for editing
- **Auto-Submit**: Material Issues are automatically submitted after editing
- **Warehouse Auto-Selection**: Warehouse automatically selected based on user permissions
- **Item Autocomplete**: Dynamic item search with autocomplete functionality
- **Stock Display**: Real-time stock quantity display when item is selected
- **Row Management**: Add/delete item rows with checkboxes
- **Print Format**: Custom print format with translations (Stock Entry Portal)

### Print Formats
- **Sales Order Portal**: Custom print format for Sales Orders with translations
- **Sales Invoice Portal**: Custom print format for Sales Invoices with translations
- **Delivery Note Portal**: Custom print format for Delivery Notes with translations
- **Material Request Portal**: Custom print format for Material Requests with translations
- **Stock Entry Portal**: Custom print format for Stock Entries (Material Issue) with translations
- **Stock Summary Print**: Custom print page for stock summary with translations
- **Language Selection**: Language dropdown in print preview (TR, EN, DE, FR, IT)
- **Consistent Design**: All print formats follow the same clean, professional design

### Internationalization (i18n)
- **5 Languages Supported**: Turkish (TR), English (EN), German (DE), French (FR), Italian (IT)
- **Translation Files**: All translations in CSV format (`translations/tr.csv`, `en.csv`, `de.csv`, `fr.csv`, `it.csv`)
- **Complete Coverage**: All buttons, fields, labels, filters, and messages translated
- **Product Page Translations**: All product listing page elements translated (filters, search, sort, show)
- **Button Translations**: All action buttons translated (Add to Cart, View in Cart, Past Orders, Continue Shopping, Order, Change, Explore)
- **Dynamic Translations**: Translations load dynamically based on user's language selection

## 🧪 Testing

Run tests:
```bash
bench --site your-site.local run-tests --app north_medical_portal
```

Clear cache for testing:
```bash
bench --site your-site.local clear-cache
bench --site your-site.local clear-website-cache
```

## 🔧 Development Guidelines

### Code Style
- All comments in English
- Turkish translations in translation files only
- Clean code principles: DRY, Single Responsibility
- Meaningful function and variable names

### API Development
- All APIs use `@frappe.whitelist()` decorator
- Permission validation required for all APIs
- Company-based data filtering
- Error handling with proper error messages

### Portal Page Development
- Use `validate_dealer_access()` for permission check
- Use `get_user_company()` for company detection
- Use `get_company_warehouses()` for warehouse filtering
- Set `context.no_cache = 1` for dynamic pages
- Wrap all user-facing strings with `_()` for translation
- Use `frappe._()` in JavaScript for client-side translations

### Translation Development
- All translations in CSV format in `translations/` directory
- Source text in English, translations in target language
- Use `_()` function in Python templates for server-side translations
- Use `__()` function in JavaScript for client-side translations
- After adding translations, run `bench build` and clear cache
- Translations are loaded from `frappe._messages` object in JavaScript

## 🌐 Language Support

### Supported Languages
- **Turkish (TR)**: Tam destek
- **English (EN)**: Full support
- **German (DE)**: Vollständige Unterstützung
- **French (FR)**: Support complet
- **Italian (IT)**: Supporto completo

### Translation Coverage
- ✅ All portal pages (Stock, Orders, Invoices, Material Requests, Material Issue)
- ✅ All print formats (Sales Order, Sales Invoice, Delivery Note, Material Request, Stock Entry, Stock Summary)
- ✅ All buttons and action labels
- ✅ All form fields and labels
- ✅ All filter options and labels
- ✅ All product page elements (search, sort, show, filters)
- ✅ All error and success messages

### Adding New Translations
1. Add translation to CSV files in `translations/` directory
2. Format: `Source Text,Translated Text,`
3. Run `bench build` to compile translations
4. Clear cache: `bench --site all clear-cache`
5. Restart server: `bench restart`

## 📚 Documentation

- **User Manual**: See ERPNext [documentation](https://docs.erpnext.com)
- **Developer Docs**: Frappe Framework [documentation](https://frappeframework.com/docs)
- **Print Format Guide**: Custom print formats located in ERPNext app under `erpnext/*/print_format/*_portal/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - See [license.txt](license.txt) file for details.

## 🎯 Key Features Summary

### Material Issue Form
- ERPNext-like professional form design
- Automatic warehouse selection based on user permissions
- Dynamic item search with autocomplete
- Real-time stock quantity display
- Add/delete item rows with checkboxes
- Quantity validation (whole numbers only)
- Auto-submit after editing

### Print Formats
- Consistent design across all document types
- Language selection dropdown (5 languages)
- Clean, professional layout
- No unnecessary colors or decorations
- Proper alignment and spacing

### Material Request Integration
- Add Material Request items to cart
- Automatic status updates when orders are placed
- Status progression: Draft → Pending → Partially Ordered → Ordered
- Auto-submit when items are ordered

### Stock Management
- Real-time stock status display
- Reorder level editing
- Manual reorder check trigger
- Automatic Material Request creation for low stock items
- Stock summary print page

## 🙏 Credits

Developed for North Medical Germany with:
- Dealer portal system
- Automated stock management
- Material Issue (Stock Entry) management
- Product badge system
- Custom field integrations
- Brand-specific styling
- Multi-language support (5 languages)
- Custom print formats
- Professional UI/UX design

---

**Developed with ❤️ for North Medical Germany**
