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
			"name", "customer", "customer_name", "transaction_date", "delivery_date",
			"grand_total", "status", "docstatus", "creation"
		],
		order_by="transaction_date desc",
		limit=100
	)
	
	# Her order için items_preview ekle
	for order in sales_orders:
		order_doc = frappe.get_doc("Sales Order", order.name)
		order["items_preview"] = ", ".join([d.item_name for d in order_doc.items if d.item_name])
	
	return {"sales_orders": sales_orders}










