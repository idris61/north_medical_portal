"""
WooCommerce ürün detay sayfalarından varyant fiyatlarını çekip
ERP'deki Item / UOM / Item Price yapısını buna göre güncelle.

Not:
- Burada amaç, webdeki varyant + miktar bazlı fiyatları mümkün olduğunca
  aynı UOM mantığı ile ERP'ye taşımak.
- Mevcut Item'lar korunur; sadece UOM ve Item Price kayıtları eklenir/güncellenir.
"""

import html
import json
import re
import time
from typing import Dict, List, Optional, Tuple

import frappe
import requests
from bs4 import BeautifulSoup

from .fetch_variant_prices import find_matching_item


def get_all_product_detail_urls(max_page: int = 10) -> List[Tuple[str, str]]:
	"""
	Tüm ürün liste sayfalarını dolaşarak ürün detay URL'lerini topla.

	Returns:
		list[tuple[name, url]]
	"""
	base_url = "https://www.northmedical.de/produkte/"
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
	}

	product_links: List[Tuple[str, str]] = []

	print("\n📡 Ürün detay URL'leri çekiliyor...")

	for page in range(1, max_page + 1):
		if page == 1:
			url = base_url
		else:
			url = f"{base_url}page/{page}/"

		try:
			resp = requests.get(url, timeout=30, headers=headers)
			if resp.status_code != 200:
				break

			soup = BeautifulSoup(resp.content, "html.parser")
			li_products = soup.find_all("li", class_=re.compile(r"product"))
			if not li_products:
				break

			print(f"   📄 Liste sayfası {page}: {len(li_products)} ürün")

			for li in li_products:
				link = li.find("a", href=True)
				title = li.find("h2") or li.find("h3") or li.find("h4")
				if not link or not title:
					continue

				name = title.get_text(strip=True)
				href = link["href"]
				if not href.startswith("http"):
					href = f"https://www.northmedical.de{href}"

				product_links.append((name, href))

			time.sleep(0.3)
		except Exception as e:
			print(f"   ⚠️  Liste sayfası {page} hatası: {e}")
			break

	print(f"\n📦 Toplam {len(product_links)} ürün detay URL'si bulundu")
	return product_links


def parse_variations_from_html(html_content: str) -> List[Dict]:
	"""
	Ürün detay HTML'inden data-product_variations JSON'unu parse et.
	"""
	soup = BeautifulSoup(html_content, "html.parser")
	form = soup.find("form", class_=re.compile(r"variations_form"))
	if not form:
		return []

	data_attr = form.get("data-product_variations")
	if not data_attr:
		return []

	# HTML attribute içindeki JSON'u decode et
	json_text = html.unescape(data_attr)
	try:
		variations = json.loads(json_text)
		return variations if isinstance(variations, list) else []
	except Exception as e:
		print(f"   ⚠️  JSON parse hatası: {e}")
		return []


def guess_uom_from_attribute(attribute_value: str) -> str:
	"""
	WooCommerce attribute slug'ından (örn: '1-karton-24-packungen')
	makul bir UOM ismi çıkar.
	"""
	text = attribute_value.replace("-", " ").lower()

	if "karton" in text:
		return "Carton"
	if "packung" in text or "packungen" in text:
		return "Packung"
	if "stuck" in text or "stück" in text:
		return "Piece"

	# Varsayılan
	return "Pack"


def ensure_uom_exists(uom_name: str) -> None:
	"""UOM yoksa oluştur."""
	if frappe.db.exists("UOM", uom_name):
		return

	uom = frappe.new_doc("UOM")
	uom.uom_name = uom_name
	uom.insert()
	print(f"      ➕ UOM oluşturuldu: {uom_name}")


def ensure_item_uom(item_code: str, uom_name: str) -> None:
	"""
	Item için ilgili UOM'u Item.uoms tablosuna ekle.
	Conversion factor'ı 1 bırakıyoruz; stok UOM'una dokunmuyoruz.
	"""
	item_doc = frappe.get_doc("Item", item_code)

	# Zaten varsa çık
	for row in getattr(item_doc, "uoms", []):
		if row.uom == uom_name:
			return

	# Yoksa ekle
	row = item_doc.append("uoms", {})
	row.uom = uom_name
	row.conversion_factor = 1

	item_doc.save()
	print(f"      ➕ Item UOM eklendi: {item_code} / {uom_name}")


