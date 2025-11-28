"""
Stock Summary Print Page
"""
import frappe
from north_medical_portal.utils.helpers import validate_dealer_access, get_user_warehouses


def get_context(context):
	"""Sayfa context'ini hazırla"""
	# Permission kontrolü
	user_company = validate_dealer_access()
	
	# Kullanıcının yetkili olduğu warehouse'ları al
	warehouses = get_user_warehouses(user_company)
	
	if not warehouses:
		context.update({
			"company": user_company,
			"warehouses": [],
			"stock_data": [],
			"has_stock_data": False,
		})
		context.no_cache = 1
		context.show_sidebar = False
		return
	
	warehouse_names = [w.name for w in warehouses]
	
	# Doğrudan SQL sorgusu ile stok verilerini al (get_stock_status ile aynı mantık)
	# Not: actual_qty > 0 OR projected_qty > 0 koşulu kaldırıldı, tüm stokları göster
	stock_items = frappe.db.sql("""
		SELECT 
			b.item_code,
			i.item_name,
			b.warehouse,
			w.warehouse_name,
			b.actual_qty,
			b.projected_qty,
			ir.warehouse_reorder_level,
			ir.warehouse_reorder_qty
		FROM `tabBin` b
		INNER JOIN `tabItem` i ON i.name = b.item_code
		INNER JOIN `tabWarehouse` w ON w.name = b.warehouse
		LEFT JOIN `tabItem Reorder` ir ON ir.parent = i.name AND ir.warehouse = b.warehouse
		WHERE b.warehouse IN %(warehouses)s
			AND w.company = %(company)s
		ORDER BY b.item_code, b.warehouse
	""", {"warehouses": warehouse_names, "company": user_company}, as_dict=True)
	
	# Debug: Veri kontrolü
	frappe.log_error(
		f"Stock Summary Print - Company: {user_company}, Warehouses: {warehouse_names}, Stock Items Count: {len(stock_items)}",
		"Stock Summary Print Debug"
	)
	
	context.update({
		"company": user_company,
		"warehouses": [{"name": w.name, "warehouse_name": w.warehouse_name} for w in warehouses],
		"stock_data": stock_items if stock_items else [],
		"has_stock_data": len(stock_items) > 0,
	})
	
	context.no_cache = 1
	context.show_sidebar = False  # Print sayfasında sidebar gerekmez

