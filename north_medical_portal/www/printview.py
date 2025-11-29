# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import copy
import json
import os
import re
from typing import TYPE_CHECKING, Optional

import frappe
from frappe import _, cstr, get_module_path
from frappe.core.doctype.access_log.access_log import make_access_log
from frappe.core.doctype.document_share_key.document_share_key import is_expired
from frappe.utils import cint, escape_html, strip_html
from frappe.utils.jinja_globals import is_rtl

# Import all necessary functions from original printview
from frappe.www.printview import (
	get_print_format_doc,
	get_rendered_template as _original_get_rendered_template,
	validate_print_permission,
	get_print_style,
	set_link_titles,
	trigger_print_script,
)

# Hook into get_rendered_template to ensure address is always available
def get_rendered_template_with_address(*args, **kwargs):
	"""Wrapper around get_rendered_template to ensure address is set"""
	doc = kwargs.get('doc') or (args[0] if args else None)
	
	if doc:
		doctype = getattr(doc, 'doctype', None)
		if doctype in ["Purchase Order", "Purchase Invoice"]:
			_prepare_supplier_address_for_print(doc)
		elif doctype in ["Sales Order", "Sales Invoice", "Delivery Note"]:
			_prepare_customer_address_for_print(doc)
	
	# Call original function
	return _original_get_rendered_template(*args, **kwargs)

if TYPE_CHECKING:
	from frappe.model.document import Document
	from frappe.printing.doctype.print_format.print_format import PrintFormat

no_cache = 1


def _prepare_customer_address_for_print(doc):
	"""Prepare customer address display for print formats"""
	if not doc.get("customer"):
		return
	
	customer_addr = None
	shipping_addr = None
	
	# Try customer_address field first
	if doc.get("customer_address"):
		try:
			address_doc = frappe.get_doc("Address", doc.customer_address)
			customer_addr = address_doc.get_display()
		except Exception:
			pass
	
	# Try shipping_address_name
	if not customer_addr and doc.get("shipping_address_name"):
		try:
			address_doc = frappe.get_doc("Address", doc.shipping_address_name)
			shipping_addr = address_doc.get_display()
			if not customer_addr:
				customer_addr = shipping_addr
		except Exception:
			pass
	
	# If ERPNext already set address_display, use it
	if not customer_addr and doc.get("address_display") and doc.address_display:
		customer_addr = doc.address_display
	
	# Try shipping_address field
	if not customer_addr and doc.get("shipping_address"):
		shipping_addr = doc.shipping_address
		customer_addr = shipping_addr
	
	# Try customer's linked addresses
	if not customer_addr:
		try:
			addresses = frappe.db.sql("""
				SELECT a.name
				FROM `tabAddress` a
				INNER JOIN `tabDynamic Link` dl ON a.name = dl.parent
				WHERE dl.link_doctype = 'Customer' AND dl.link_name = %s
				ORDER BY 
					CASE WHEN a.address_type = 'Shipping' THEN 0 ELSE 1 END,
					a.creation DESC
				LIMIT 1
			""", (doc.customer,), as_dict=True)
			
			if addresses:
				address_doc = frappe.get_doc("Address", addresses[0].name)
				customer_addr = address_doc.get_display()
				shipping_addr = customer_addr
		except Exception:
			pass
	
	# Force set address to doc - multiple ways to ensure it persists
	if customer_addr:
		doc.address_display = customer_addr
		doc.__dict__['address_display'] = customer_addr
		setattr(doc, 'address_display', customer_addr)
		# Add to flags so it persists through serialization
		if not hasattr(doc, 'flags'):
			doc.flags = frappe._dict()
		doc.flags.address_display = customer_addr
	
	if shipping_addr:
		doc.shipping_address_display = shipping_addr
		doc.__dict__['shipping_address_display'] = shipping_addr
		setattr(doc, 'shipping_address_display', shipping_addr)
		if not hasattr(doc, 'flags'):
			doc.flags = frappe._dict()
		doc.flags.shipping_address_display = shipping_addr
	elif customer_addr:
		doc.shipping_address_display = customer_addr
		doc.__dict__['shipping_address_display'] = customer_addr
		setattr(doc, 'shipping_address_display', customer_addr)
		if not hasattr(doc, 'flags'):
			doc.flags = frappe._dict()
		doc.flags.shipping_address_display = customer_addr


