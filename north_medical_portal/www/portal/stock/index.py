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
	
	context.update({
		"company": stock_data.get("company"),
		"warehouses": stock_data.get("warehouses", []),
		"stock_data": stock_data.get("stock_data", []),
		"has_stock_data": len(stock_data.get("stock_data", [])) > 0
	})
	
	context.no_cache = 1








