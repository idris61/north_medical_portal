"""
Portal Settings menüsündeki "Ürünler" gibi hardcoded Türkçe metinleri
İngilizce kaynak metinlere çevir
"""
import frappe


def fix_menu_translations():
	"""Portal Settings menüsündeki hardcoded Türkçe metinleri İngilizce'ye çevir"""
	try:
		portal_settings = frappe.get_doc("Portal Settings", "Portal Settings")
		
		# Menü öğelerindeki Türkçe metinleri İngilizce'ye çevir
		translation_map = {
			"Ürünler": "Products",
			"Stok Özeti": "Stock Summary",
			"Malzeme Çıkışı": "Material Issue",
			"Malzeme Talebi": "Material Request",
			"Talepler": "Requests",
		}
		
		changed = False
		for item in portal_settings.get("menu", []):
			if item.title in translation_map:
				item.title = translation_map[item.title]
				changed = True
		
		if changed:
			portal_settings.flags.ignore_permissions = True
			portal_settings.save()
			frappe.db.commit()
			# Clear all caches including portal menu cache
			frappe.clear_cache()
			from frappe.website.utils import clear_cache
			clear_cache()
			# Clear user-specific portal menu cache
			frappe.cache.delete_key("portal_menu_items")
		
	except Exception as e:
		frappe.log_error(
			title="Menu Translation Fix Error",
			message=f"Error fixing menu translations: {str(e)}"
		)
		raise

