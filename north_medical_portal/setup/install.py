"""
North Medical Portal - Installation Setup
Custom field'lar fixture'lardan otomatik yüklenir
Özel yapılandırmalar burada yapılır
"""
import frappe
from north_medical_portal.utils.add_portal_navbar import add_portal_links_to_navbar


def add_stock_summary_to_portal_settings():
	"""Portal Settings'e Stok Özeti menü öğesini ekle"""
	try:
		portal_settings = frappe.get_doc("Portal Settings", "Portal Settings")
		
		# Stok Özeti menü öğesinin zaten var olup olmadığını kontrol et
		existing_item = [d for d in portal_settings.get("menu", []) if d.get("route") == "/portal/stock"]
		
		if not existing_item:
			# Yeni menü öğesi ekle
			portal_settings.append("menu", {
				"title": "Stok Özeti",
				"route": "/portal/stock",
				"reference_doctype": None,
				"role": "Customer",
				"enabled": 1
			})
			portal_settings.flags.ignore_permissions = True
			portal_settings.save()
			frappe.db.commit()
			frappe.msgprint("Stok Özeti menü öğesi Portal Settings'e eklendi")
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
			message=f"Error adding stock summary to portal settings: {str(e)}"
		)


def after_install():
	"""App kurulumundan sonra çalışır"""
	# Custom field'lar fixture'lardan otomatik yüklenir
	# Portal sayfalarını navbar'a ekle
	try:
		add_portal_links_to_navbar()
	except Exception as e:
		frappe.log_error(
			title="Portal Navbar Setup Error",
			message=f"Error adding portal links to navbar: {str(e)}"
		)
	
	# Portal Settings'e Stok Özeti menü öğesini ekle ve menüyü düzenle
	try:
		add_stock_summary_to_portal_settings()
		# Malzeme Çıkışı menü öğesini ekle
		from north_medical_portal.setup.add_material_issue_menu import add_material_issue_to_portal_settings
		add_material_issue_to_portal_settings()
		# Menüyü düzenle (duplicate kaldır, sıralama, Issues -> Talepler)
		from north_medical_portal.setup.fix_portal_menu import fix_portal_menu
		fix_portal_menu()
	except Exception as e:
		frappe.log_error(
			title="Portal Settings Setup Error",
			message=f"Error setting up portal menu: {str(e)}"
		)
	
	frappe.db.commit()

