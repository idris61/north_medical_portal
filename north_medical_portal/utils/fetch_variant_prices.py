"""
Web sitesinden TÜM ürün ve varyant fiyatlarını çekip güncelleme scripti
"""
import re
import time
from difflib import SequenceMatcher

import frappe
import requests
from bs4 import BeautifulSoup


def similarity(a, b):
	"""İki string arasındaki benzerlik skorunu döndür."""
	return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def extract_price_from_text(text):
	"""Metin içinden fiyatı (float) olarak çıkar."""
	if not text:
		return None

	price_match = re.search(r"(\d+[.,]\d+)\s*€", text)
	if price_match:
		return float(price_match.group(1).replace(",", "."))

	price_match = re.search(r"(\d+[.,]\d+)", text)
	if price_match:
		return float(price_match.group(1).replace(",", "."))

	return None


def find_matching_item(product_name, all_items, threshold=0.5):
	"""Web ürün adını ERP Item ile eşleştir."""
	best_match = None
	best_score = 0

	# 1) Tam eşleşme
	for item in all_items:
		if item.item_name.strip().lower() == product_name.strip().lower():
			return item, 1.0

	# 2) İlk 4 kelime eşleşmesi
	product_words = product_name.lower().split()[:4]
	for item in all_items:
		item_words = item.item_name.lower().split()[:4]
		if product_words == item_words:
			return item, 0.9

	# 3) Fuzzy match
	for item in all_items:
		score = similarity(product_name, item.item_name)
		if score > best_score and score >= threshold:
			best_score = score
			best_match = item

	return best_match, best_score


def get_all_products_with_variants():
	"""Web sitesinden TÜM ürünleri çek (varyant fiyatları dahil, ham liste)."""
	base_url = "https://www.northmedical.de/produkte/"
	all_products = []
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
	}

	print("\n📡 Web sitesinden tüm ürünler çekiliyor (varyantlar dahil)...")

	max_page = 10
	page = 1

	while page <= max_page:
		if page == 1:
			url = base_url
		else:
			url = f"{base_url}page/{page}/"

		try:
			response = requests.get(url, timeout=30, headers=headers)
			if response.status_code != 200:
				break

			soup = BeautifulSoup(response.content, "html.parser")
			wc_products = soup.find_all("li", class_=re.compile(r"product"))

			if len(wc_products) == 0:
				break

			print(f"   📄 Sayfa {page}: {len(wc_products)} ürün bulundu")

			for product_elem in wc_products:
				# Ürün adı
				title_elem = product_elem.find(
					"h2", class_=re.compile(r"woocommerce-loop-product__title")
				)
				if not title_elem:
					link_elem = product_elem.find(
						"a", class_=re.compile(r"woocommerce-LoopProduct-link")
					)
					if link_elem:
						title_elem = link_elem.find("h2")
				if not title_elem:
					title_elem = product_elem.find(["h2", "h3", "h4"])

				if title_elem:
					product_name = title_elem.get_text(strip=True)
				else:
					continue

				if not product_name or len(product_name) < 5:
					continue

				# Fiyat - varyant fiyatları da kontrol et
				prices = []

				# Ana fiyat
				price_elem = product_elem.find(
					"span", class_=re.compile(r"price|amount|woocommerce-Price-amount")
				)
				if not price_elem:
					price_elem = product_elem.find("bdi", class_=re.compile(r"amount"))

				if price_elem:
					price_text = price_elem.get_text(strip=True)
					# Fiyat aralığı kontrolü (örn: "1.35€ – 30.90€")
					if "–" in price_text or "-" in price_text:
						price_parts = re.findall(r"(\d+[.,]\d+)", price_text)
						for part in price_parts:
							price = float(part.replace(",", "."))
							if price > 0:
								prices.append(price)
					else:
						price = extract_price_from_text(price_text)
						if price:
							prices.append(price)

				# Eğer fiyat bulunamadıysa, tüm span'leri kontrol et
				if not prices:
					all_spans = product_elem.find_all("span")
					for span in all_spans:
						span_text = span.get_text(strip=True)
						if "€" in span_text:
							if "–" in span_text or "-" in span_text:
								price_parts = re.findall(r"(\d+[.,]\d+)", span_text)
								for part in price_parts:
									price = float(part.replace(",", "."))
									if price > 0:
										prices.append(price)
							else:
								price = extract_price_from_text(span_text)
								if price:
									prices.append(price)

				if prices:
					# Her fiyat için ayrı kayıt oluştur
					for price in prices:
						if not any(
							p["name"] == product_name
							and abs(p["price"] - price) < 0.01
							for p in all_products
						):
							all_products.append({"name": product_name, "price": price})
					price_str = ", ".join([f"{p}€" for p in prices])
					print(f"      ✅ {product_name[:50]}... → {price_str}")

			page += 1
			time.sleep(0.5)

		except Exception as e:
			print(f"   ⚠️  Sayfa {page} hatası: {str(e)}")
			break

	return all_products


