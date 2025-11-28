"""
Web sitesindeki gerçek fiyatları kullanarak Item Price tablosundaki fiyatları güncelle.

Kullanım:
    bench --site north_medical.local execute "north_medical_portal.utils.fix_prices_from_website.fix_all_prices_from_website"
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


def parse_variations_from_html(html_content: str) -> List[Dict]:
	"""Ürün detay HTML'inden data-product_variations JSON'unu parse et."""
	soup = BeautifulSoup(html_content, "html.parser")
	form = soup.find("form", class_=re.compile(r"variations_form"))
	if not form:
		return []

	data_attr = form.get("data-product_variations")
	if not data_attr:
		return []

	json_text = html.unescape(data_attr)
	try:
		variations = json.loads(json_text)
		return variations if isinstance(variations, list) else []
	except Exception as e:
		return []


def extract_uom_and_price_from_variation(variation: Dict) -> Tuple[Optional[str], Optional[float]]:
	"""
	Variation'dan UOM ve fiyat bilgisini çıkar.
	
	Returns:
		(uom_name, price)
	"""
	attrs = variation.get("attributes") or {}
	display_price = variation.get("display_price")
	
	if not display_price:
		return None, None
	
	# Attribute değerinden bilgi çıkar
	attr_val = None
	for key, val in attrs.items():
		if val:
			attr_val = str(val)
			break
	
	if not attr_val:
		return None, None
	
	attr_text = attr_val.lower().replace("-", " ").replace("_", " ")
	price = float(display_price)
	
	uom_name = None
	
	# UOM ismi
	if "karton" in attr_text:
		uom_name = "Carton"
	elif "packung" in attr_text:
		uom_name = "Packung"
	elif "box" in attr_text or "boxen" in attr_text:
		uom_name = "Pack"
	elif "pack" in attr_text:
		uom_name = "Pack"
	elif "stuck" in attr_text or "stück" in attr_text:
		uom_name = "Piece"
	elif "roll" in attr_text or "rolle" in attr_text:
		uom_name = "Roll"
	
	return uom_name, price


def get_prices_from_website(variations: List[Dict]) -> Dict[str, float]:
	"""
	Web sitesindeki variation'lardan UOM bazlı fiyatları çıkar.
	
	Returns:
		{"Packung": 6.8, "Carton": 68.0}
	"""
	prices = {}
	
	for var in variations:
		uom, price = extract_uom_and_price_from_variation(var)
		if not uom or not price:
			continue
		
		# Aynı UOM için birden fazla fiyat varsa ortalama al
		if uom not in prices:
			prices[uom] = []
		prices[uom].append(price)
	
	# Ortalama fiyatları hesapla
	result = {}
	for uom, price_list in prices.items():
		if price_list:
			result[uom] = sum(price_list) / len(price_list)
	
	return result


def update_item_prices(item_code: str, uom_prices: Dict[str, float], price_list: str = "Standard Selling"):
	"""
	Item Price tablosundaki fiyatları güncelle veya oluştur.
	"""
	try:
		# Mevcut Item Price kayıtlarını al
		existing_prices = frappe.db.get_all(
			"Item Price",
			fields=["name", "uom", "price_list_rate"],
			filters={
				"item_code": item_code,
				"price_list": price_list
			}
		)
		
		existing_uoms = {r.uom: r for r in existing_prices}
		
		updated_count = 0
		created_count = 0
		
		for uom, new_price in uom_prices.items():
			if uom in existing_uoms:
				# Güncelle
				existing = existing_uoms[uom]
				if abs(existing.price_list_rate - new_price) > 0.01:
					frappe.db.set_value(
						"Item Price",
						existing.name,
						"price_list_rate",
						new_price
					)
					updated_count += 1
			else:
				# Yeni oluştur
				item_price = frappe.new_doc("Item Price")
				item_price.item_code = item_code
				item_price.price_list = price_list
				item_price.uom = uom
				item_price.price_list_rate = new_price
				item_price.currency = "EUR"
				item_price.flags.ignore_permissions = True
				item_price.insert()
				created_count += 1
		
		frappe.db.commit()
		
		return updated_count, created_count
		
	except Exception as e:
		frappe.log_error(f"Error updating prices for {item_code}: {str(e)}", "Price Fix Error")
		return 0, 0


@frappe.whitelist()
def fix_all_prices_from_website(max_products=100):
	"""
	Tüm ürünlerin Item Price kayıtlarını web sitesindeki gerçek fiyatlarla güncelle.
	"""
	# Price List kontrolü
	price_list_name = "Standard Selling"
	if not frappe.db.exists("Price List", price_list_name):
		return {"status": "error", "message": "Price List not found"}
	
	# ERP'deki tüm aktif ürünler
	erp_items = frappe.get_all(
		"Item",
		filters={"disabled": 0, "is_sales_item": 1},
		fields=["name", "item_code", "item_name", "stock_uom"],
		order_by="item_name asc"
	)
	
	# Web sitesinden tüm ürün detay URL'lerini çek
	base_url = "https://www.northmedical.de/produkte/"
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
	}
	
	product_urls = []
	max_pages = 10
	
	for page in range(1, max_pages + 1):
		if page == 1:
			url = base_url
		else:
			url = f"{base_url}page/{page}/"
		
		try:
			resp = requests.get(url, timeout=30, headers=headers)
			if resp.status_code != 200:
				break
			
			soup = BeautifulSoup(resp.content, "html.parser")
			products = soup.find_all("li", class_=re.compile(r"product"))
			
			if not products:
				break
			
			for prod in products:
				link = prod.find("a", href=True)
				title = prod.find(["h2", "h3", "h4"])
				if link and title:
					href = link["href"]
					if not href.startswith("http"):
						href = f"https://www.northmedical.de{href}"
					product_urls.append((title.get_text(strip=True), href))
			
			time.sleep(0.3)
		except Exception as e:
			frappe.log_error(f"Error fetching page {page}: {str(e)}", "Fix Prices From Website")
			break
	
	stats = {
		"processed": 0,
		"matched": 0,
		"updated": 0,
		"created": 0,
		"skipped": 0,
		"errors": 0
	}
	
	# Her ürün için detay sayfasını çek ve fiyatları güncelle
	for web_name, web_url in product_urls[:max_products]:
		try:
			stats["processed"] += 1
			
			# ERP'de eşleşen ürünü bul
			matched_item, match_score = find_matching_item(web_name, erp_items, threshold=0.6)
			
			if not matched_item or match_score < 0.6:
				stats["skipped"] += 1
				continue
			
			stats["matched"] += 1
			
			# Ürün detay sayfasını çek
			resp = requests.get(web_url, timeout=30, headers=headers)
			if resp.status_code != 200:
				stats["errors"] += 1
				continue
			
			variations = parse_variations_from_html(resp.content)
			
			if not variations:
				stats["skipped"] += 1
				continue
			
			# UOM bazlı fiyatları çıkar
			uom_prices = get_prices_from_website(variations)
			
			if not uom_prices:
				stats["skipped"] += 1
				continue
			
			# Piece fiyatını hesapla (eğer yoksa)
			# Eğer Packung fiyatı varsa, Piece fiyatı = Packung / 100 (çünkü 1 Packung = 100 Piece)
			if "Piece" not in uom_prices:
				if "Packung" in uom_prices:
					packung_price = uom_prices["Packung"]
					# Conversion factor'ı kontrol et
					conversions = frappe.db.get_all(
						"UOM Conversion Detail",
						fields=["uom", "conversion_factor"],
						filters={"parent": matched_item.item_code}
					)
					packung_factor = next((c.conversion_factor for c in conversions if c.uom == "Packung"), 100.0)
					if packung_factor > 0:
						uom_prices["Piece"] = packung_price / packung_factor
			
			# Item Price kayıtlarını güncelle
			updated, created = update_item_prices(
				matched_item.item_code, 
				uom_prices, 
				price_list_name
			)
			
			if updated > 0 or created > 0:
				stats["updated"] += updated
				stats["created"] += created
			else:
				stats["skipped"] += 1
			
			time.sleep(0.5)  # Rate limiting
			
		except Exception as e:
			stats["errors"] += 1
			frappe.log_error(f"Error processing {web_name}: {str(e)}", "Fix Prices From Website")
	
	return {
		"status": "success",
		"stats": stats
	}

