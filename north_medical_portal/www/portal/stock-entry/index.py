"""
Stock Entry Portal Detail Page
"""
import frappe
from frappe import _
from north_medical_portal.utils.helpers import validate_dealer_access


def get_context(context):
	"""Stock Entry detay sayfası için context"""
	context.no_cache = 1
	context.show_sidebar = True
	
	# Permission kontrolü
	user_company = validate_dealer_access()
	
	# Stock Entry dokümanını al
	stock_entry_name = frappe.form_dict.name
	if not stock_entry_name:
		frappe.throw(_("Stock Entry adı belirtilmedi"))
	
	stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)
	
	# Kullanıcının şirketine ait mi kontrol et
	if stock_entry.company != user_company:
		frappe.throw(_("Bu Stock Entry'ye erişim yetkiniz bulunmamaktadır"), frappe.PermissionError)
	
	context.doc = stock_entry
	context.title = stock_entry_name
	context.parents = [{"label": _("Malzeme Çıkışı"), "route": "/portal/material-issue"}]
	
	# Print format
	default_print_format = frappe.db.get_value(
		"Property Setter",
		dict(property="default_print_format", doc_type="Stock Entry"),
		"value",
	)
	if default_print_format:
		context.print_format = default_print_format
	else:
		context.print_format = "Standard"
	
	# Attachments
	context.attachments = frappe.get_all(
		"File",
		fields=["name", "file_name", "file_url", "is_private"],
		filters={"attached_to_name": stock_entry_name, "attached_to_doctype": "Stock Entry", "is_private": 0},
	)
	
	# Items için resim bilgilerini ekle
	for item in stock_entry.items:
		item_image = frappe.db.get_value("Item", item.item_code, "image")
		item.thumbnail = item_image
		if item_image:
			item.image_url = frappe.utils.get_url(item_image)

