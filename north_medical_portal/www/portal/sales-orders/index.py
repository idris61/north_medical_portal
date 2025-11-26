"""
Satış Siparişleri Sayfası
"""
import frappe
from north_medical_portal.utils.helpers import validate_dealer_access
from north_medical_portal.www.api.sales_orders import get_sales_orders


def get_context(context):
	"""Sayfa context'ini hazırla"""
	user_company = validate_dealer_access()
	
	orders_data = get_sales_orders()
	
	context.update({
		"company": user_company,
		"sales_orders": orders_data.get("sales_orders", []),
		"has_orders": len(orders_data.get("sales_orders", [])) > 0
	})
	
	context.no_cache = 1








