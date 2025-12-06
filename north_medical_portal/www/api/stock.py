import frappe
from frappe import _
from north_medical_portal.utils.helpers import get_user_warehouses, validate_dealer_access, is_admin_user
from north_medical_portal.utils.stock import check_company_reorder_levels, create_auto_material_request

@frappe.whitelist()
def get_stock_status():
	"""Bayi stok durumunu döndür - Sadece kullanıcının yetkili olduğu warehouse'ları gösterir (bayi_customer field'ına göre)
	Admin kullanıcılar için tüm warehouse'ları gösterir"""
	# Permission kontrolü ve şirket doğrulama
	user_company = validate_dealer_access()
	
	# Kullanıcının yetkili olduğu warehouse'ları al (bayi_customer field'ına göre)
	warehouses = get_user_warehouses(user_company)
	
	# Kullanıcı kendi warehouse'ları için düzenleme yapabilir
	# Her müşteri kendi deposu için düzenleme yapabilir
	can_edit_reorder = True  # Warehouse yetkisi kontrolü API'de yapılıyor
	
	if not warehouses:
		return {
			"company": user_company,
			"warehouses": [],
			"stock_data": [],
			"can_edit_reorder": can_edit_reorder
		}
	
	warehouse_names = [w.name for w in warehouses]
	
	stock_data = frappe.db.sql("""
		SELECT 
			b.item_code,
			i.item_name,
			b.warehouse,
			w.warehouse_name,
			b.actual_qty,
			ir.warehouse_reorder_level,
			ir.warehouse_reorder_qty
		FROM `tabBin` b
		INNER JOIN `tabItem` i ON i.name = b.item_code
		INNER JOIN `tabWarehouse` w ON w.name = b.warehouse
		LEFT JOIN `tabItem Reorder` ir ON ir.parent = i.name AND ir.warehouse = b.warehouse
		WHERE b.warehouse IN %(warehouses)s
			AND w.company = %(company)s
			AND (b.actual_qty > 0 OR b.projected_qty > 0)
		ORDER BY b.item_code, b.warehouse
	""", {"warehouses": warehouse_names, "company": user_company}, as_dict=True)
	
	# Her müşteri kendi deposu için düzenleme yapabilir
	# Warehouse yetkisi kontrolü API'de yapılıyor
	can_edit_reorder = True
	
	return {
		"company": user_company,
		"warehouses": [{"name": w.name, "warehouse_name": w.warehouse_name} for w in warehouses],
		"stock_data": stock_data,
		"can_edit_reorder": can_edit_reorder
	}


@frappe.whitelist()
def update_reorder_levels(item_code, warehouse, reorder_level=None, reorder_qty=None):
	"""
	Item için reorder level ve reorder quantity güncelle
	
	Args:
		item_code: Item kodu
		warehouse: Warehouse adı
		reorder_level: Min. stok seviyesi (opsiyonel)
		reorder_qty: Sipariş miktarı (opsiyonel)
	"""
	# Permission kontrolü
	user_company = validate_dealer_access()
	
	# Warehouse'un kullanıcının yetkili olduğu warehouse'lardan biri olduğunu kontrol et
	warehouses = get_user_warehouses(user_company)
	warehouse_names = [w.name for w in warehouses]
	
	if warehouse not in warehouse_names:
		frappe.throw(_("Bu depo için yetkiniz bulunmamaktadır"), frappe.PermissionError)
	
	# Item'ı al
	item = frappe.get_doc("Item", item_code)
	
	# Item Reorder kaydını bul veya oluştur
	reorder_row = None
	for row in item.get("reorder_levels", []):
		if row.warehouse == warehouse:
			reorder_row = row
			break
	
	if not reorder_row:
		# Yeni reorder row oluştur
		reorder_row = item.append("reorder_levels", {
			"warehouse": warehouse,
			"warehouse_group": warehouse,
			"material_request_type": "Purchase"
		})
	
	# Değerleri güncelle
	if reorder_level is not None:
		reorder_row.warehouse_reorder_level = float(reorder_level) if reorder_level else 0
	
	if reorder_qty is not None:
		reorder_row.warehouse_reorder_qty = float(reorder_qty) if reorder_qty else 0
	
	# Validation: Eğer reorder_level varsa reorder_qty de olmalı
	if reorder_row.warehouse_reorder_level and not reorder_row.warehouse_reorder_qty:
		frappe.throw(_("Min. stok seviyesi belirlendiğinde sipariş miktarı da belirlenmelidir"))
	
	# Permission kontrolü: Warehouse yetkisi yukarıda kontrol edildi
	# Her müşteri kendi deposu için düzenleme yapabilir
	# Item'ı kaydet (sadece reorder_levels child table'ını güncelliyoruz)
	item.flags.ignore_permissions = True  # Sadece reorder level güncellemesi için
	item.save()
	frappe.db.commit()
	
	return {
		"message": _("Stok seviyeleri güncellendi"),
		"reorder_level": reorder_row.warehouse_reorder_level,
		"reorder_qty": reorder_row.warehouse_reorder_qty
	}