def update_item_prices_for_variations(
	product_name: str,
	variations: List[Dict],
	all_items: List[Dict],
	price_list_name: str = "Standard Selling",
	currency: str = "EUR",
) -> Tuple[int, int]:
	"""
	Verilen ürün için varyant fiyatlarını Item Price'a yaz.

	Returns:
		(matched_count, updated_count)
	"""
	if not variations:
		return 0, 0

	matched_item, score = find_matching_item(product_name, all_items, threshold=0.5)
	if not matched_item or score < 0.5:
		print(f"   ❌ ERP Item bulunamadı: {product_name}")
		return 0, 0

	# Burada fiyatı template seviyesinde tutmak istiyoruz.
	# has_variants olsa bile, tüm bedenler için aynı fiyat politikası kullanıldığı için
	# template item üzerinde UOM bazlı fiyat oluşturmak güvenli.

	matched_count = 0
	updated_count = 0

	for var in variations:
		attrs = var.get("attributes") or {}
		display_price = var.get("display_price")
		if display_price is None:
			continue

		# Şimdilik tek attribute bekliyoruz (pa_varianten)
		attr_val = None
		if attrs:
			attr_val = next(iter(attrs.values()))

		if not attr_val:
			uom_name = "Pack"
		else:
			uom_name = guess_uom_from_attribute(str(attr_val))

		# UOM ve Item UOM kaydını garanti altına al
		ensure_uom_exists(uom_name)
		ensure_item_uom(matched_item.item_code, uom_name)

		# Mevcut fiyatı bul
		existing = frappe.db.get_value(
			"Item Price",
			{
				"item_code": matched_item.item_code,
				"price_list": price_list_name,
				"currency": currency,
				"uom": uom_name,
			},
			["name", "price_list_rate"],
			as_dict=True,
		)

		if existing:
			if abs(float(existing.price_list_rate) - float(display_price)) > 0.01:
				frappe.db.set_value(
					"Item Price",
					existing.name,
					"price_list_rate",
					float(display_price),
				)
				print(
					f"      ✅ {matched_item.item_code} / {uom_name}: "
					f"{existing.price_list_rate}€ → {display_price}€"
				)
				updated_count += 1
			else:
				print(
					f"      ✓  {matched_item.item_code} / {uom_name}: "
					f"{display_price}€ (zaten güncel)"
				)
		else:
			ip = frappe.new_doc("Item Price")
			ip.item_code = matched_item.item_code
			ip.price_list = price_list_name
			ip.currency = currency
			ip.uom = uom_name
			ip.price_list_rate = float(display_price)
			ip.insert()
			print(
				f"      ➕ {matched_item.item_code} / {uom_name}: "
				f"{display_price}€ (yeni, skor: {score:.2f})"
			)
			updated_count += 1

		matched_count += 1

	return matched_count, updated_count


