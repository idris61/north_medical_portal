"""
Override Frappe's and ERPNext's website permission functions to allow admin access
"""
import frappe
from north_medical_portal.utils.helpers import is_admin_user


def override_erpnext_permissions():
	"""Override Frappe's has_website_permission function to allow admin access"""
	# Store original function
	if not hasattr(frappe, '_original_has_website_permission'):
		frappe._original_has_website_permission = frappe.has_website_permission
		
		def has_website_permission_with_admin(doc=None, ptype="read", user=None, verbose=False, doctype=None):
			"""Override has_website_permission to allow admin access"""
			# Admin kullanıcılar için bypass
			if is_admin_user():
				return True
			
			# Normal kullanıcılar için orijinal fonksiyonu çağır
			return frappe._original_has_website_permission(doc, ptype, user, verbose, doctype)
		
		# Replace the function
		frappe.has_website_permission = has_website_permission_with_admin
		
		# Also override ERPNext's function
		try:
			from erpnext.controllers import website_list_for_contact
			
			if not hasattr(website_list_for_contact, '_original_has_website_permission'):
				website_list_for_contact._original_has_website_permission = website_list_for_contact.has_website_permission
				
				def erpnext_has_website_permission_with_admin(doc, ptype="read", user=None, verbose=False):
					"""Override ERPNext's has_website_permission to allow admin access"""
					# Admin kullanıcılar için bypass
					if is_admin_user():
						return True
					
					# Normal kullanıcılar için orijinal fonksiyonu çağır
					return website_list_for_contact._original_has_website_permission(doc, ptype, user, verbose)
				
				# Replace the function
				website_list_for_contact.has_website_permission = erpnext_has_website_permission_with_admin
		except ImportError:
			pass

