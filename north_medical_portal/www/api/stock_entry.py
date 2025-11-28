"""
Stock Entry API - Malzeme alım/çıkış işlemleri
"""
import frappe
from frappe import _
from frappe.utils import nowdate
from north_medical_portal.utils.helpers import validate_dealer_access, get_company_warehouses, get_user_warehouses


@frappe.whitelist()
def create_stock_entry(entry_type, items, warehouse=None, remarks=None):
	"""
	Stock Entry oluştur (Material Receipt veya Material Issue)
	
	Args:
		entry_type: "Material Receipt" veya "Material Issue"
		items: [{"item_code": "...", "qty": 10}, ...]
		warehouse: Depo adı (Material Receipt için to_warehouse, Material Issue için from_warehouse)
		remarks: Notlar
	"""
	user_company = validate_dealer_access()
	
	if entry_type not in ["Material Receipt", "Material Issue"]:
		frappe.throw(_("Geçersiz entry type. 'Material Receipt' veya 'Material Issue' olmalı"))
	
	# Warehouse kontrolü
	if not warehouse:
		warehouses = get_company_warehouses(user_company)
		if warehouses:
			warehouse = warehouses[0].name
		else:
			frappe.throw(_("Depo bulunamadı"))
	
	# Warehouse'un şirkete ait olduğunu kontrol et
	wh_doc = frappe.get_doc("Warehouse", warehouse)
	if wh_doc.company != user_company:
		frappe.throw(_("Bu depo sizin şirketinize ait değil"))
	
	# Stock Entry oluştur
	stock_entry = frappe.new_doc("Stock Entry")
	stock_entry.stock_entry_type = entry_type
	stock_entry.purpose = entry_type
	stock_entry.company = user_company
	stock_entry.posting_date = nowdate()
	
	if entry_type == "Material Receipt":
		stock_entry.to_warehouse = warehouse
	else:  # Material Issue
		stock_entry.from_warehouse = warehouse
	
	if remarks:
		stock_entry.remarks = remarks
	
	# Items ekle
	if isinstance(items, str):
		import json
		items = json.loads(items)
	
	for item in items:
		item_code = item.get("item_code")
		qty = item.get("qty", 0)
		
		if not item_code or qty <= 0:
			continue
		
		item_row = {
			"item_code": item_code,
			"qty": qty,
		}
		
		if entry_type == "Material Receipt":
			item_row["t_warehouse"] = warehouse
		else:  # Material Issue
			item_row["s_warehouse"] = warehouse
		
		stock_entry.append("items", item_row)
	
	if not stock_entry.items:
		frappe.throw(_("En az bir ürün eklenmelidir"))
	
	stock_entry.flags.ignore_permissions = True
	stock_entry.insert()
	stock_entry.submit()
	
	return {
		"name": stock_entry.name,
		"status": "Submitted",
		"message": _("Stok hareketi oluşturuldu")
	}


@frappe.whitelist()
def get_stock_entries(entry_type=None):
	"""Stok hareketlerini listele"""
	user_company = validate_dealer_access()
	
	# SQL sorgusu ile warehouse isimlerini ve items preview'ını al
	if entry_type:
		stock_entries = frappe.db.sql("""
			SELECT 
				se.name,
				se.stock_entry_type,
				se.purpose,
				se.posting_date,
				se.docstatus,
				se.creation,
				se.remarks,
				se.from_warehouse,
				se.to_warehouse,
				COALESCE(w_from.warehouse_name, w_to.warehouse_name, se.from_warehouse, se.to_warehouse, '-') as warehouse_display,
				GROUP_CONCAT(DISTINCT sed.item_name ORDER BY sed.idx SEPARATOR ', ') as items_preview
			FROM `tabStock Entry` se
			LEFT JOIN `tabWarehouse` w_from ON w_from.name = se.from_warehouse
			LEFT JOIN `tabWarehouse` w_to ON w_to.name = se.to_warehouse
			LEFT JOIN `tabStock Entry Detail` sed ON sed.parent = se.name
			WHERE se.company = %(company)s
				AND se.stock_entry_type = %(entry_type)s
			GROUP BY se.name
			ORDER BY se.posting_date DESC, se.creation DESC
			LIMIT 100
		""", {"company": user_company, "entry_type": entry_type}, as_dict=True)
	else:
		stock_entries = frappe.db.sql("""
			SELECT 
				se.name,
				se.stock_entry_type,
				se.purpose,
				se.posting_date,
				se.docstatus,
				se.creation,
				se.remarks,
				se.from_warehouse,
				se.to_warehouse,
				COALESCE(w_from.warehouse_name, w_to.warehouse_name, se.from_warehouse, se.to_warehouse, '-') as warehouse_display,
				GROUP_CONCAT(DISTINCT sed.item_name ORDER BY sed.idx SEPARATOR ', ') as items_preview
			FROM `tabStock Entry` se
			LEFT JOIN `tabWarehouse` w_from ON w_from.name = se.from_warehouse
			LEFT JOIN `tabWarehouse` w_to ON w_to.name = se.to_warehouse
			LEFT JOIN `tabStock Entry Detail` sed ON sed.parent = se.name
			WHERE se.company = %(company)s
			GROUP BY se.name
			ORDER BY se.posting_date DESC, se.creation DESC
			LIMIT 100
		""", {"company": user_company}, as_dict=True)
	
	return {"stock_entries": stock_entries}