def sync_all_variant_prices():
	"""
	Webdeki varyantlı ürünlerin fiyatlarını ERP'deki UOM bazlı Item Price'lara yaz.

	Bu fonksiyon:
	- Tüm ürün detay URL'lerini toplar
	- Her bir ürün için varyant JSON'unu okur
	- ERP'de karşılık gelen Item'ı bulur
	- Her varyant için uygun UOM'u tahmin eder ve Item Price'ı günceller/oluşturur
	"""
	print("=" * 70)
	print("WOO VARIANT → ERP ITEM UOM FİYAT SİNKRONİZASYONU")
	print("=" * 70)

	price_list_name = "Standard Selling"
	currency = "EUR"

	# Price List kontrol
	if not frappe.db.exists("Price List", price_list_name):
		price_list = frappe.new_doc("Price List")
		price_list.price_list_name = price_list_name
		price_list.currency = currency
		price_list.selling = 1
		price_list.enabled = 1
		price_list.insert()
		print(f"✅ Price List oluşturuldu: {price_list_name}")
	else:
		print(f"✅ Price List mevcut: {price_list_name}")

	# Tüm Item'lar (template + variant)
	all_items = frappe.db.sql(
		"""
        SELECT name, item_code, item_name, has_variants, variant_of
        FROM `tabItem`
        WHERE disabled = 0
    """,
		as_dict=True,
	)

	print(f"\n📦 ERP'de {len(all_items)} aktif Item bulundu\n")

	# Web ürünleri
	products = get_all_product_detail_urls()

	total_variations = 0
	total_matched = 0
	total_updated = 0

	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
	}

	for name, url in products:
		try:
			resp = requests.get(url, timeout=30, headers=headers)
			if resp.status_code != 200:
				print(f"   ⚠️  {name[:50]}... için HTTP {resp.status_code}")
				continue

			variations = parse_variations_from_html(resp.text)
			if not variations:
				continue

			print(f"\n🧩 {name[:80]}...")
			print(f"   🌐 {url}")
			print(f"   🎯 {len(variations)} varyant bulundu")

			matched, updated = update_item_prices_for_variations(
				name, variations, all_items, price_list_name=price_list_name, currency=currency
			)

			total_variations += len(variations)
			total_matched += matched
			total_updated += updated

			# Çok hızlı gitmemek için ufak bekleme
			time.sleep(0.5)
		except Exception as e:
			print(f"   ⚠️  {name[:50]}... hata: {e}")
			continue

	frappe.db.commit()

	print("\n📊 Özet:")
	print(f"   🔢 Toplam varyant: {total_variations}")
	print(f"   ✅ Eşleşen varyant: {total_matched}")
	print(f"   💰 Güncellenen/oluşturulan Item Price: {total_updated}")
	print("\n✅ WooCommerce varyant fiyatları ERP UOM fiyatları ile senkronize edildi.")



def cleanup_legacy_item_prices():
	"""
	Web varyant senkronu sonrasında, kullanılmayacak eski Item Price
	kayıtlarını temizle.

	Strateji:
	- Standard Selling / EUR price list'inde
	- Aynı item için UOM'lu fiyatı varsa
	- UOM'u boş olan (legacy) Item Price kayıtlarını sil.
	"""
	price_list_name = "Standard Selling"
	currency = "EUR"

	print("=" * 70)
	print("LEGACY ITEM PRICE TEMİZLİĞİ")
	print("=" * 70)

	# UOM'lu fiyatı olan item'lar
	items_with_uom = frappe.db.sql(
		"""
        SELECT DISTINCT item_code
        FROM `tabItem Price`
        WHERE price_list = %s
          AND currency = %s
          AND IFNULL(uom, '') != ''
          AND IFNULL(item_code, '') != ''
    """,
		(price_list_name, currency),
		as_dict=True,
	)

	if not items_with_uom:
		print("❌ UOM'lu fiyatı olan item bulunamadı, temizlenecek kayıt yok.")
		return

	item_codes = [row.item_code for row in items_with_uom]

	# Silinecek legacy kayıtlar (uom boş)
	# pymysql parametre format problemi yaşamamak için IN kısmını manuel oluşturuyoruz
	placeholders = ", ".join(["%s"] * len(item_codes))
	query = f"""
        SELECT name, item_code, price_list_rate
        FROM `tabItem Price`
        WHERE price_list = %s
          AND currency = %s
          AND IFNULL(uom, '') = ''
          AND item_code IN ({placeholders})
    """

	values = [price_list_name, currency] + item_codes
	legacy_prices = frappe.db.sql(query, values=values, as_dict=True)

	if not legacy_prices:
		print("✅ Legacy Item Price kaydı bulunamadı.")
		return

	print(f"\n🧹 Silinecek legacy fiyat sayısı: {len(legacy_prices)}")

	for row in legacy_prices:
		print(f"   - {row.item_code}: {row.price_list_rate}€ (name={row.name}) siliniyor")
		frappe.delete_doc("Item Price", row.name, force=1)

	frappe.db.commit()

	print("\n✅ Legacy Item Price kayıtları temizlendi.")


