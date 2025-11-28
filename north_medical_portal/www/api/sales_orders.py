"""
Satış Siparişleri API - Bayilerin satış siparişlerini listele
"""
import frappe
from frappe import _
from north_medical_portal.utils.helpers import validate_dealer_access


@frappe.whitelist()
def get_sales_orders():
	"""Bayi satış siparişlerini listele"""
	user_company = validate_dealer_access()
	
	sales_orders = frappe.get_all(
		"Sales Order",
		filters={"company": user_company},
		fields=[
			"name", "customer", "transaction_date", "delivery_date",
			"grand_total", "status", "docstatus", "creation"
		],
		order_by="transaction_date desc",
		limit=100
	)
	
	return {"sales_orders": sales_orders}










