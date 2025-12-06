# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _

from webshop.webshop.doctype.webshop_settings.webshop_settings import show_attachments


def _prepare_supplier_address_for_detail(doc):
	"""Prepare supplier address display for detail page"""
	if not doc.get("supplier"):
		return
	
	# Try supplier_address field first
	if doc.get("supplier_address"):
		try:
			address_doc = frappe.get_doc("Address", doc.supplier_address)
			doc.supplier_address_display = address_doc.get_display()
			return
		except Exception:
			pass
	
	# Try ERPNext's address_display field
	if doc.get("address_display"):
		doc.supplier_address_display = doc.address_display
		return
	
	# Try shipping_address_name for Purchase Order
	if doc.doctype == "Purchase Order" and doc.get("shipping_address_name"):
		try:
			address_doc = frappe.get_doc("Address", doc.shipping_address_name)
			doc.supplier_address_display = address_doc.get_display()
			return
		except Exception:
			pass
	
	# Try billing_address_name for Purchase Invoice
	if doc.doctype == "Purchase Invoice" and doc.get("billing_address_name"):
		try:
			address_doc = frappe.get_doc("Address", doc.billing_address_name)
			doc.supplier_address_display = address_doc.get_display()
			return
		except Exception:
			pass
	
	# Try shipping_address field
	if doc.doctype == "Purchase Order" and doc.get("shipping_address"):
		doc.supplier_address_display = doc.shipping_address
		return
	
	# Try supplier's linked addresses
	try:
		addresses = frappe.db.sql("""
			SELECT a.name
			FROM `tabAddress` a
			INNER JOIN `tabDynamic Link` dl ON a.name = dl.parent
			WHERE dl.link_doctype = 'Supplier' AND dl.link_name = %s
			ORDER BY 
				CASE WHEN a.address_type = 'Billing' THEN 0 ELSE 1 END,
				a.creation DESC
			LIMIT 1
		""", (doc.supplier,), as_dict=True)
		
		if addresses:
			address_doc = frappe.get_doc("Address", addresses[0].name)
			doc.supplier_address_display = address_doc.get_display()
	except Exception:
		pass


def get_context(context):
	context.no_cache = 1
	context.show_sidebar = True
	context.doc = frappe.get_doc(frappe.form_dict.doctype, frappe.form_dict.name)
	if hasattr(context.doc, "set_indicator"):
		context.doc.set_indicator()

	if show_attachments():
		context.attachments = get_attachments(frappe.form_dict.doctype, frappe.form_dict.name)

	context.parents = frappe.form_dict.parents
	context.title = frappe.form_dict.name
	context.payment_ref = frappe.db.get_value(
		"Payment Request", {"reference_name": frappe.form_dict.name}, "name"
	)

	context.enabled_checkout = frappe.get_doc("Webshop Settings").enable_checkout

	# Sales Order, Sales Invoice, Delivery Note, Material Request, Stock Entry ve Purchase Order için özel print format
	if frappe.form_dict.doctype == "Sales Order":
		context.print_format = "Sales Order Portal"
	elif frappe.form_dict.doctype == "Sales Invoice":
		context.print_format = "Sales Invoice Portal"
	elif frappe.form_dict.doctype == "Delivery Note":
		context.print_format = "Delivery Note Portal"
	elif frappe.form_dict.doctype == "Material Request":
		context.print_format = "Material Request Portal"
	elif frappe.form_dict.doctype == "Stock Entry":
		context.print_format = "Stock Entry Portal"
	elif frappe.form_dict.doctype == "Purchase Order":
		context.print_format = "Purchase Order Portal"
	elif frappe.form_dict.doctype == "Purchase Invoice":
		context.print_format = "Purchase Invoice Portal"
	else:
		default_print_format = frappe.db.get_value(
			"Property Setter",
			dict(property="default_print_format", doc_type=frappe.form_dict.doctype),
			"value",
		)
		if default_print_format:
			context.print_format = default_print_format
		else:
			context.print_format = "Standard"

	# Purchase Order ve Purchase Invoice için modified_by_name ve supplier address ekle
	if frappe.form_dict.doctype in ["Purchase Order", "Purchase Invoice"]:
		if context.doc.modified_by:
			context.doc.modified_by_name = frappe.utils.get_fullname(context.doc.modified_by)
		else:
			context.doc.modified_by_name = None
		
		# Supplier address bilgisini hazırla (detay sayfası için)
		_prepare_supplier_address_for_detail(context.doc)
	
	# Sales Order, Sales Invoice ve Delivery Note için customer address ekle
	if frappe.form_dict.doctype in ["Sales Order", "Sales Invoice", "Delivery Note"]:
		# Önce address_display ve shipping_address_display'i None olarak initialize et
		context.doc.address_display = None
		context.doc.shipping_address_display = None
		
		# Önce customer_address kontrol et
		if context.doc.get("customer_address"):
			try:
				address_doc = frappe.get_doc("Address", context.doc.customer_address)
				context.doc.address_display = address_doc.get_display()
			except Exception:
				pass
		
		# Eğer address_display yoksa, shipping_address_name kontrol et (Sales Order için)
		if not context.doc.address_display and frappe.form_dict.doctype == "Sales Order" and context.doc.get("shipping_address_name"):
			try:
				address_doc = frappe.get_doc("Address", context.doc.shipping_address_name)
				context.doc.shipping_address_display = address_doc.get_display()
			except Exception:
				pass
		
		# Eğer hala address_display yoksa, ERPNext'in set ettiği address_display varsa, onu kullan
		if not context.doc.address_display and context.doc.get("address_display"):
			context.doc.address_display = context.doc.address_display
		
		# Eğer hala address_display yoksa ve shipping_address field'ı varsa (ERPNext'in set ettiği), onu kullan
		if not context.doc.address_display and not context.doc.shipping_address_display and context.doc.get("shipping_address"):
			context.doc.shipping_address_display = context.doc.shipping_address
	
	# Admin kullanıcılar için bypass
	from north_medical_portal.utils.helpers import is_admin_user
	if not is_admin_user():
		if not frappe.has_website_permission(context.doc):
			frappe.throw(_("Not Permitted"), frappe.PermissionError)

	if context.doc.get("customer"):
		# check for the loyalty program of the customer
		customer_loyalty_program = frappe.db.get_value(
			"Customer", context.doc.customer, "loyalty_program"
		)
		if customer_loyalty_program:
			from erpnext.accounts.doctype.loyalty_program.loyalty_program import (
				get_loyalty_program_details_with_points,
			)

			loyalty_program_details = get_loyalty_program_details_with_points(
				context.doc.customer, customer_loyalty_program
			)
			context.available_loyalty_points = int(loyalty_program_details.get("loyalty_points"))

	# show Make Purchase Invoice button based on permission
	context.show_make_pi_button = frappe.has_permission("Purchase Invoice", "create")


def get_attachments(dt, dn):
	return frappe.get_all(
		"File",
		fields=["name", "file_name", "file_url", "is_private"],
		filters={"attached_to_name": dn, "attached_to_doctype": dt, "is_private": 0},
	)

