"""
Malzeme Çıkışı Form Sayfası - Bayilerin kendi warehouse'larından malzeme çıkışı yapması
"""
import frappe
from north_medical_portal.utils.helpers import validate_dealer_access, get_user_warehouses
from north_medical_portal.www.api.stock import get_stock_status


def get_context(context):
	"""Sayfa context'ini hazırla"""
	# Permission kontrolü
	user_company = validate_dealer_access()
	
	# Kullanıcının yetkili olduğu warehouse'ları al
	warehouses = get_user_warehouses(user_company)
	
	# Stok verilerini al (ürün listesi için)
	stock_data = get_stock_status()
	
	context.update({
		"company": user_company,
		"warehouses": warehouses,
		"stock_items": stock_data.get("stock_data", []),
		"has_warehouses": len(warehouses) > 0
	})
	
	context.no_cache = 1