@frappe.whitelist()
def create_material_issue(warehouse, items, posting_date=None, remarks=None):
	"""
	Malzeme çıkışı oluştur - Bayilerin kendi warehouse'larından malzeme çıkışı
	
	Args:
		warehouse: Depo adı
		items: [{"item_code": "...", "qty": 10}, ...]
		posting_date: İşlem tarihi (opsiyonel, varsayılan: bugün)
		remarks: Notlar
	"""
	user_company = validate_dealer_access()
	
	# Kullanıcının yetkili olduğu warehouse'ları kontrol et
	user_warehouses = get_user_warehouses(user_company)
	warehouse_names = [w.name for w in user_warehouses]
	
	if warehouse not in warehouse_names:
		frappe.throw(_("Bu depo için yetkiniz bulunmamaktadır"))
	
	# Warehouse dokümanını al
	wh_doc = frappe.get_doc("Warehouse", warehouse)
	if wh_doc.company != user_company:
		frappe.throw(_("Bu depo sizin şirketinize ait değil"))
	
	# Items parse et
	if isinstance(items, str):
		import json
		items = json.loads(items)
	
	if not items or len(items) == 0:
		frappe.throw(_("En az bir ürün eklenmelidir"))
	
	# Her ürün için stok kontrolü yap
	for item in items:
		item_code = item.get("item_code")
		qty = float(item.get("qty", 0))
		
		if not item_code or qty <= 0:
			frappe.throw(_("Geçersiz ürün veya miktar"))
		
		# Mevcut stoku kontrol et
		bin_data = frappe.db.get_value(
			"Bin",
			{"item_code": item_code, "warehouse": warehouse},
			["actual_qty", "projected_qty"],
			as_dict=True
		)
		
		if not bin_data:
			frappe.throw(_("{0} ürünü için {1} deposunda stok bulunmamaktadır").format(item_code, warehouse))
		
		available_qty = bin_data.actual_qty or 0
		if qty > available_qty:
			frappe.throw(_("{0} ürünü için yeterli stok yok. Mevcut: {1}, İstenen: {2}").format(
				item_code, available_qty, qty
			))
	
	# Stock Entry oluştur
	stock_entry = frappe.new_doc("Stock Entry")
	stock_entry.stock_entry_type = "Material Issue"
	stock_entry.purpose = "Material Issue"
	stock_entry.company = user_company
	stock_entry.posting_date = posting_date if posting_date else nowdate()
	stock_entry.from_warehouse = warehouse
	
	if remarks:
		stock_entry.remarks = remarks
	
	# Items ekle
	for item in items:
		item_code = item.get("item_code")
		qty = float(item.get("qty", 0))
		
		# Item dokümanından UOM al
		item_doc = frappe.get_doc("Item", item_code)
		
		stock_entry.append("items", {
			"item_code": item_code,
			"s_warehouse": warehouse,
			"qty": qty,
			"uom": item_doc.stock_uom,
			"conversion_factor": 1
		})
	
	# Warehouse account'ını kontrol et ve grup hesap ise alt hesabı bul
	warehouse_account = wh_doc.account
	account_changed = False
	original_account = None
	
	if warehouse_account:
		account_is_group = frappe.db.get_value("Account", warehouse_account, "is_group")
		if account_is_group:
			# Alt hesap bul - önce direkt child'ı kontrol et
			child_account = frappe.db.get_value(
				"Account",
				{"parent_account": warehouse_account, "is_group": 0, "company": user_company},
				"name",
				order_by="name asc"
			)
			
			# Eğer direkt child yoksa, recursive olarak alt hesap bul
			if not child_account:
				def find_child_account(account_name):
					children = frappe.get_all(
						"Account",
						filters={"parent_account": account_name, "company": user_company},
						fields=["name", "is_group"],
						order_by="name asc"
					)
					for child in children:
						if not child.is_group:
							return child.name
						else:
							# Recursive olarak alt hesap ara
							result = find_child_account(child.name)
							if result:
								return result
					return None
				
				child_account = find_child_account(warehouse_account)
			
			if child_account:
				# Warehouse'ın account'ını geçici olarak güncelle
				original_account = warehouse_account
				wh_doc.account = child_account
				wh_doc.flags.ignore_permissions = True
				wh_doc.save()
				frappe.db.commit()
				account_changed = True
				
				# Warehouse account map cache'ini temizle
				if hasattr(frappe.flags, 'warehouse_account_map') and frappe.flags.warehouse_account_map:
					if isinstance(frappe.flags.warehouse_account_map, dict):
						if user_company in frappe.flags.warehouse_account_map:
							if isinstance(frappe.flags.warehouse_account_map[user_company], dict):
								if warehouse in frappe.flags.warehouse_account_map[user_company]:
									del frappe.flags.warehouse_account_map[user_company][warehouse]
					# Tüm cache'i temizle
					frappe.flags.warehouse_account_map = {}
			else:
				frappe.throw(_("Warehouse {0} için grup hesap {1} altında grup olmayan bir hesap bulunamadı").format(
					warehouse, warehouse_account
				))
	
	# Stock Entry'yi kaydet ve submit et
	stock_entry.flags.ignore_permissions = True
	stock_entry.insert()
	
	try:
		stock_entry.submit()
	finally:
		# Submit sonrası warehouse account'ını geri al (başarılı veya başarısız olsun)
		if account_changed and original_account:
			wh_doc.account = original_account
			wh_doc.flags.ignore_permissions = True
			wh_doc.save()
			frappe.db.commit()
			
			# Cache'i tekrar temizle
			if hasattr(frappe.flags, 'warehouse_account_map') and frappe.flags.warehouse_account_map:
				if isinstance(frappe.flags.warehouse_account_map, dict):
					if user_company in frappe.flags.warehouse_account_map:
						if isinstance(frappe.flags.warehouse_account_map[user_company], dict):
							if warehouse in frappe.flags.warehouse_account_map[user_company]:
								del frappe.flags.warehouse_account_map[user_company][warehouse]
					frappe.flags.warehouse_account_map = {}
	
	return {
		"name": stock_entry.name,
		"status": "Submitted",
		"message": _("Malzeme çıkışı başarıyla oluşturuldu ve stoktan düşüldü")
	}


