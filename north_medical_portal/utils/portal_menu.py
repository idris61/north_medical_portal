"""
Portal menu utilities with language-aware caching
"""
import frappe
from frappe.model.document import Document


def get_portal_sidebar_items():
	"""
	Override get_portal_sidebar_items to include language in cache key
	This ensures menu items are re-cached when language changes
	"""
	# Get current language
	current_lang = frappe.local.lang or "en"
	
	# Create cache key with user and language
	cache_key = f"{frappe.session.user}:{current_lang}"
	sidebar_items = frappe.cache.hget("portal_menu_items", cache_key)
	
	if sidebar_items is None:
		# Build sidebar items (same logic as original function)
		sidebar_items = []
		roles = frappe.get_roles()
		portal_settings = frappe.get_doc("Portal Settings", "Portal Settings")

		def add_items(sidebar_items, items):
			# Admin kullanıcılar için tüm menüleri göster
			from north_medical_portal.utils.helpers import is_admin_user
			is_admin = is_admin_user()
			
			for d in items:
				if d.get("enabled"):
					# Admin kullanıcılar için role kontrolünü bypass et
					if is_admin or (not d.get("role")) or d.get("role") in roles:
						sidebar_items.append(d.as_dict() if isinstance(d, Document) else d)

		if not portal_settings.hide_standard_menu:
			add_items(sidebar_items, portal_settings.get("menu"))

		if portal_settings.custom_menu:
			add_items(sidebar_items, portal_settings.get("custom_menu"))

		items_via_hooks = frappe.get_hooks("portal_menu_items")
		if items_via_hooks:
			for i in items_via_hooks:
				i["enabled"] = 1
			add_items(sidebar_items, items_via_hooks)
		
		# Cache with language-aware key
		frappe.cache.hset("portal_menu_items", cache_key, sidebar_items)
	
	return sidebar_items

