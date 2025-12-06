"""
Web sitesinden (https://www.northmedical.de/produkte/) gerçek fiyatları çekip
ERPNext'teki Standard Selling price listesindeki fiyatları güncelle.

Kullanım:
    bench --site north_medical.local execute "north_medical_portal.utils.sync_prices_from_website.sync_all_prices_from_website"
"""

import re
import time
from difflib import SequenceMatcher

import frappe
import requests
from bs4 import BeautifulSoup

from .fetch_variant_prices import extract_price_from_text, find_matching_item


def similarity(a, b):
	"""İki string arasındaki benzerlik skorunu döndür."""
	return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def get_products_from_website(max_pages=20):
	"""
	Web sitesinden tüm ürün listesini ve fiyatlarını çek.
	
	Returns:
		list[dict]: Her dict {"name": str, "price": float, "price_range": tuple}
	"""
	base_url = "https://www.northmedical.de/produkte/"
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
	}
	
	products = []
	
	print(f"\n📡 Web sitesinden ürün listesi çekiliyor (max {max_pages} sayfa)...")
	
	for page in range(1, max_pages + 1):
		if page == 1:
			url = base_url
		else:
			url = f"{base_url}page/{page}/"
		
		try:
			response = requests.get(url, timeout=30, headers=headers)
			if response.status_code != 200:
				print(f"   ⚠️  Sayfa {page}: HTTP {response.status_code}")
				break
			
			soup = BeautifulSoup(response.content, "html.parser")
			
			# Ürün elementlerini bul
			product_elements = soup.find_all("li", class_=re.compile(r"product"))
			
			if not product_elements:
				print(f"   ✅ Sayfa {page}: Ürün bulunamadı, son sayfa.")
				break
			
			print(f"   📄 Sayfa {page}: {len(product_elements)} ürün bulundu")
			
			for product_elem in product_elements:
				# Ürün adı
				title_elem = product_elem.find("h2", class_=re.compile(r"woocommerce-loop-product__title"))
				if not title_elem:
					link_elem = product_elem.find("a", class_=re.compile(r"woocommerce-LoopProduct-link"))
					if link_elem:
						title_elem = link_elem.find("h2") or link_elem.find("h3")
				if not title_elem:
					title_elem = product_elem.find(["h2", "h3", "h4"])
				
				if not title_elem:
					continue
				
				product_name = title_elem.get_text(strip=True)
				if not product_name or len(product_name) < 5:
					continue
				
				# Fiyat
				price = None
				price_min = None
				price_max = None
				
				# Ana fiyat elementi
				price_elem = product_elem.find("span", class_=re.compile(r"price|amount|woocommerce-Price-amount"))
				if not price_elem:
					price_elem = product_elem.find("bdi", class_=re.compile(r"amount"))
				if not price_elem:
					price_elem = product_elem.find("ins", class_=re.compile(r"price"))
				
				if price_elem:
					price_text = price_elem.get_text(strip=True)
					
					# Fiyat aralığı kontrolü (örn: "1.35€ – 30.90€" veya "5.20€ – 52.00€")
					if "–" in price_text or "-" in price_text:
						price_parts = re.findall(r"(\d+[.,]\d+)", price_text)
						if len(price_parts) >= 2:
							price_min = float(price_parts[0].replace(",", "."))
							price_max = float(price_parts[-1].replace(",", "."))
							# Aralık varsa en düşük fiyatı kullan (müşteriye daha uygun)
							price = price_min
						elif len(price_parts) == 1:
							price = float(price_parts[0].replace(",", "."))
					else:
						price = extract_price_from_text(price_text)
				
				# Eğer hala fiyat bulunamadıysa, tüm fiyat içeren span'leri kontrol et
				if not price:
					all_price_elems = product_elem.find_all(text=re.compile(r"\d+[.,]\d+\s*€"))
					for elem_text in all_price_elems:
						extracted = extract_price_from_text(elem_text)
						if extracted:
							price = extracted
							break
				
				if price:
					products.append({
						"name": product_name,
						"price": price,
						"price_min": price_min,
						"price_max": price_max
					})
			
			time.sleep(0.5)  # Rate limiting
			
		except Exception as e:
			print(f"   ❌ Sayfa {page} hatası: {e}")
			frappe.log_error(f"Web scraping error on page {page}: {str(e)}", "Price Sync Error")
			break
	
	print(f"\n✅ Toplam {len(products)} ürün fiyatı çekildi")
	return products