@frappe.whitelist()
def search_items_for_portal(txt="", warehouse=None, page_length=20):
	"""
	Portal kullanıcıları için ürün arama - Item doctype permission olmadan
	Sadece belirtilen warehouse'daki ürünleri döndürür (warehouse belirtilmezse tüm yetkili warehouse'lar)
	"""
	user_company = validate_dealer_access()
	
	# Kullanıcının yetkili olduğu warehouse'ları al
	user_warehouses = get_user_warehouses(user_company)
	if not user_warehouses:
		return {"results": []}
	
	user_warehouse_names = [w.name for w in user_warehouses]
	
	# Warehouse belirtilmişse, sadece o warehouse'u kullan ve yetki kontrolü yap
	if warehouse:
		if warehouse not in user_warehouse_names:
			frappe.throw(_("Bu depo için yetkiniz bulunmamaktadır"), frappe.PermissionError)
		warehouse_names = [warehouse]
	else:
		# Warehouse belirtilmemişse tüm yetkili warehouse'ları kullan
		warehouse_names = user_warehouse_names
	
	# SQL ile ürünleri ara (Item doctype permission olmadan)
	# Stok durumu sayfasındaki gibi Bin'den başla - sadece Bin'de kaydı olan ürünleri göster
	# Çünkü stok durumu sayfasında görünen ürünler Bin'de kayıtlı
	
	# Arama koşulu
	search_condition = ""
	if txt:
		search_condition = """
			AND (
				i.item_code LIKE %(txt)s
				OR i.item_name LIKE %(txt)s
				OR i.description LIKE %(txt)s
			)
		"""
	
	# Tek warehouse için direkt sorgu
	if len(warehouse_names) == 1:
		# Bin'den başla - stok durumu sayfasındaki gibi
		# page_length'i integer'a çevir
		page_length_int = int(page_length) if page_length else 20
		items = frappe.db.sql("""
			SELECT DISTINCT
				b.item_code,
				i.item_name,
				COALESCE(b.actual_qty, 0) as actual_qty
			FROM `tabBin` b
			INNER JOIN `tabItem` i ON i.name = b.item_code
			WHERE b.warehouse = %(warehouse)s
				AND i.disabled = 0
				AND (b.actual_qty > 0 OR b.projected_qty > 0)
				{search_condition}
			ORDER BY i.item_code ASC
			LIMIT %(page_length)s
		""".format(search_condition=search_condition), {
			"warehouse": warehouse_names[0],
			"txt": f"%{txt}%" if txt else "%",
			"page_length": page_length_int
		}, as_dict=True)
	else:
		# Birden fazla warehouse için (warehouse belirtilmemişse)
		# page_length'i integer'a çevir
		page_length_int = int(page_length) if page_length else 20
		all_items = {}
		for wh_name in warehouse_names:
			wh_items = frappe.db.sql("""
				SELECT DISTINCT
					b.item_code,
					i.item_name,
					COALESCE(b.actual_qty, 0) as actual_qty
				FROM `tabBin` b
				INNER JOIN `tabItem` i ON i.name = b.item_code
				WHERE b.warehouse = %(warehouse)s
					AND i.disabled = 0
					AND (b.actual_qty > 0 OR b.projected_qty > 0)
					{search_condition}
				ORDER BY i.item_code ASC
				LIMIT %(page_length)s
			""".format(search_condition=search_condition), {
				"warehouse": wh_name,
				"txt": f"%{txt}%" if txt else "%",
				"page_length": page_length_int
			}, as_dict=True)
			
			for item in wh_items:
				if item.item_code not in all_items:
					all_items[item.item_code] = item
				else:
					# Aynı ürün birden fazla warehouse'da varsa, stok miktarını topla
					all_items[item.item_code].actual_qty += item.actual_qty
		
		items = list(all_items.values())
		items = sorted(items, key=lambda x: x.item_code)[:page_length]
	
	# ERPNext search_link formatına uygun formatta döndür
	results = []
	for item in items:
		results.append([
			item.item_code,
			item.item_name or item.item_code,
			f"Stock: {int(item.actual_qty)}" if item.actual_qty else "Stock: 0"
		])
	
	return {"results": results}


