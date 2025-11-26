"""
Faturalar API - Bayilerin faturalarını listele
"""
import frappe
from frappe import _
from north_medical_portal.utils.helpers import validate_dealer_access


@frappe.whitelist()
def get_invoices():
	"""Bayi faturalarını listele"""
	user_company = validate_dealer_access()
	
	# Sales Invoice'ları getir
	invoices = frappe.get_all(
		"Sales Invoice",
		filters={"company": user_company},
		fields=[
			"name", "customer", "posting_date", "due_date", 
			"grand_total", "outstanding_amount", "status", 
			"docstatus", "creation"
		],
		order_by="posting_date desc",
		limit=100
	)
	
	return {"invoices": invoices}