@frappe.whitelist()
def get_stock_entry_for_edit(stock_entry_name):
	"""
	Belgeyi düzenleme için getir
	
	Args:
		stock_entry_name: Stock Entry adı
	"""
	user_company = validate_dealer_access()
	
	# Belgeyi al
	stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)
	
	# Şirket kontrolü
	if stock_entry.company != user_company:
		frappe.throw(_("Bu belgeye erişim yetkiniz yok"))
	
	# Sadece draft belgeler düzenlenebilir
	if stock_entry.docstatus != 0:
		frappe.throw(_("Sadece taslak belgeler düzenlenebilir"))
	
	# Items'ı formatla
	items = []
	for item in stock_entry.items:
		items.append({
			"item_code": item.item_code,
			"item_name": item.item_name,
			"qty": item.qty,
			"uom": item.uom,
			"available_qty": None  # Client-side'da güncellenecek
		})
	
	return {
		"name": stock_entry.name,
		"warehouse": stock_entry.from_warehouse or stock_entry.to_warehouse,
		"posting_date": stock_entry.posting_date,
		"remarks": stock_entry.remarks,
		"items": items
	}


@frappe.whitelist()
def update_stock_entry(stock_entry_name, warehouse, items, posting_date=None, remarks=None):
	"""
	Stock Entry'yi güncelle
	
	Args:
		stock_entry_name: Stock Entry adı
		warehouse: Depo adı
		items: [{"item_code": "...", "qty": 10}, ...]
		posting_date: İşlem tarihi
		remarks: Notlar
	"""
	user_company = validate_dealer_access()
	
	# Belgeyi al
	stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)
	
	# Şirket kontrolü
	if stock_entry.company != user_company:
		frappe.throw(_("Bu belgeye erişim yetkiniz yok"))
	
	# Sadece draft belgeler güncellenebilir
	if stock_entry.docstatus != 0:
		frappe.throw(_("Sadece taslak belgeler güncellenebilir"))
	
	# Warehouse kontrolü
	user_warehouses = get_user_warehouses(user_company)
	warehouse_names = [w.name for w in user_warehouses]
	
	if warehouse not in warehouse_names:
		frappe.throw(_("Bu depo için yetkiniz bulunmamaktadır"))
	
	# Warehouse dokümanını al
	wh_doc = frappe.get_doc("Warehouse", warehouse)
	if wh_doc.company != user_company:
		frappe.throw(_("Bu depo sizin şirketinize ait değil"))
	
	# Items parse et
	if isinstance(items, str):
		import json
		items = json.loads(items)
	
	if not items or len(items) == 0:
		frappe.throw(_("En az bir ürün eklenmelidir"))
	
	# Her ürün için stok kontrolü yap (Material Issue için)
	if stock_entry.stock_entry_type == "Material Issue":
		for item in items:
			item_code = item.get("item_code")
			qty = float(item.get("qty", 0))
			
			if not item_code or qty <= 0:
				frappe.throw(_("Geçersiz ürün veya miktar"))
			
			# Mevcut stoku kontrol et
			bin_data = frappe.db.get_value(
				"Bin",
				{"item_code": item_code, "warehouse": warehouse},
				["actual_qty", "projected_qty"],
				as_dict=True
			)
			
			if not bin_data:
				frappe.throw(_("{0} ürünü için {1} deposunda stok bulunmamaktadır").format(item_code, warehouse))
			
			available_qty = bin_data.actual_qty or 0
			if qty > available_qty:
				frappe.throw(_("{0} ürünü için yeterli stok yok. Mevcut: {1}, İstenen: {2}").format(
					item_code, available_qty, qty
				))
	
	# Belgeyi güncelle
	stock_entry.from_warehouse = warehouse if stock_entry.stock_entry_type == "Material Issue" else None
	stock_entry.to_warehouse = warehouse if stock_entry.stock_entry_type == "Material Receipt" else None
	
	if posting_date:
		stock_entry.posting_date = posting_date
	
	if remarks is not None:
		stock_entry.remarks = remarks
	
	# Mevcut items'ı temizle
	stock_entry.items = []
	
	# Yeni items'ı ekle
	for item in items:
		item_code = item.get("item_code")
		qty = float(item.get("qty", 0))
		
		if not item_code or qty <= 0:
			continue
		
		# Item dokümanından UOM al
		item_doc = frappe.get_doc("Item", item_code)
		
		item_row = {
			"item_code": item_code,
			"qty": qty,
			"uom": item_doc.stock_uom,
			"conversion_factor": 1
		}
		
		if stock_entry.stock_entry_type == "Material Issue":
			item_row["s_warehouse"] = warehouse
		else:  # Material Receipt
			item_row["t_warehouse"] = warehouse
		
		stock_entry.append("items", item_row)
	
	if not stock_entry.items:
		frappe.throw(_("En az bir ürün eklenmelidir"))
	
	# Warehouse account'ını kontrol et ve grup hesap ise alt hesabı bul (Material Issue için)
	account_changed = False
	original_account = None
	
	if stock_entry.stock_entry_type == "Material Issue" and wh_doc.account:
		account_is_group = frappe.db.get_value("Account", wh_doc.account, "is_group")
		if account_is_group:
			# Alt hesap bul - önce direkt child'ı kontrol et
			child_account = frappe.db.get_value(
				"Account",
				{"parent_account": wh_doc.account, "is_group": 0, "company": user_company},
				"name",
				order_by="name asc"
			)
			
			# Eğer direkt child yoksa, recursive olarak alt hesap bul
			if not child_account:
				def find_child_account(account_name):
					children = frappe.get_all(
						"Account",
						filters={"parent_account": account_name, "company": user_company},
						fields=["name", "is_group"],
						order_by="name asc"
					)
					for child in children:
						if not child.is_group:
							return child.name
						else:
							# Recursive olarak alt hesap ara
							result = find_child_account(child.name)
							if result:
								return result
					return None
				
				child_account = find_child_account(wh_doc.account)
			
			if child_account:
				# Warehouse'ın account'ını geçici olarak güncelle
				original_account = wh_doc.account
				wh_doc.account = child_account
				wh_doc.flags.ignore_permissions = True
				wh_doc.save()
				frappe.db.commit()
				account_changed = True
				
				# Warehouse account map cache'ini temizle
				if hasattr(frappe.flags, 'warehouse_account_map') and frappe.flags.warehouse_account_map:
					if isinstance(frappe.flags.warehouse_account_map, dict):
						if user_company in frappe.flags.warehouse_account_map:
							if isinstance(frappe.flags.warehouse_account_map[user_company], dict):
								if warehouse in frappe.flags.warehouse_account_map[user_company]:
									del frappe.flags.warehouse_account_map[user_company][warehouse]
					# Tüm cache'i temizle
					frappe.flags.warehouse_account_map = {}
	
	# Belgeyi kaydet ve submit et
	stock_entry.flags.ignore_permissions = True
	stock_entry.save()
	
	try:
		stock_entry.submit()
	finally:
		# Submit sonrası warehouse account'ını geri al (başarılı veya başarısız olsun)
		if account_changed and original_account:
			wh_doc.account = original_account
			wh_doc.flags.ignore_permissions = True
			wh_doc.save()
			frappe.db.commit()
			
			# Cache'i tekrar temizle
			if hasattr(frappe.flags, 'warehouse_account_map') and frappe.flags.warehouse_account_map:
				if isinstance(frappe.flags.warehouse_account_map, dict):
					if user_company in frappe.flags.warehouse_account_map:
						if isinstance(frappe.flags.warehouse_account_map[user_company], dict):
							if warehouse in frappe.flags.warehouse_account_map[user_company]:
								del frappe.flags.warehouse_account_map[user_company][warehouse]
					frappe.flags.warehouse_account_map = {}
	
	return {
		"name": stock_entry.name,
		"status": "Submitted",
		"message": _("Belge başarıyla güncellendi ve onaylandı")
	}


