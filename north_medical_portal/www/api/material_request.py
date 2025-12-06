import frappe
from frappe import _
from frappe.utils import nowdate, add_days
from north_medical_portal.utils.helpers import get_company_warehouses, validate_dealer_access

@frappe.whitelist()
def create_material_request(items, warehouse=None):
	"""Malzeme talebi oluştur"""
	# Permission kontrolü ve şirket doğrulama
	user_company = validate_dealer_access()
	
	if not warehouse:
		warehouses = get_company_warehouses(user_company)
		if warehouses:
			warehouse = warehouses[0].name
		else:
			frappe.throw(_("Depo bulunamadı"))
	
	# Material Request oluştur
	mr = frappe.new_doc("Material Request")
	mr.material_request_type = "Material Transfer"
	mr.company = user_company
	mr.schedule_date = add_days(nowdate(), 7)
	mr.transaction_date = nowdate()
	
	# Items ekle
	if isinstance(items, str):
		import json
		items = json.loads(items)
	
	for item in items:
		mr.append("items", {
			"item_code": item.get("item_code"),
			"qty": item.get("qty", 1),
			"warehouse": warehouse,
			"schedule_date": add_days(nowdate(), 7)
		})
	
	mr.flags.ignore_permissions = True
	mr.insert()
	mr.submit()
	
	return {
		"name": mr.name,
		"status": mr.status,
		"message": _("Malzeme talebi oluşturuldu")
	}

@frappe.whitelist()
def get_material_requests():
	"""Malzeme taleplerini listele - Controller ile tutarlı"""
	# Permission kontrolü ve şirket doğrulama
	user_company = validate_dealer_access()
	
	# Şirketin tüm talepleri (controller ile tutarlı)
	material_requests = frappe.get_all(
		"Material Request",
		filters={"company": user_company},
		fields=["name", "status", "material_request_type", "schedule_date", "creation", "docstatus", "owner", "transaction_date", "set_warehouse"],
		order_by="creation desc",
		limit=100
	)
	
	# Her Material Request için hedef depo ve requested_by bilgilerini ekle
	for request in material_requests:
		# Talebi oluşturan kullanıcı bilgisi
		if request.owner:
			request.owner_name = frappe.utils.get_fullname(request.owner)
			# requested_by field'ı varsa onu kullan
			mr_doc = frappe.get_doc("Material Request", request.name)
			if hasattr(mr_doc, 'requested_by') and mr_doc.requested_by:
				request.requested_by_name = frappe.utils.get_fullname(mr_doc.requested_by)
			else:
				request.requested_by_name = request.owner_name
		
		# Hedef depo bilgisini belirle
		if request.set_warehouse:
			request.target_warehouse = request.set_warehouse
			request.target_warehouse_display = request.set_warehouse
		else:
			# Item'lardaki warehouse bilgilerini kontrol et
			items = frappe.get_all(
				"Material Request Item",
				filters={"parent": request.name},
				fields=["warehouse"]
			)
			warehouses = set()
			for item in items:
				if item.warehouse:
					warehouses.add(item.warehouse)
			
			if len(warehouses) == 1:
				# Tüm item'lar aynı depoda
				request.target_warehouse = list(warehouses)[0]
				request.target_warehouse_display = list(warehouses)[0]
			elif len(warehouses) > 1:
				# Farklı depolar var
				request.target_warehouse = None
				request.target_warehouse_display = _("Per Item")
			else:
				# Hiç depo yok
				request.target_warehouse = None
				request.target_warehouse_display = "-"
	
	return {"material_requests": material_requests}


@frappe.whitelist()
def add_material_request_to_cart(material_request_name):
	"""Material Request'teki ürünleri webshop sepetine ekle"""
	user_company = validate_dealer_access()
	
	if not material_request_name:
		frappe.throw(_("Material Request name is required"), frappe.ValidationError)
	
	# Material Request'i al
	try:
		mr = frappe.get_doc("Material Request", material_request_name)
	except frappe.DoesNotExistError:
		frappe.throw(_("Material Request not found"), frappe.DoesNotExistError)
	
	# Kullanıcının şirketine ait mi kontrol et
	if mr.company != user_company:
		frappe.throw(_("Bu Material Request'e erişim yetkiniz bulunmamaktadır"), frappe.PermissionError)
	
	# Sadece Purchase tipindeki Material Request'ler sepete eklenebilir
	if mr.material_request_type != "Purchase":
		frappe.throw(_("Sadece 'Purchase' tipindeki Material Request'ler sepete eklenebilir"))
	
	# İptal edilmiş belgeler sepete eklenemez
	if mr.docstatus == 2:
		frappe.throw(_("İptal edilmiş Material Request'ler sepete eklenemez"))
	
	# Webshop sepetine ekle
	from webshop.webshop.shopping_cart.cart import update_cart as webshop_update_cart
	from frappe.utils import flt
	
	added_items = []
	errors = []
	skipped_items = []
	
	if not mr.items:
		frappe.throw(_("Bu Material Request'te ürün bulunmamaktadır"))
	
	for item in mr.items:
		if not item.item_code:
			continue
			
		# Sadece henüz sipariş verilmemiş ürünleri ekle
		ordered_qty = flt(item.ordered_qty or 0)
		stock_qty = flt(item.stock_qty or item.qty or 0)
		
		if ordered_qty < stock_qty:
			remaining_qty = stock_qty - ordered_qty
			if remaining_qty > 0:
				try:
					# Sepete ekle
					webshop_update_cart(
						item_code=item.item_code,
						qty=remaining_qty,
						uom=item.uom or item.stock_uom
					)
					added_items.append({
						"item_code": item.item_code,
						"item_name": item.item_name or item.item_code,
						"qty": remaining_qty
					})
				except Exception as e:
					error_msg = str(e)
					errors.append({
						"item_code": item.item_code,
						"item_name": item.item_name or item.item_code,
						"error": error_msg
					})
					frappe.log_error(f"Sepete ekleme hatası - Item: {item.item_code}, Error: {error_msg}", "Add Material Request to Cart")
		else:
			skipped_items.append({
				"item_code": item.item_code,
				"item_name": item.item_name or item.item_code,
				"reason": _("Already ordered")
			})
	
	# Hiç ürün eklenemediyse hata ver
	if not added_items and errors:
		error_list = ", ".join([f"{e['item_code']}" for e in errors])
		frappe.throw(_("Ürünler sepete eklenemedi: {0}").format(error_list))
	
	if not added_items and not errors:
		frappe.throw(_("Sepete eklenecek ürün bulunamadı. Tüm ürünler zaten sipariş edilmiş olabilir."))
	
	# Mesaj oluştur
	if errors:
		message = _("{0} ürün sepete eklendi").format(len(added_items))
		if len(errors) > 0:
			message += _(", {0} ürün eklenemedi").format(len(errors))
	else:
		message = _("{0} ürün sepete eklendi").format(len(added_items))
	
	return {
		"message": message,
		"added_items": added_items,
		"errors": errors,
		"skipped_items": skipped_items,
		"cart_url": "/cart"
	}
