"""
Portal Settings menüsünü düzenle:
1. Stok Özeti'nden birini kaldır (duplicate)
2. Stok Özeti'ni Sevkiyatlar'ın altına taşı
3. Issues'ı "Talepler" olarak değiştir
"""
import frappe


def fix_portal_menu():
	"""Portal Settings menüsünü düzenle"""
	try:
		portal_settings = frappe.get_doc("Portal Settings", "Portal Settings")
		
		# 0. Eski "Malzeme Talebi" menü öğelerini kaldır (ERPNext default)
		# Yeni portal rotası: /portal/material-requests
		removed_old_mr = 0
		
		# ERPNext default route'larını kaldır (/material-requests, /material-request)
		for item in list(portal_settings.get("menu", [])):
			if item.route in ("/material-requests", "/material-request"):
				portal_settings.remove(item)
				removed_old_mr += 1
		
		# /portal/material-requests duplicate'lerini kaldır (sadece bir tane olmalı)
		portal_mr_items = [d for d in portal_settings.get("menu", []) if d.route == "/portal/material-requests"]
		if len(portal_mr_items) > 1:
			# İlkini tut, diğerlerini kaldır
			for dup_item in portal_mr_items[1:]:
				portal_settings.remove(dup_item)
				removed_old_mr += 1
		
		# 1. Stok Özeti duplicate'lerini bul ve birini kaldır
		stock_summary_items = [d for d in portal_settings.get("menu", []) if d.get("route") == "/portal/stock"]
		if len(stock_summary_items) > 1:
			# İlkini tut, diğerlerini kaldır
			for item in stock_summary_items[1:]:
				portal_settings.remove(item)
		
		# 2. Issues'ı "Talepler" olarak değiştir
		issues_items = [d for d in portal_settings.get("menu", []) if d.get("route") == "/issues"]
		for item in issues_items:
			if item.title == "Issues" or item.title == "Sorunlar":
				item.title = "Talepler"
		
		# 3. Stok Özeti'ni Sevkiyatlar'ın altına taşı
		# Önce menü öğelerini sıralayalım
		menu_items = list(portal_settings.menu)
		
		# Sevkiyatlar'ın index'ini bul
		shipments_idx = None
		stock_summary_idx = None
		
		for idx, item in enumerate(menu_items):
			if item.route == "/shipments":
				shipments_idx = idx
			elif item.route == "/portal/stock":
				stock_summary_idx = idx
		
		# Eğer Stok Özeti varsa ve Sevkiyatlar'ın altında değilse, taşı
		if stock_summary_idx is not None and shipments_idx is not None:
			if stock_summary_idx != shipments_idx + 1:
				# Stok Özeti'ni kaldır
				stock_item = menu_items.pop(stock_summary_idx)
				# Sevkiyatlar'ın hemen altına ekle
				menu_items.insert(shipments_idx + 1, stock_item)
				# Menüyü yeniden set et
				portal_settings.menu = []
				for item in menu_items:
					portal_settings.append("menu", item)
		
		# 4. Material Issue menüsünü ekle (yoksa)
		material_issue_exists = any(d.route == "/portal/material-issue" for d in portal_settings.get("menu", []))
		if not material_issue_exists:
			# Sevkiyatlar'dan sonra ekle
			shipments_idx = None
			for idx, item in enumerate(portal_settings.menu):
				if item.route == "/shipments":
					shipments_idx = idx
					break
			
			if shipments_idx is not None:
				# Material Issue'yu ekle
				portal_settings.append("menu", {
					"title": "Malzeme Çıkışı",
					"route": "/portal/material-issue",
					"reference_doctype": "Stock Entry",
					"role": "Customer",
					"enabled": 1
				})
				# Sıralamayı düzelt
				menu_items = list(portal_settings.menu)
				material_issue_item = menu_items.pop()
				menu_items.insert(shipments_idx + 1, material_issue_item)
				portal_settings.menu = []
				for item in menu_items:
					portal_settings.append("menu", item)
		
		# 5. Material Request menüsünü ekle (yoksa ve /portal/material-requests route'u yoksa)
		material_request_exists = any(d.route == "/portal/material-requests" for d in portal_settings.get("menu", []))
		if not material_request_exists:
			# Material Issue'dan sonra ekle
			material_issue_idx = None
			for idx, item in enumerate(portal_settings.menu):
				if item.route == "/portal/material-issue":
					material_issue_idx = idx
					break
			
			if material_issue_idx is not None:
				portal_settings.append("menu", {
					"title": "Malzeme Talebi",
					"route": "/portal/material-requests",
					"reference_doctype": "Material Request",
					"role": "Customer",
					"enabled": 1
				})
				# Sıralamayı düzelt
				menu_items = list(portal_settings.menu)
				material_request_item = menu_items.pop()
				menu_items.insert(material_issue_idx + 1, material_request_item)
				portal_settings.menu = []
				for item in menu_items:
					portal_settings.append("menu", item)
		
		# Değişiklikleri kaydet
		portal_settings.flags.ignore_permissions = True
		portal_settings.save()
		frappe.db.commit()
		
	except Exception as e:
		frappe.log_error(
			title="Portal Settings Menu Fix Error",
			message=f"Error fixing portal menu: {str(e)}"
		)
		raise