@frappe.whitelist()
def cancel_stock_entry(stock_entry_name):
	"""
	Stock Entry'yi iptal et
	
	Args:
		stock_entry_name: Stock Entry adı
	"""
	user_company = validate_dealer_access()
	
	# Belgeyi al
	stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)
	
	# Şirket kontrolü
	if stock_entry.company != user_company:
		frappe.throw(_("Bu belgeye erişim yetkiniz yok"))
	
	# Sadece submitted belgeler iptal edilebilir
	if stock_entry.docstatus != 1:
		frappe.throw(_("Sadece onaylanmış belgeler iptal edilebilir"))
	
	# Belgeyi iptal et
	stock_entry.flags.ignore_permissions = True
	stock_entry.cancel()
	
	return {
		"name": stock_entry.name,
		"status": "Cancelled",
		"message": _("Belge başarıyla iptal edildi")
	}


@frappe.whitelist()
def delete_stock_entry(stock_entry_name):
	"""
	Stock Entry'yi sil (draft veya iptal edilmiş belgeler)
	
	Args:
		stock_entry_name: Stock Entry adı
	"""
	user_company = validate_dealer_access()
	
	# Belgeyi al
	stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)
	
	# Şirket kontrolü
	if stock_entry.company != user_company:
		frappe.throw(_("Bu belgeye erişim yetkiniz yok"))
	
	# Sadece draft veya iptal edilmiş belgeler silinebilir
	if stock_entry.docstatus not in [0, 2]:
		frappe.throw(_("Sadece taslak veya iptal edilmiş belgeler silinebilir"))
	
	# Belgeyi sil
	stock_entry.flags.ignore_permissions = True
	stock_entry.delete()
	
	return {
		"message": _("Belge başarıyla silindi")
	}


@frappe.whitelist()
def amend_stock_entry(stock_entry_name):
	"""
	İptal edilmiş Stock Entry'yi düzelt (durumunu draft'a çevir)
	
	Args:
		stock_entry_name: İptal edilmiş Stock Entry adı
	"""
	user_company = validate_dealer_access()
	
	# Belgeyi al
	stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)
	
	# Şirket kontrolü
	if stock_entry.company != user_company:
		frappe.throw(_("Bu belgeye erişim yetkiniz yok"))
	
	# Sadece iptal edilmiş belgeler düzeltilebilir
	if stock_entry.docstatus != 2:
		frappe.throw(_("Sadece iptal edilmiş belgeler düzeltilebilir"))
	
	# Belgeyi draft'a çevir (docstatus'u 0 yap)
	# SQL ile direkt güncelleme yapıyoruz
	frappe.db.set_value("Stock Entry", stock_entry_name, "docstatus", 0, update_modified=False)
	frappe.db.commit()
	
	# Belgeyi reload et
	stock_entry.reload()
	
	return {
		"name": stock_entry.name,
		"status": "Draft",
		"message": _("Belge başarıyla düzeltildi ve düzenlenebilir hale getirildi")
	}




