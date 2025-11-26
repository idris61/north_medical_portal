"""
Ortak helper fonksiyonlar - Tüm portal sayfaları ve API'ler için
"""
import frappe
from frappe import _


def get_user_company():
	"""
	Kullanıcının bağlı olduğu şirketi döndür
	
	Öncelik sırası:
	1. User'ın company field'ı
	2. User'ın role'üne göre şirket
	3. İlk bayi şirketi (geçici çözüm)
	
	Returns:
		str: Şirket adı veya None
	"""
	user = frappe.session.user
	
	if user == "Guest":
		return None
	
	# 1. User'ın company field'ını kontrol et
	user_doc = frappe.get_doc("User", user)
	if hasattr(user_doc, "company") and user_doc.company:
		# Company'nin North Medical olmadığından emin ol
		if user_doc.company != "North Medical":
			return user_doc.company
	
	# 2. User'ın role'lerine göre şirket bul
	user_roles = frappe.get_roles(user)
	
	# Role'lerde şirket adı geçiyorsa (örn: "Dealer Manager - Bayi 1")
	for role in user_roles:
		if " - " in role:
			company_name = role.split(" - ")[-1]
			company_exists = frappe.db.exists("Company", company_name)
			if company_exists and company_name != "North Medical":
				return company_name
	
	# 3. User'ın bağlı olduğu Company'yi bul (geçici çözüm)
	# TODO: User-Company ilişkisi düzgün kurulduğunda bu kısım kaldırılacak
	companies = frappe.get_all(
		"Company",
		filters={"name": ["!=", "North Medical"]},
		fields=["name", "company_name"],
		order_by="creation asc"
	)
	
	if companies:
		# İlk bayi şirketini döndür (şimdilik)
		return companies[0].name
	
	return None


def get_company_warehouses(company):
	"""
	Şirketin warehouse'larını döndür
	
	Args:
		company (str): Şirket adı
		
	Returns:
		list: Warehouse listesi
	"""
	if not company:
		return []
	
	return frappe.get_all(
		"Warehouse",
		filters={"company": company, "is_group": 0},
		fields=["name", "warehouse_name"],
		order_by="warehouse_name asc"
	)


def get_user_customer():
	"""
	Kullanıcının bağlı olduğu Customer'ı döndür
	
	Öncelik sırası:
	1. Customer dokümanındaki Portal Users tablosundan (daha doğrudan)
	2. Contact üzerinden Customer link'i (fallback)
	
	Returns:
		str: Customer adı veya None
	"""
	user = frappe.session.user
	
	if user == "Guest":
		return None
	
	# 1. Önce Portal Users tablosundan kontrol et
	portal_user_parent = frappe.db.get_value(
		"Portal User",
		{"user": user},
		"parent",
		as_dict=False
	)
	
	if portal_user_parent:
		# Parent'ın Customer olup olmadığını kontrol et
		if frappe.db.exists("Customer", portal_user_parent):
			return portal_user_parent
	
	# 2. Contact üzerinden Customer'ı bul (fallback)
	from frappe.contacts.doctype.contact.contact import get_contact_name
	contact_name = get_contact_name(user)
	
	if contact_name:
		contact = frappe.get_doc("Contact", contact_name)
		for link in contact.links:
			if link.link_doctype == "Customer":
				return link.link_name
	
	return None


def get_user_warehouses(company):
	"""
	Kullanıcının yetkili olduğu warehouse'ları döndür
	Warehouse'daki "bayi_customer" field'ına göre filtreler
	
	Args:
		company (str): Şirket adı
		
	Returns:
		list: Kullanıcının yetkili olduğu warehouse listesi
	"""
	if not company:
		return []
	
	# Kullanıcının customer'ını bul
	user_customer = get_user_customer()
	
	if not user_customer:
		# Customer bulunamazsa boş liste döndür
		return []
	
	# Warehouse'ları bayi_customer field'ına göre filtrele
	warehouses = frappe.get_all(
		"Warehouse",
		filters={
			"company": company,
			"is_group": 0,
			"bayi_customer": user_customer
		},
		fields=["name", "warehouse_name"],
		order_by="warehouse_name asc"
	)
	
	return warehouses


def validate_dealer_access(company=None):
	"""
	Kullanıcının bayi erişim yetkisini kontrol et
	
	Args:
		company (str, optional): Kontrol edilecek şirket
		
	Returns:
		bool: Erişim yetkisi var mı
		
	Raises:
		frappe.PermissionError: Erişim yetkisi yoksa
	"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Lütfen giriş yapın"), frappe.PermissionError)
	
	user_company = get_user_company()
	if not user_company:
		frappe.throw(_("Şirket bilgisi bulunamadı"), frappe.PermissionError)
	
	# Eğer belirli bir şirket kontrol ediliyorsa
	if company and company != user_company:
		frappe.throw(_("Bu şirkete erişim yetkiniz yok"), frappe.PermissionError)
	
	return user_company

