# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from erpnext.controllers.website_list_for_contact import get_transaction_list
from north_medical_portal.utils.helpers import validate_dealer_access, is_admin_user


def get_context(context):
	context.no_cache = 1
	context.show_sidebar = True
	context.title = _("Purchase Orders")
	
	# Admin kullanıcılar için özel işlem
	if is_admin_user():
		# Admin için tüm Purchase Order'ları göster
		context.purchase_orders = get_all_purchase_orders()
	else:
		# Normal kullanıcılar için dealer access kontrolü
		user_company = validate_dealer_access()
		context.purchase_orders = get_purchase_orders_for_company(user_company)
	
	context.has_orders = len(context.purchase_orders) > 0


def get_all_purchase_orders():
	"""Admin kullanıcılar için tüm Purchase Order'ları getir"""
	orders = frappe.get_all(
		"Purchase Order",
		filters={"docstatus": ["<", 2]},
		fields=["name", "supplier", "supplier_name", "customer", "customer_name", "transaction_date", "grand_total", "status", "docstatus", "company", "modified_by"],
		order_by="transaction_date desc",
		limit=100
	)
	
	# Her order için detayları ekle
	result = []
	for order in orders:
		# Modified by bilgisini ekle
		modified_by_name = frappe.utils.get_fullname(order.modified_by) if order.modified_by else "-"
		order_dict = {
			"name": order.name,
			"supplier": order.supplier,
			"supplier_name": order.supplier_name,
			"customer": order.customer,
			"customer_name": order.customer_name,
			"transaction_date": order.transaction_date,
			"grand_total": order.grand_total,
			"status": order.status,
			"docstatus": order.docstatus,
			"company": order.company,
			"modified_by": order.modified_by,
			"modified_by_name": modified_by_name
		}
		result.append(order_dict)
	
	return result


def get_purchase_orders_for_company(company):
	"""Belirli bir şirket için Purchase Order'ları getir"""
	orders = frappe.get_all(
		"Purchase Order",
		filters={"docstatus": ["<", 2], "company": company},
		fields=["name", "supplier", "supplier_name", "customer", "customer_name", "transaction_date", "grand_total", "status", "docstatus", "company", "modified_by"],
		order_by="transaction_date desc",
		limit=100
	)
	
	# Her order için detayları ekle
	result = []
	for order in orders:
		# Modified by bilgisini ekle
		modified_by_name = frappe.utils.get_fullname(order.modified_by) if order.modified_by else "-"
		order_dict = {
			"name": order.name,
			"supplier": order.supplier,
			"supplier_name": order.supplier_name,
			"customer": order.customer,
			"customer_name": order.customer_name,
			"transaction_date": order.transaction_date,
			"grand_total": order.grand_total,
			"status": order.status,
			"docstatus": order.docstatus,
			"company": order.company,
			"modified_by": order.modified_by,
			"modified_by_name": modified_by_name
		}
		result.append(order_dict)
	
	return result

