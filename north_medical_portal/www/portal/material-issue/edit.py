"""
Malzeme Çıkışı Düzenleme Sayfası - Bayilerin malzeme çıkışı belgelerini düzenlemesi
"""
import frappe
from north_medical_portal.utils.helpers import validate_dealer_access, get_user_warehouses
from north_medical_portal.www.api.stock_entry import get_stock_entry_for_edit


def get_context(context):
	"""Sayfa context'ini hazırla"""
	# Permission kontrolü
	user_company = validate_dealer_access()
	
	# URL'den stock_entry_name'i al
	stock_entry_name = frappe.form_dict.name
	
	if not stock_entry_name:
		frappe.throw("Stock Entry adı belirtilmedi", frappe.PermissionError)
	
	# Belgeyi al ve kontrol et
	try:
		entry_data = get_stock_entry_for_edit(stock_entry_name)
	except Exception as e:
		frappe.throw("Belge bulunamadı veya düzenlenemez", frappe.PermissionError)
	
	# Kullanıcının yetkili olduğu warehouse'ları al
	warehouses = get_user_warehouses(user_company)
	
	# Default warehouse (belgedeki warehouse)
	default_warehouse = entry_data.get("warehouse")
	single_warehouse = len(warehouses) == 1
	
	context.update({
		"company": user_company,
		"warehouses": warehouses,
		"default_warehouse": default_warehouse,
		"has_warehouses": len(warehouses) > 0,
		"single_warehouse": single_warehouse,
		"stock_entry_name": stock_entry_name,
		"entry_data": entry_data
	})
	
	context.no_cache = 1
	context.show_sidebar = True

