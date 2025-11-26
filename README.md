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
- **Stok Durumu** (`/portal/stock`): Bayilerin anlık stok durumlarını görüntüleme
- **Satış Siparişleri** (`/portal/sales-orders`): Bayi satış siparişlerini listeleme ve görüntüleme
- **Faturalar** (`/portal/invoices`): Bayi faturalarını görüntüleme
- **Malzeme Talepleri** (`/portal/material-requests`): Material Request oluşturma ve yönetimi
- **Stok Hareketleri** (`/portal/stock-entries`): Material Receipt/Issue işlemleri

#### API Endpoints
- **Stock API** (`/api/method/north_medical_portal.www.api.stock.get_stock_status`): Stok durumu sorgulama
- **Sales Orders API** (`/api/method/north_medical_portal.www.api.sales_orders.get_sales_orders`): Satış siparişleri listeleme
- **Invoices API** (`/api/method/north_medical_portal.www.api.invoices.get_invoices`): Fatura listeleme
- **Material Request API** (`/api/method/north_medical_portal.www.api.material_request.create_material_request`): Material Request oluşturma
- **Material Request List API** (`/api/method/north_medical_portal.www.api.material_request.get_material_requests`): Material Request listeleme
- **Stock Entry API** (`/api/method/north_medical_portal.www.api.stock_entry.create_stock_entry`): Stock Entry oluşturma (Material Receipt/Issue)
- **Stock Entry List API** (`/api/method/north_medical_portal.www.api.stock_entry.get_stock_entries`): Stock Entry listeleme

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
│   │   ├── sales-orders/        # Satış siparişleri sayfası
│   │   ├── invoices/           # Faturalar sayfası
│   │   ├── material-requests/   # Malzeme talepleri sayfası
│   │   └── stock-entries/       # Stok hareketleri sayfası
│   └── login.py                 # Login context override
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
- **Create Requests**: Create Material Requests from portal
- **View Requests**: List and view all Material Requests
- **Automatic Creation**: Automatic Material Request creation for low stock items
- **Add to Cart**: Add Material Request items directly to webshop cart
- **Status Auto-Update**: Material Request status automatically updates when Sales Order is created from cart
- **Status Progression**: Status changes from "Pending" → "Partially Ordered" → "Ordered" based on ordered quantities

### Sales Order Management
- **View Orders**: List all sales orders for dealer
- **Order Details**: View detailed order information
- **Status Tracking**: Track order status
- **Material Request Integration**: Automatically updates Material Request status when Sales Order is created from Material Request items

### Invoice Management
- **View Invoices**: List all invoices for dealer
- **Invoice Details**: View detailed invoice information
- **Payment Tracking**: Track invoice payment status

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

## 📚 Documentation

- **User Manual**: See ERPNext [documentation](https://docs.erpnext.com)
- **Developer Docs**: Frappe Framework [documentation](https://frappeframework.com/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - See [license.txt](license.txt) file for details.

## 🙏 Credits

Developed for North Medical Germany with:
- Dealer portal system
- Automated stock management
- Product badge system
- Custom field integrations
- Brand-specific styling

---

**Developed with ❤️ for North Medical Germany**