@frappe.whitelist()
def sync_all_prices_from_website(price_list="Standard Selling", max_pages=20, similarity_threshold=0.6):
	"""
	Web sitesinden tüm fiyatları çekip ERPNext'teki fiyatları güncelle.
	
	Args:
		price_list: Güncellenecek fiyat listesi (default: "Standard Selling")
		max_pages: Çekilecek maksimum sayfa sayısı
		similarity_threshold: Ürün eşleştirme için minimum benzerlik skoru (0.0-1.0)
	"""
	
	print(f"\n🚀 Fiyat senkronizasyonu başlatılıyor...")
	print(f"   📋 Fiyat Listesi: {price_list}")
	print(f"   📄 Maksimum Sayfa: {max_pages}")
	print(f"   🎯 Benzerlik Eşiği: {similarity_threshold}")
	
	# Web sitesinden ürünleri çek
	web_products = get_products_from_website(max_pages=max_pages)
	
	if not web_products:
		print("\n❌ Web sitesinden ürün çekilemedi!")
		return {
			"status": "error",
			"message": "Web sitesinden ürün çekilemedi"
		}
	
	# ERPNext'teki tüm aktif stok ürünlerini al (template item'lar hariç - onların variant'larına fiyat eklenir)
	erp_items = frappe.get_all(
		"Item",
		filters={"disabled": 0, "is_stock_item": 1, "has_variants": 0},
		fields=["name", "item_code", "item_name", "stock_uom", "variant_of"],
		order_by="item_name asc"
	)
	
	print(f"\n📦 ERPNext'te {len(erp_items)} aktif stok ürünü bulundu")
	
	# Price list kontrolü
	if not frappe.db.exists("Price List", price_list):
		return {
			"status": "error",
			"message": f"Price List '{price_list}' bulunamadı!"
		}
	
	price_list_doc = frappe.get_doc("Price List", price_list)
	currency = price_list_doc.currency
	
	print(f"   💰 Para Birimi: {currency}\n")
	
	# İstatistikler
	stats = {
		"total_web_products": len(web_products),
		"matched": 0,
		"updated": 0,
		"created": 0,
		"skipped": 0,
		"not_found": 0
	}
	
	# Her web ürünü için ERP'de eşleştirme yap ve fiyat güncelle
	for web_prod in web_products:
		web_name = web_prod["name"]
		web_price = web_prod["price"]
		
		# ERP'de eşleşen ürünü bul
		matched_item, match_score = find_matching_item(web_name, erp_items, threshold=similarity_threshold)
		
		if not matched_item:
			stats["not_found"] += 1
			continue
		
		if match_score < similarity_threshold:
			stats["skipped"] += 1
			continue
		
		item_code = matched_item.item_code
		item_name = matched_item.item_name
		
		# Template item'ları atla (has_variants=1 olanlar template'tir, fiyat eklenemez)
		if matched_item.get("has_variants"):
			stats["skipped"] += 1
			continue
		
		stats["matched"] += 1
		
		# Mevcut Item Price kayıtlarını kontrol et (tüm UOM'lar)
		existing_prices = frappe.get_all(
			"Item Price",
			filters={
				"item_code": item_code,
				"price_list": price_list
			},
			fields=["name", "price_list_rate", "uom"],
			order_by="uom asc"
		)
		
		# Önce stock_uom için fiyat güncelle/oluştur
		target_uom = matched_item.stock_uom
		found_stock_uom_price = None
		
		for ep in existing_prices:
			if ep.uom == target_uom:
				found_stock_uom_price = ep
				break
		
		if found_stock_uom_price:
			# Güncelle
			if abs(found_stock_uom_price.price_list_rate - web_price) > 0.01:  # Fiyat değişmişse
				ip_doc = frappe.get_doc("Item Price", found_stock_uom_price.name)
				ip_doc.price_list_rate = web_price
				ip_doc.flags.ignore_permissions = True
				ip_doc.save()
				stats["updated"] += 1
				print(f"   ✅ {item_code[:30]:<30} | {item_name[:40]:<40} | € {found_stock_uom_price.price_list_rate:.2f} → € {web_price:.2f} ({target_uom}) | Skor: {match_score:.2f}")
			else:
				stats["skipped"] += 1
		else:
			# Yeni kayıt oluştur
			new_price = frappe.get_doc({
				"doctype": "Item Price",
				"item_code": item_code,
				"price_list": price_list,
				"price_list_rate": web_price,
				"uom": target_uom,
				"currency": currency,
				"selling": 1,
				"buying": 0
			})
			new_price.flags.ignore_permissions = True
			new_price.insert()
			stats["created"] += 1
			print(f"   ✨ {item_code[:30]:<30} | {item_name[:40]:<40} | € {web_price:.2f} ({target_uom}) (YENİ) | Skor: {match_score:.2f}")
	
	print(f"\n{'='*80}")
	print(f"📊 ÖZET:")
	print(f"   🌐 Web'den çekilen ürün: {stats['total_web_products']}")
	print(f"   ✅ Eşleşen ürün: {stats['matched']}")
	print(f"   📝 Güncellenen fiyat: {stats['updated']}")
	print(f"   ✨ Oluşturulan yeni fiyat: {stats['created']}")
	print(f"   ⏭️  Atlanan (değişiklik yok): {stats['skipped']}")
	print(f"   ❌ Bulunamayan: {stats['not_found']}")
	print(f"{'='*80}\n")
	
	frappe.db.commit()
	
	return {
		"status": "success",
		"stats": stats
	}

