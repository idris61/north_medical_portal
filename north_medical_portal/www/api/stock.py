import frappe
from frappe import _
from north_medical_portal.utils.helpers import get_user_warehouses, validate_dealer_access

@frappe.whitelist()
def get_stock_status():
	"""Bayi stok durumunu döndür - Sadece kullanıcının yetkili olduğu warehouse'ları gösterir (bayi_customer field'ına göre)
	Admin kullanıcılar için tüm warehouse'ları gösterir"""
	# Permission kontrolü ve şirket doğrulama
	user_company = validate_dealer_access()
	
	# Kullanıcının yetkili olduğu warehouse'ları al (bayi_customer field'ına göre)
	warehouses = get_user_warehouses(user_company)
	
	if not warehouses:
		return {
			"company": user_company,
			"warehouses": [],
			"stock_data": []
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
	
	return {
		"company": user_company,
		"warehouses": [{"name": w.name, "warehouse_name": w.warehouse_name} for w in warehouses],
		"stock_data": stock_data
	}


