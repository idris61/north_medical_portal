"""
Material Request için özel website permission kontrolü
"""
import frappe
from frappe import _
from north_medical_portal.utils.helpers import get_user_company, is_admin_user


def has_website_permission(doc, ptype="read", user=None, verbose=False):
	"""
	Material Request için website permission kontrolü
	Kullanıcının şirketine ait Material Request'lere erişim izni verir
	read ve print permission'ları için çalışır
	"""
	if not user:
		user = frappe.session.user
	
	if user == "Guest":
		return False
	
	# Admin kullanıcılar tüm Material Request'lere erişebilir
	if is_admin_user():
		return True
	
	# Kullanıcının şirketini al
	user_company = get_user_company()
	if not user_company:
		return False
	
	# Material Request'in şirketi kullanıcının şirketi ile eşleşiyor mu?
	if doc.company == user_company:
		return True
	
	return False

