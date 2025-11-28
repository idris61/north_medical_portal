"""
Stok Durumu Sayfası - Bayilerin anlık stok durumlarını gösterir
Sadece kullanıcının yetkili olduğu warehouse'ları gösterir
"""
import frappe
from north_medical_portal.utils.helpers import validate_dealer_access
from north_medical_portal.www.api.stock import get_stock_status


def get_context(context):
	"""Sayfa context'ini hazırla"""
	# Permission kontrolü
	user_company = validate_dealer_access()
	
	# API'den stok verilerini al
	stock_data = get_stock_status()
	
	# Item resimlerini ekle
	stock_items = stock_data.get("stock_data", [])
	for item in stock_items:
		item_image = frappe.db.get_value("Item", item.get("item_code"), "image")
		item["thumbnail"] = item_image
		if item_image:
			item["image_url"] = frappe.utils.get_url(item_image)
	
	context.update({
		"company": stock_data.get("company"),
		"warehouses": stock_data.get("warehouses", []),
		"stock_data": stock_items,
		"has_stock_data": len(stock_items) > 0,
		"can_edit_reorder": stock_data.get("can_edit_reorder", False)
	})
	
	context.no_cache = 1
	context.show_sidebar = True