def _prepare_supplier_address_for_print(doc):
	"""Prepare supplier address display for print formats"""
	if not doc.get("supplier"):
		return
	
	supplier_addr = None
	
	# Try supplier_address field first
	if doc.get("supplier_address"):
		try:
			address_doc = frappe.get_doc("Address", doc.supplier_address)
			supplier_addr = address_doc.get_display()
		except Exception:
			pass
	
	if not supplier_addr and doc.get("address_display"):
		supplier_addr = doc.address_display
	
	if not supplier_addr and doc.doctype == "Purchase Order" and doc.get("shipping_address_name"):
		try:
			address_doc = frappe.get_doc("Address", doc.shipping_address_name)
			supplier_addr = address_doc.get_display()
		except Exception:
			pass
	
	if not supplier_addr and doc.doctype == "Purchase Invoice" and doc.get("billing_address_name"):
		try:
			address_doc = frappe.get_doc("Address", doc.billing_address_name)
			supplier_addr = address_doc.get_display()
		except Exception:
			pass
	
	if not supplier_addr and doc.doctype == "Purchase Order" and doc.get("shipping_address"):
		supplier_addr = doc.shipping_address
	
	if not supplier_addr:
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
				supplier_addr = address_doc.get_display()
		except Exception:
			pass
	
	# Format address if single line
	if supplier_addr and '<br' not in supplier_addr.lower() and '\n' not in supplier_addr:
		# Format postal code and city on separate line
		formatted = re.sub(r'\s+(\d{5}\s+[A-ZÄÖÜ][A-ZÄÖÜ\s]+)', r'<br>\1', supplier_addr)
		if formatted != supplier_addr:
			formatted = re.sub(r'\s+(Industriestraße|Straße|Strasse|str\.|street)', r'<br>\1', formatted, flags=re.IGNORECASE)
		supplier_addr = formatted
	
	# Force set address to doc - multiple ways to ensure it persists
	if supplier_addr:
		doc.supplier_address_display = supplier_addr
		doc.__dict__['supplier_address_display'] = supplier_addr
		if not doc.get('address_display'):
			doc.address_display = supplier_addr
		doc.__dict__['address_display'] = supplier_addr
		setattr(doc, 'supplier_address_display', supplier_addr)
		setattr(doc, 'address_display', supplier_addr)
		if not hasattr(doc, 'flags'):
			doc.flags = frappe._dict()
		doc.flags.supplier_address_display = supplier_addr
		doc.flags.address_display = supplier_addr


