"""
Portal Settings'e Stok Özeti menü öğesini ekle
Bu script'i manuel olarak çalıştırabilirsiniz:
bench --site all execute north_medical_portal.setup.add_stock_summary.add_stock_summary_to_portal_settings
"""
import frappe


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
			print("✅ Stok Özeti menü öğesi Portal Settings'e eklendi")
		else:
			# Zaten varsa, enabled olduğundan emin ol
			if not existing_item[0].enabled:
				existing_item[0].enabled = 1
				portal_settings.flags.ignore_permissions = True
				portal_settings.save()
				frappe.db.commit()
				print("✅ Stok Özeti menü öğesi aktifleştirildi")
			else:
				print("ℹ️  Stok Özeti menü öğesi zaten mevcut ve aktif")
				
	except Exception as e:
		frappe.log_error(
			title="Portal Settings Setup Error",
			message=f"Error adding stock summary to portal settings: {str(e)}"
		)
		print(f"❌ Hata: {str(e)}")
		raise