def aggregate_products_use_min_price(products):
	"""
	Aynı ürün adı için birden fazla fiyat varsa
	(en küçük fiyatı kullan, diğerlerini logla).
	"""
	if not products:
		return []

	by_name = {}
	for p in products:
		name = p["name"]
		price = p["price"]
		if name not in by_name:
			by_name[name] = {"name": name, "prices": [price]}
		else:
			if price not in by_name[name]["prices"]:
				by_name[name]["prices"].append(price)

	aggregated = []
	print("\n🔍 Varyantlı ürünlerin fiyatları inceleniyor...")
	for name, info in by_name.items():
		prices = sorted(info["prices"])
		if len(prices) > 1:
			price_str = ", ".join([f"{p}€" for p in prices])
			print(f"   • {name[:60]}... → {price_str} (min seçilecek)")
		min_price = prices[0]
		aggregated.append({"name": name, "price": min_price})

	print(f"\n📦 Toplam {len(aggregated)} benzersiz ürün (min fiyat ile) kullanılacak")
	return aggregated


def update_all_prices_with_variants():
	"""Tüm ürün ve varyant fiyatlarını güncelle."""
	print("=" * 70)
	print("WEB'DEN TÜM ÜRÜN VE VARYANT FİYATLARINI ÇEKME")
	print("=" * 70)

	# Web'den TÜM ürünleri çek
	raw_products = get_all_products_with_variants()
	print(f"\n📦 Toplam {len(raw_products)} ürün/varyant fiyatı bulundu")

	# Varyantlı ürünlerde min fiyatı kullanarak tekilleştir
	products = aggregate_products_use_min_price(raw_products)

	if not products:
		print("❌ Hiç ürün bulunamadı!")
		return

	# Price List'i bul veya oluştur
	price_list_name = "Standard Selling"
	if not frappe.db.exists("Price List", price_list_name):
		price_list = frappe.new_doc("Price List")
		price_list.price_list_name = price_list_name
		price_list.currency = "EUR"
		price_list.selling = 1
		price_list.enabled = 1
		price_list.insert()
		print(f"✅ Price List oluşturuldu: {price_list_name}")
	else:
		print(f"✅ Price List mevcut: {price_list_name}")

	currency = "EUR"

	# Tüm item'ları al (template ve variant'lar dahil)
	all_items = frappe.db.sql(
		"""
        SELECT name, item_code, item_name, has_variants, variant_of
        FROM `tabItem`
        WHERE disabled = 0
    """,
		as_dict=True,
	)

	print(f"\n📦 {len(all_items)} item ile eşleştiriliyor...\n")

	matched_count = 0
	updated_count = 0
	not_found = []

	for product in products:
		product_name = product["name"]
		price = product["price"]

		# Item'ı bul (variant'lar dahil, template'ler hariç)
		matched_item, score = find_matching_item(
			product_name, all_items, threshold=0.5
		)

		if matched_item and score >= 0.5:
			# Template item kontrolü
			if matched_item.get("has_variants"):
				print(f"⚠️  {matched_item.item_code}: Template item, atlanıyor")
				continue

			matched_count += 1

			# Mevcut fiyatı kontrol et
			existing_price = frappe.db.get_value(
				"Item Price",
				{
					"item_code": matched_item.item_code,
					"price_list": price_list_name,
					"currency": currency,
				},
				"price_list_rate",
			)

			if existing_price:
				# Fiyat farklıysa güncelle
				if abs(existing_price - price) > 0.01:
					frappe.db.set_value(
						"Item Price",
						{
							"item_code": matched_item.item_code,
							"price_list": price_list_name,
							"currency": currency,
						},
						"price_list_rate",
						price,
					)
					print(
						f"✅ {matched_item.item_code}: {existing_price}€ → {price}€ (skor: {score:.2f})"
					)
				else:
					print(f"✓  {matched_item.item_code}: {price}€ (zaten güncel)")
			else:
				# Yeni fiyat ekle
				item_price = frappe.new_doc("Item Price")
				item_price.item_code = matched_item.item_code
				item_price.price_list = price_list_name
				item_price.currency = currency
				item_price.price_list_rate = price
				item_price.insert()
				print(
					f"➕ {matched_item.item_code}: {price}€ (yeni, skor: {score:.2f})"
				)

			updated_count += 1

			# Her 10 item'da bir commit
			if updated_count % 10 == 0:
				frappe.db.commit()
		else:
			not_found.append({"name": product_name, "price": price})

	frappe.db.commit()

	print("\n📊 Özet:")
	print(f"   ✅ Eşleşen: {matched_count}")
	print(f"   💰 Güncellenen: {updated_count}")
	print(f"   ❌ Bulunamayan: {len(not_found)}")

	if not_found:
		print("\n⚠️  Bulunamayan ürünler (ilk 10):")
		for item in not_found[:10]:
			print(f"   - {item['name'][:60]}... ({item['price']}€)")

	# Variant'ların fiyat durumunu kontrol et
	variants_without_price = frappe.db.sql(
		"""
        SELECT i.item_code, i.item_name
        FROM `tabItem` i
        LEFT JOIN `tabItem Price` ip ON ip.item_code = i.name 
            AND ip.price_list = %s 
            AND ip.currency = %s
        WHERE i.disabled = 0
        AND i.variant_of IS NOT NULL
        AND ip.name IS NULL
        LIMIT 10
    """,
		(price_list_name, currency),
		as_dict=True,
	)

	if variants_without_price:
		print("\n⚠️  Fiyatı olmayan variant'lar (ilk 10):")
		for item in variants_without_price:
			print(f"   - {item.item_code}: {item.item_name[:50]}...")

	print("\n✅ İşlem tamamlandı!")



