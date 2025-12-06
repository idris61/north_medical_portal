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
	
	# Admin kullanıcılar için bypass
	from north_medical_portal.utils.helpers import is_admin_user
	if not is_admin_user():
		# Kullanıcının şirketine ait mi kontrol et
		if stock_entry.company != user_company:
			frappe.throw(_("Bu Stock Entry'ye erişim yetkiniz bulunmamaktadır"), frappe.PermissionError)
	
	context.doc = stock_entry
	context.title = stock_entry_name
	context.parents = [{"label": _("Malzeme Çıkışı"), "route": "/portal/material-issue"}]
	
	# Stock Entry için özel print format
	context.print_format = "Stock Entry Portal"
	
	# Çıkış yapan kullanıcı bilgisini ekle
	if stock_entry.modified_by:
		stock_entry.modified_by_name = frappe.utils.get_fullname(stock_entry.modified_by)
	else:
		stock_entry.modified_by_name = None
	
	if stock_entry.owner:
		stock_entry.owner_name = frappe.utils.get_fullname(stock_entry.owner)
	else:
		stock_entry.owner_name = None
	
	# Tarih formatını hazırla
	if stock_entry.posting_date:
		stock_entry.posting_date_formatted = frappe.utils.format_date(stock_entry.posting_date, 'medium')
	elif stock_entry.creation:
		stock_entry.posting_date_formatted = frappe.utils.format_date(stock_entry.creation, 'medium')
	else:
		stock_entry.posting_date_formatted = "-"
	
	# Items için resim bilgilerini ekle ve abbreviation hesapla - Material Request gibi
	# items'ı direkt değiştirmek yerine, her item'a özellik ekle
	if stock_entry.items:
		for item in stock_entry.items:
			# Resim bilgilerini ekle
			try:
				if item.item_code:
					item_image = frappe.db.get_value("Item", item.item_code, "image")
					item.thumbnail = item_image
					if item_image:
						item.image_url = frappe.utils.get_url(item_image)
					else:
						item.image_url = None
				else:
					item.thumbnail = None
					item.image_url = None
			except:
				item.thumbnail = None
				item.image_url = None
			
			# Abbreviation hesapla
			try:
				item_name_or_code = item.item_name or item.item_code
				if item_name_or_code:
					item.abbr = frappe.utils.get_abbr(item_name_or_code) or "NA"
				else:
					item.abbr = "NA"
			except:
				item.abbr = "NA"
			
			# Qty formatını hazırla
			from frappe.utils import flt
			try:
				qty = flt(item.qty or 0)
				item.qty_formatted = f"{qty:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
				if item.qty_formatted.endswith(",00"):
					item.qty_formatted = item.qty_formatted[:-3]
			except:
				item.qty_formatted = str(item.qty or 0) if item.qty else "0"
	
	# Attachments
	context.attachments = frappe.get_all(
		"File",
		fields=["name", "file_name", "file_url", "is_private"],
		filters={"attached_to_name": stock_entry_name, "attached_to_doctype": "Stock Entry", "is_private": 0},
	)