@frappe.whitelist()
def get_item_stock_info(item_code, warehouse):
	"""
	Belirli bir ürün için belirli bir depodaki stok bilgisini döndürür
	"""
	user_company = validate_dealer_access()
	
	# Kullanıcının yetkili olduğu warehouse'ları al
	user_warehouses = get_user_warehouses(user_company)
	if not user_warehouses:
		return {"item_name": "", "actual_qty": 0, "available_qty": 0}
	
	user_warehouse_names = [w.name for w in user_warehouses]
	
	# Warehouse yetki kontrolü
	if warehouse not in user_warehouse_names:
		frappe.throw(_("Bu depo için yetkiniz bulunmamaktadır"), frappe.PermissionError)
	
	# Item bilgilerini al (item_name, disabled, stock_uom)
	item = frappe.db.get_value("Item", item_code, ["item_name", "disabled", "stock_uom"], as_dict=True)
	if not item:
		return {"item_name": "", "actual_qty": 0, "available_qty": 0, "stock_uom": ""}
	
	# Stok bilgisini al
	bin_data = frappe.db.get_value("Bin", 
		{"item_code": item_code, "warehouse": warehouse}, 
		["actual_qty", "reserved_qty", "projected_qty"], 
		as_dict=True)
	
	if bin_data:
		actual_qty = bin_data.actual_qty or 0
		reserved_qty = bin_data.reserved_qty or 0
		available_qty = actual_qty - reserved_qty
	else:
		actual_qty = 0
		available_qty = 0
	
	return {
		"item_name": item.item_name or item_code,
		"actual_qty": actual_qty,
		"available_qty": available_qty,
		"reserved_qty": bin_data.reserved_qty if bin_data else 0,
		"stock_uom": item.stock_uom or ""
	}


@frappe.whitelist()
def trigger_reorder_check():
	"""
	Manuel olarak reorder level kontrolünü tetikle ve Material Request oluştur
	Kullanıcının şirketi için çalışır
	"""
	user_company = validate_dealer_access()
	
	try:
		# Kullanıcının şirketi için reorder level kontrolünü çalıştır
		# Önce kaç ürün bulunduğunu kontrol et
		warehouses = frappe.get_all(
			"Warehouse",
			filters={"company": user_company, "is_group": 0},
			fields=["name"]
		)
		
		if not warehouses:
			return {
				"success": False,
				"message": _("Bu şirket için depo bulunamadı")
			}
		
		warehouse_names = [w.name for w in warehouses]
		
		# Reorder level altına düşen ürünleri bul
		# actual_qty kullanıyoruz çünkü stok sayfasında da actual_qty gösteriliyor
		low_stock_items = frappe.db.sql("""
			SELECT 
				b.item_code,
				i.item_name,
				b.warehouse,
				b.actual_qty,
				b.projected_qty,
				ir.warehouse_reorder_level,
				ir.warehouse_reorder_qty,
				ir.material_request_type
			FROM `tabBin` b
			INNER JOIN `tabItem` i ON i.name = b.item_code
			INNER JOIN `tabItem Reorder` ir ON ir.parent = i.name AND ir.warehouse = b.warehouse
			WHERE b.warehouse IN %(warehouses)s
			AND ir.warehouse_reorder_level > 0
			AND b.actual_qty <= ir.warehouse_reorder_level
			AND b.actual_qty >= 0
		""", {"warehouses": warehouse_names}, as_dict=True)
		
		if not low_stock_items:
			return {
				"success": True,
				"message": _("Asgari stok seviyesi altında ürün bulunamadı"),
				"items_found": 0,
				"material_requests_created": 0
			}
		
		# Material Request oluştur
		mr_count = create_auto_material_request(user_company, low_stock_items)
		
		if mr_count > 0:
			return {
				"success": True,
				"message": _("Asgari stok kontrolü tamamlandı. {0} adet Material Request oluşturuldu.").format(mr_count),
				"items_found": len(low_stock_items),
				"material_requests_created": mr_count
			}
		else:
			return {
				"success": True,
				"message": _("Asgari stok seviyesi altında {0} ürün bulundu ancak Material Request oluşturulamadı (muhtemelen bugün için zaten oluşturulmuş).").format(len(low_stock_items)),
				"items_found": len(low_stock_items),
				"material_requests_created": 0
			}
		
	except Exception as e:
		frappe.log_error(f"Reorder check error: {str(e)}", "Trigger Reorder Check")
		return {
			"success": False,
			"message": _("Hata oluştu: {0}").format(str(e))
		}