def get_context(context):
	"""Override get_context to add language selection"""
	# Get language from form_dict or use current language
	selected_lang = frappe.form_dict.get("_lang") or frappe.local.lang
	
	# Temporarily set the language for this request
	if selected_lang and selected_lang != frappe.local.lang:
		frappe.local.lang = selected_lang
	
	# Build context (similar to original get_context)
	if not ((frappe.form_dict.doctype and frappe.form_dict.name) or frappe.form_dict.doc):
		return {
			"body": f"""
				<h1>Error</h1>
				<p>Parameters doctype and name required</p>
				<pre>{escape_html(frappe.as_json(frappe.form_dict, indent=2))}</pre>
				"""
		}

	if frappe.form_dict.doc:
		doc = frappe.form_dict.doc
	else:
		# Material Request için özel permission kontrolü
		if frappe.form_dict.doctype == "Material Request":
			# Doc'u ignore_permissions ile al (website permission kontrolü yapacağız)
			doc = frappe.get_doc(frappe.form_dict.doctype, frappe.form_dict.name, ignore_permissions=True)
			# Website permission kontrolü yap
			from north_medical_portal.utils.material_request_permission import has_website_permission
			if not has_website_permission(doc, ptype="print"):
				frappe.throw(_("Not Permitted"), frappe.PermissionError)
			
			# Material Request için print format context hazırla
			# Talebi oluşturan kullanıcı bilgisini ekle
			if doc.owner:
				doc.owner_name = frappe.utils.get_fullname(doc.owner)
				# requested_by field'ı varsa onu kullan
				if hasattr(doc, 'requested_by') and doc.requested_by:
					doc.requested_by_name = frappe.utils.get_fullname(doc.requested_by)
				else:
					doc.requested_by_name = doc.owner_name
			
			# Hedef depo bilgisini belirle
			if doc.set_warehouse:
				doc.target_warehouse = doc.set_warehouse
				doc.target_warehouse_display = doc.set_warehouse
			else:
				# Item'lardaki warehouse bilgilerini kontrol et
				warehouses = set()
				for item in doc.items:
					if item.warehouse:
						warehouses.add(item.warehouse)
				
				if len(warehouses) == 1:
					# Tüm item'lar aynı depoda
					doc.target_warehouse = list(warehouses)[0]
					doc.target_warehouse_display = list(warehouses)[0]
				elif len(warehouses) > 1:
					# Farklı depolar var
					doc.target_warehouse = None
					doc.target_warehouse_display = _("Per Item")
				else:
					# Hiç depo yok
					doc.target_warehouse = None
					doc.target_warehouse_display = "-"
		elif frappe.form_dict.doctype == "Stock Entry":
			# Stock Entry için print format context hazırla
			doc = frappe.get_doc(frappe.form_dict.doctype, frappe.form_dict.name, ignore_permissions=True)
			# Çıkış yapan kullanıcı bilgisini ekle
			if doc.modified_by:
				doc.modified_by_name = frappe.utils.get_fullname(doc.modified_by)
			else:
				doc.modified_by_name = None
			
			if doc.owner:
				doc.owner_name = frappe.utils.get_fullname(doc.owner)
			else:
				doc.owner_name = None
		elif frappe.form_dict.doctype in ["Sales Order", "Sales Invoice", "Delivery Note"]:
			# Sales Order, Sales Invoice ve Delivery Note için print format context hazırla
			doc = frappe.get_doc(frappe.form_dict.doctype, frappe.form_dict.name, ignore_permissions=True)
			
			# Customer address bilgisini hazırla
			_prepare_customer_address_for_print(doc)
		elif frappe.form_dict.doctype in ["Purchase Order", "Purchase Invoice"]:
			# Purchase Order ve Purchase Invoice için print format context hazırla
			doc = frappe.get_doc(frappe.form_dict.doctype, frappe.form_dict.name, ignore_permissions=True)
			
			# Modified By bilgisini ekle
			if doc.modified_by:
				doc.modified_by_name = frappe.utils.get_fullname(doc.modified_by)
			else:
				doc.modified_by_name = None
			
			# Supplier address bilgisini hazırla
			_prepare_supplier_address_for_print(doc)
		else:
			doc = frappe.get_doc(frappe.form_dict.doctype, frappe.form_dict.name)

	set_link_titles(doc)

	settings = frappe.parse_json(frappe.form_dict.settings)

	letterhead = frappe.form_dict.letterhead or None

	meta = frappe.get_meta(doc.doctype)

	print_format = get_print_format_doc(None, meta=meta)

	# Material Request için print permission kontrolünü atla
	if frappe.form_dict.doctype == "Material Request":
		frappe.flags.ignore_print_permissions = True
	
	# Ensure address is set before rendering
	current_doctype = frappe.form_dict.doctype
	if current_doctype in ["Purchase Order", "Purchase Invoice"]:
		_prepare_supplier_address_for_print(doc)
	elif current_doctype in ["Sales Order", "Sales Invoice", "Delivery Note"]:
		_prepare_customer_address_for_print(doc)
	
	if print_format and print_format.get("print_format_builder_beta"):
		from frappe.utils.weasyprint import get_html

		body = get_html(
			doctype=frappe.form_dict.doctype, name=frappe.form_dict.name, print_format=print_format.name
		)
		body += trigger_print_script
	else:
		body = get_rendered_template_with_address(
			doc,
			print_format=print_format,
			meta=meta,
			trigger_print=frappe.form_dict.trigger_print,
			no_letterhead=frappe.form_dict.no_letterhead,
			letterhead=letterhead,
			settings=settings,
		)
	
	# Flag'i temizle
	if frappe.form_dict.doctype == "Material Request":
		frappe.flags.ignore_print_permissions = False

	# Include selected print format name in access log
	print_format_name = getattr(print_format, "name", "Standard")

	make_access_log(
		doctype=frappe.form_dict.doctype,
		document=frappe.form_dict.name,
		file_type="PDF",
		method="Print",
		page=f"Print Format: {print_format_name}",
	)

	# Get only portal languages (tr, en, de, fr, it)
	portal_languages = ["tr", "en", "de", "fr", "it"]
	languages = frappe.get_all(
		"Language",
		filters={"enabled": 1, "name": ["in", portal_languages]},
		fields=["name", "language_name"],
		order_by="name"
	)
	
	# Format as list of tuples for template, maintain portal order
	language_map = {lang.name: lang.language_name for lang in languages}
	language_list = [(lang_code, language_map[lang_code]) for lang_code in portal_languages if lang_code in language_map]

	return {
		"body": body,
		"print_style": get_print_style(frappe.form_dict.style, print_format),
		"comment": frappe.session.user,
		"title": frappe.utils.strip_html(cstr(doc.get_title() or doc.name)),
		"lang": selected_lang,
		"layout_direction": "rtl" if is_rtl() else "ltr",
		"doctype": frappe.form_dict.doctype,
		"name": frappe.form_dict.name,
		"key": frappe.form_dict.get("key"),
		"print_format": print_format_name,
		"letterhead": letterhead,
		"no_letterhead": frappe.form_dict.no_letterhead,
		"pdf_generator": frappe.form_dict.get("pdf_generator", "wkhtmltopdf"),
		"languages": language_list,
		"current_lang": selected_lang,
	}
