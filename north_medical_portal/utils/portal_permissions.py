"""
Portal permissions for admin users - Allow admin to access all documents
"""
import frappe
from north_medical_portal.utils.helpers import is_admin_user


def has_website_permission_for_purchase_order(doc, ptype="read", user=None, verbose=False):
	"""Purchase Order için website permission - Admin tüm belgelere erişebilir"""
	if is_admin_user():
		return True
	# Normal kullanıcılar için ERPNext'in varsayılan permission kontrolü
	from erpnext.controllers.website_list_for_contact import has_website_permission as erpnext_has_permission
	return erpnext_has_permission(doc, ptype, user, verbose)


def has_website_permission_for_purchase_invoice(doc, ptype="read", user=None, verbose=False):
	"""Purchase Invoice için website permission - Admin tüm belgelere erişebilir"""
	if is_admin_user():
		return True
	# Normal kullanıcılar için ERPNext'in varsayılan permission kontrolü
	from erpnext.controllers.website_list_for_contact import has_website_permission as erpnext_has_permission
	return erpnext_has_permission(doc, ptype, user, verbose)


def has_website_permission_for_stock_entry(doc, ptype="read", user=None, verbose=False):
	"""Stock Entry için website permission - Admin tüm belgelere erişebilir"""
	if is_admin_user():
		return True
	# Normal kullanıcılar için şirket kontrolü
	from north_medical_portal.utils.helpers import get_user_company
	user_company = get_user_company()
	if not user_company:
		return False
	return doc.company == user_company

