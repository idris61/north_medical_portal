"""
Faturalar Sayfası
"""
import frappe
from north_medical_portal.utils.helpers import validate_dealer_access
from north_medical_portal.www.api.invoices import get_invoices


def get_context(context):
	"""Sayfa context'ini hazırla"""
	user_company = validate_dealer_access()
	
	invoices_data = get_invoices()
	
	context.update({
		"company": user_company,
		"invoices": invoices_data.get("invoices", []),
		"has_invoices": len(invoices_data.get("invoices", [])) > 0
	})
	
	context.no_cache = 1










