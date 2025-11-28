"""
Portal Settings'e Malzeme Çıkışı menü öğesini ekle
"""
import frappe


def add_material_issue_to_portal_settings():
	"""Portal Settings'e Malzeme Çıkışı menü öğesini ekle"""
	try:
		portal_settings = frappe.get_doc("Portal Settings", "Portal Settings")
		
		# Malzeme Çıkışı menü öğesinin zaten var olup olmadığını kontrol et
		existing_item = [d for d in portal_settings.get("menu", []) if d.get("route") == "/portal/material-issue"]
		
		if not existing_item:
			# Yeni menü öğesi ekle - Sevkiyatlar'dan sonra
			# Önce Sevkiyatlar'ın index'ini bul
			shipments_index = None
			for idx, item in enumerate(portal_settings.menu):
				if item.route == "/shipments":
					shipments_index = idx
					break
			
			# Menü öğesini ekle
			portal_settings.append("menu", {
				"title": "Malzeme Çıkışı",
				"route": "/portal/material-issue",
				"reference_doctype": None,
				"role": "Customer",
				"enabled": 1
			})
			
			# Eğer Sevkiyatlar bulunduysa, sıralamayı düzelt
			if shipments_index is not None:
				# Menü öğelerini yeniden sırala
				menu_items = list(portal_settings.menu)
				# Son eklenen öğeyi (Malzeme Çıkışı) bul
				material_issue_item = menu_items[-1]
				# Kaldır
				menu_items.pop()
				# Sevkiyatlar'dan sonra ekle
				menu_items.insert(shipments_index + 1, material_issue_item)
				# Menüyü yeniden set et
				portal_settings.menu = []
				for item in menu_items:
					portal_settings.append("menu", item)
			
			portal_settings.flags.ignore_permissions = True
			portal_settings.save()
			frappe.db.commit()
		else:
			# Zaten varsa, enabled olduğundan emin ol
			if not existing_item[0].enabled:
				existing_item[0].enabled = 1
				portal_settings.flags.ignore_permissions = True
				portal_settings.save()
				frappe.db.commit()
				
	except Exception as e:
		frappe.log_error(
			title="Portal Settings Setup Error",
			message=f"Error adding material issue to portal settings: {str(e)}"
		)
		raise

