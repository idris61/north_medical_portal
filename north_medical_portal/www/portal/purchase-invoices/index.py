# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from erpnext.controllers.website_list_for_contact import get_transaction_list
from north_medical_portal.utils.helpers import validate_dealer_access, is_admin_user


def get_context(context):
	context.no_cache = 1
	context.show_sidebar = True
	context.title = _("Purchase Invoices")
	
	# Admin kullanıcılar için özel işlem
	if is_admin_user():
		# Admin için tüm Purchase Invoice'ları göster
		context.purchase_invoices = get_all_purchase_invoices()
	else:
		# Normal kullanıcılar için dealer access kontrolü
		user_company = validate_dealer_access()
		context.purchase_invoices = get_purchase_invoices_for_company(user_company)
	
	context.has_invoices = len(context.purchase_invoices) > 0


def get_all_purchase_invoices():
	"""Admin kullanıcılar için tüm Purchase Invoice'ları getir"""
	invoices = frappe.get_all(
		"Purchase Invoice",
		filters={"docstatus": ["<", 2]},
		fields=["name", "supplier", "supplier_name", "customer", "customer_name", "posting_date", "grand_total", "outstanding_amount", "status", "docstatus", "company", "modified_by"],
		order_by="posting_date desc",
		limit=100
	)
	
	# Her invoice için detayları ekle
	result = []
	for invoice in invoices:
		# Modified by bilgisini ekle
		modified_by_name = frappe.utils.get_fullname(invoice.modified_by) if invoice.modified_by else "-"
		invoice_dict = {
			"name": invoice.name,
			"supplier": invoice.supplier,
			"supplier_name": invoice.supplier_name,
			"customer": invoice.customer,
			"customer_name": invoice.customer_name,
			"posting_date": invoice.posting_date,
			"grand_total": invoice.grand_total,
			"outstanding_amount": invoice.outstanding_amount,
			"status": invoice.status,
			"docstatus": invoice.docstatus,
			"company": invoice.company,
			"modified_by": invoice.modified_by,
			"modified_by_name": modified_by_name
		}
		result.append(invoice_dict)
	
	return result


def get_purchase_invoices_for_company(company):
	"""Belirli bir şirket için Purchase Invoice'ları getir"""
	invoices = frappe.get_all(
		"Purchase Invoice",
		filters={"docstatus": ["<", 2], "company": company},
		fields=["name", "supplier", "supplier_name", "customer", "customer_name", "posting_date", "grand_total", "outstanding_amount", "status", "docstatus", "company", "modified_by"],
		order_by="posting_date desc",
		limit=100
	)
	
	# Her invoice için detayları ekle
	result = []
	for invoice in invoices:
		# Modified by bilgisini ekle
		modified_by_name = frappe.utils.get_fullname(invoice.modified_by) if invoice.modified_by else "-"
		invoice_dict = {
			"name": invoice.name,
			"supplier": invoice.supplier,
			"supplier_name": invoice.supplier_name,
			"customer": invoice.customer,
			"customer_name": invoice.customer_name,
			"posting_date": invoice.posting_date,
			"grand_total": invoice.grand_total,
			"outstanding_amount": invoice.outstanding_amount,
			"status": invoice.status,
			"docstatus": invoice.docstatus,
			"company": invoice.company,
			"modified_by": invoice.modified_by,
			"modified_by_name": modified_by_name
		}
		result.append(invoice_dict)
	
	return result

