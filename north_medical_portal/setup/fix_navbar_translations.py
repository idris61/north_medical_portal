"""
Website Settings navbar'ındaki "Ürünler" gibi hardcoded Türkçe metinleri
İngilizce kaynak metinlere çevir
"""
import frappe


def fix_navbar_translations():
	"""Website Settings navbar'ındaki hardcoded Türkçe metinleri İngilizce'ye çevir"""
	try:
		website_settings = frappe.get_doc("Website Settings")
		
		# Navbar öğelerindeki Türkçe metinleri İngilizce'ye çevir
		translation_map = {
			"Ürünler": "Products",
			"Ana Sayfa": "Main page",
			"Haberler": "News",
			"İletişim": "Contact",
		}
		
		changed = False
		if website_settings.top_bar_items:
			for item in website_settings.top_bar_items:
				if item.label in translation_map:
					item.label = translation_map[item.label]
					changed = True
		
		if changed:
			website_settings.flags.ignore_permissions = True
			website_settings.save()
			frappe.db.commit()
			# Clear all caches
			frappe.clear_cache()
			from frappe.website.utils import clear_cache
			clear_cache()
		
	except Exception as e:
		frappe.log_error(
			title="Navbar Translation Fix Error",
			message=f"Error fixing navbar translations: {str(e)}"
		)
		raise



