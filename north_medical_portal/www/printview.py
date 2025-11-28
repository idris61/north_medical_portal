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
	get_rendered_template,
	validate_print_permission,
	get_print_style,
	set_link_titles,
	trigger_print_script,
)

if TYPE_CHECKING:
	from frappe.model.document import Document
	from frappe.printing.doctype.print_format.print_format import PrintFormat

no_cache = 1


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
		else:
			doc = frappe.get_doc(frappe.form_dict.doctype, frappe.form_dict.name)

	set_link_titles(doc)

	settings = frappe.parse_json(frappe.form_dict.settings)

	letterhead = frappe.form_dict.letterhead or None

	meta = frappe.get_meta(doc.doctype)

	print_format = get_print_format_doc(None, meta=meta)

	# Material Request için print permission kontrolünü atla (zaten yaptık)
	if frappe.form_dict.doctype == "Material Request":
		frappe.flags.ignore_print_permissions = True
	
	if print_format and print_format.get("print_format_builder_beta"):
		from frappe.utils.weasyprint import get_html

		body = get_html(
			doctype=frappe.form_dict.doctype, name=frappe.form_dict.name, print_format=print_format.name
		)
		body += trigger_print_script
	else:
		body = get_rendered_template(
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
