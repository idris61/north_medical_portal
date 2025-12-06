import frappe
from frappe.utils import nowdate

def check_reorder_levels():
	"""Günlük stok kontrolü - reorder level altına düşen ürünleri tespit et"""
	# Sadece bayi şirketlerini kontrol et
	companies = frappe.get_all(
		"Company",
		filters={"name": ["!=", "North Medical"]},
		fields=["name"]
	)
	
	for company in companies:
		check_company_reorder_levels(company.name)

def check_company_reorder_levels(company):
	"""Belirli bir şirket için reorder level kontrolü"""
	warehouses = frappe.get_all(
		"Warehouse",
		filters={"company": company, "is_group": 0},
		fields=["name"]
	)
	
	if not warehouses:
		return
	
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
	
	if low_stock_items:
		# Material Request oluştur
		create_auto_material_request(company, low_stock_items)

def create_auto_material_request(company, items):
	"""Otomatik Material Request oluştur
	Returns: Oluşturulan Material Request sayısı
	"""
	mr_count = 0
	
	# Material Request tipine göre grupla
	request_type_items = {}
	for item in items:
		# Item Reorder'daki material_request_type'ı kullan
		# "Transfer" -> "Material Transfer", diğerleri aynı kalır
		mr_type = item.material_request_type or "Purchase"
		if mr_type == "Transfer":
			mr_type = "Material Transfer"
		elif mr_type not in ["Purchase", "Material Transfer", "Material Issue", "Manufacture"]:
			mr_type = "Purchase"  # Varsayılan olarak Purchase
		
		if mr_type not in request_type_items:
			request_type_items[mr_type] = {}
		
		# Warehouse'a göre de grupla
		warehouse = item.warehouse
		if warehouse not in request_type_items[mr_type]:
			request_type_items[mr_type][warehouse] = []
		request_type_items[mr_type][warehouse].append(item)
	
	# Her Material Request tipi ve warehouse için ayrı MR oluştur
	for mr_type, warehouse_items in request_type_items.items():
		for warehouse, warehouse_item_list in warehouse_items.items():
			# Bugün için zaten Material Request var mı kontrol et
			existing_mr = frappe.db.exists(
				"Material Request",
				{
					"company": company,
					"material_request_type": mr_type,
					"schedule_date": nowdate(),
					"docstatus": ["<", 2]
				}
			)
			
			if existing_mr:
				continue
			
			# Material Request oluştur
			mr = frappe.new_doc("Material Request")
			mr.material_request_type = mr_type
			mr.company = company
			mr.requested_by = "Administrator"
			mr.schedule_date = nowdate()
			mr.transaction_date = nowdate()
			
			# Material Transfer ise kaynak depo belirle
			if mr_type == "Material Transfer":
				# Ana şirketin ana deposunu kaynak olarak kullan
				main_company = frappe.db.get_value("Company", {"name": ["!=", company]}, "name", order_by="creation asc")
				if main_company:
					# Ana şirketin ana deposunu bul
					main_warehouse = frappe.db.get_value(
						"Warehouse",
						{"company": main_company, "is_group": 0},
						"name",
						order_by="creation asc"
					)
					if main_warehouse:
						mr.set_from_warehouse = main_warehouse
			
			for item in warehouse_item_list:
				# actual_qty kullanıyoruz çünkü stok sayfasında da actual_qty gösteriliyor
				current_qty = item.actual_qty or 0
				reorder_qty = item.warehouse_reorder_qty or (item.warehouse_reorder_level - current_qty)
				if reorder_qty > 0:
					item_dict = {
						"item_code": item.item_code,
						"qty": reorder_qty,
						"warehouse": warehouse,
						"schedule_date": nowdate()
					}
					
					# Material Transfer ise kaynak depo da ekle
					if mr_type == "Material Transfer" and mr.set_from_warehouse:
						item_dict["from_warehouse"] = mr.set_from_warehouse
					
					mr.append("items", item_dict)
			
			if mr.items:
				try:
					mr.flags.ignore_permissions = True
					mr.insert()
					# Material Request'i Draft olarak bırak (submit etme)
					frappe.db.commit()
					mr_count += 1
				except Exception as e:
					frappe.log_error(f"Material Request oluşturma hatası: {str(e)}", "Create Auto Material Request")
					# Hata olsa bile devam et
	
	return mr_count


