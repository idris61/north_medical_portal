# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from frappe.utils import flt
import erpnext.controllers.website_list_for_contact as original_module


def get_list_for_transactions(doctype, txt, filters, limit_start, limit_page_length=20, ignore_permissions=False, fields=None, order_by=None):
	"""Override get_list_for_transactions to include supplier and customer fields"""
	# Purchase Order ve Purchase Invoice için supplier ve modified_by field'larını ekle
	if doctype in ["Purchase Order", "Purchase Invoice"]:
		# fields parametresi None veya "name" ise, supplier ve modified_by ekle
		if fields is None or fields == "name":
			fields = ["name", "supplier", "supplier_name", "modified_by"]
		elif isinstance(fields, list):
			# List ise, eksik field'ları ekle
			required_fields = ["supplier", "supplier_name", "modified_by"]
			for field in required_fields:
				if field not in fields:
					fields.append(field)
		elif isinstance(fields, str):
			# String ise, eksik field'ları ekle
			if "supplier" not in fields:
				if fields == "name":
					fields = "name,supplier,supplier_name,modified_by"
				else:
					fields = fields + ",supplier,supplier_name"
			if "modified_by" not in fields:
				fields = fields + ",modified_by"
	# Sales Order için customer field'larını ekle
	elif doctype == "Sales Order":
		# fields parametresi None veya "name" ise, customer ekle
		if fields is None or fields == "name":
			fields = ["name", "customer", "customer_name"]
		elif isinstance(fields, list):
			# List ise, eksik field'ları ekle
			required_fields = ["customer", "customer_name"]
			for field in required_fields:
				if field not in fields:
					fields.append(field)
		elif isinstance(fields, str):
			# String ise, eksik field'ları ekle
			if "customer" not in fields:
				if fields == "name":
					fields = "name,customer,customer_name"
				else:
					fields = fields + ",customer,customer_name"
	
	# Call original function
	return original_module.get_list_for_transactions(
		doctype, txt, filters, limit_start, limit_page_length, ignore_permissions, fields, order_by
	)


def post_process(doctype, data):
	"""Override post_process to add supplier and customer info for Purchase Order and Purchase Invoice"""
	# Call original post_process
	result = original_module.post_process(doctype, data)
	
	# Add supplier info for Purchase Order and Purchase Invoice
	if doctype in ["Purchase Order", "Purchase Invoice"]:
		for doc in result:
			# DocType bilgisini ekle (template'de kullanmak için)
			doc.doctype = doctype
			
			# Supplier bilgisi zaten doc'da olabilir, kontrol et
			if not hasattr(doc, 'supplier_name') or not doc.supplier_name:
				if hasattr(doc, 'supplier') and doc.supplier:
					doc.supplier_name = frappe.db.get_value("Supplier", doc.supplier, "supplier_name") or doc.supplier
				else:
					doc.supplier_name = None
			
			# Modified by bilgisini ekle
			if hasattr(doc, 'modified_by') and doc.modified_by:
				doc.modified_by_name = frappe.utils.get_fullname(doc.modified_by)
			else:
				doc.modified_by_name = None
	
	# Add customer info for Sales Order
	if doctype == "Sales Order":
		for doc in result:
			# DocType bilgisini ekle (template'de kullanmak için)
			doc.doctype = doctype
			
			# Customer bilgisi zaten doc'da olabilir, kontrol et
			if not hasattr(doc, 'customer_name') or not doc.customer_name:
				if hasattr(doc, 'customer') and doc.customer:
					doc.customer_name = frappe.db.get_value("Customer", doc.customer, "customer_name") or doc.customer
				else:
					doc.customer_name = None
	
	return result


def get_list_context_po(context=None):
	"""Override Purchase Order get_list_context to use custom row template"""
	from erpnext.controllers.website_list_for_contact import get_list_context as original_get_list_context
	list_context = original_get_list_context(context)
	# Custom row template kullan
	list_context["row_template"] = "north_medical_portal/templates/includes/transaction_row.html"
	return list_context


def get_list_context_pi(context=None):
	"""Override Purchase Invoice get_list_context to use custom row template"""
	from erpnext.controllers.website_list_for_contact import get_list_context as original_get_list_context
	list_context = original_get_list_context(context)
	# Custom row template kullan
	list_context["row_template"] = "north_medical_portal/templates/includes/transaction_row.html"
	return list_context


def override_post_process():
	"""Override ERPNext'in post_process, get_list_for_transactions ve get_list_context fonksiyonlarını"""
	original_module.post_process = post_process
	original_module.get_list_for_transactions = get_list_for_transactions
	
	# Purchase Order ve Purchase Invoice için get_list_context'i override et
	import erpnext.buying.doctype.purchase_order.purchase_order as po_module
	import erpnext.accounts.doctype.purchase_invoice.purchase_invoice as pi_module
	
	po_module.get_list_context = get_list_context_po
	pi_module.get_list_context = get_list_context_pi


