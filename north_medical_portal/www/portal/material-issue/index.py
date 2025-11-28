"""
Malzeme Çıkışı Liste Sayfası - Bayilerin malzeme çıkışlarını listeler
"""
import frappe
from north_medical_portal.utils.helpers import validate_dealer_access
from north_medical_portal.www.api.stock_entry import get_stock_entries


def get_context(context):
	"""Sayfa context'ini hazırla"""
	# Permission kontrolü
	user_company = validate_dealer_access()
	
	# Material Issue tipindeki stok hareketlerini al
	entries_data = get_stock_entries("Material Issue")
	
	context.update({
		"company": user_company,
		"stock_entries": entries_data.get("stock_entries", []),
		"has_entries": len(entries_data.get("stock_entries", [])) > 0
	})
	
	context.no_cache = 1
	context.show_sidebar = True

