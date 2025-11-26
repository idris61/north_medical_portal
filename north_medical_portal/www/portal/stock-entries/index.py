"""
Stok Hareketleri Sayfası - Material Receipt/Issue
"""
import frappe
from north_medical_portal.utils.helpers import validate_dealer_access, get_company_warehouses
from north_medical_portal.www.api.stock_entry import get_stock_entries


def get_context(context):
	"""Sayfa context'ini hazırla"""
	user_company = validate_dealer_access()
	
	# Tüm stok hareketleri
	all_entries = get_stock_entries()
	
	# Material Receipt'ler
	receipts = get_stock_entries("Material Receipt")
	
	# Material Issue'lar
	issues = get_stock_entries("Material Issue")
	
	warehouses = get_company_warehouses(user_company)
	
	context.update({
		"company": user_company,
		"warehouses": warehouses,
		"stock_entries": all_entries.get("stock_entries", []),
		"receipts": receipts.get("stock_entries", []),
		"issues": issues.get("stock_entries", []),
		"has_entries": len(all_entries.get("stock_entries", [])) > 0
	})
	
	context.no_cache = 1








