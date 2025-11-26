"""
Sales Order için Material Request güncelleme işlemleri
"""
import frappe
from frappe import _
from frappe.utils import flt


def update_material_request_from_sales_order(sales_order, method=None):
	"""
	Sales Order submit edildiğinde, Material Request'lerin durumunu güncelle
	
	Material Request'ten sepete eklenen ürünler için:
	- Material Request'in ordered_qty'sini güncelle
	- Material Request'in durumunu güncelle (Pending -> Partially Ordered -> Ordered)
	"""
	if not sales_order or sales_order.docstatus != 1:
		return
	
	# Sales Order'daki item'ları Material Request'lerle eşleştir
	# Material Request'ten sepete eklenen ürünler için Material Request'i bul
	material_requests_to_update = {}
	
	for so_item in sales_order.items:
		# Bu item'ın hangi Material Request'ten geldiğini bul
		# Material Request Item'larında bu item_code ve qty'yi ara
		item_qty = flt(so_item.stock_qty or so_item.qty)
		
		mr_items = frappe.db.sql("""
			SELECT 
				mr.name as material_request,
				mri.name as material_request_item,
				mri.item_code,
				mri.stock_qty,
				mri.ordered_qty,
				mr.material_request_type,
				mr.status
			FROM `tabMaterial Request Item` mri
			INNER JOIN `tabMaterial Request` mr ON mri.parent = mr.name
			WHERE 
				mr.material_request_type = 'Purchase'
				AND mr.docstatus = 1
				AND mri.item_code = %(item_code)s
				AND CAST(mri.stock_qty AS DECIMAL(18,6)) > CAST(COALESCE(mri.ordered_qty, 0) AS DECIMAL(18,6))
				AND mr.company = %(company)s
			ORDER BY mr.creation DESC
		""", {
			"item_code": so_item.item_code,
			"company": sales_order.company
		}, as_dict=True)
		
		if not mr_items:
			continue
		
		# Sales Order'daki qty'yi Material Request Item'lara dağıt
		remaining_qty = flt(so_item.stock_qty or so_item.qty)
		
		# Debug: Bulunan Material Request'leri göster
		frappe.log_error(
			title=f"MR Update Debug: {so_item.item_code}",
			message=f"Found {len(mr_items)} MR items for {so_item.item_code}, remaining_qty={remaining_qty}"
		)
		
		for mr_item in mr_items:
			if remaining_qty <= 0:
				break
			
			mr_name = mr_item.material_request
			mri_name = mr_item.material_request_item
			
			if mr_name not in material_requests_to_update:
				material_requests_to_update[mr_name] = {}
			
			if mri_name not in material_requests_to_update[mr_name]:
				material_requests_to_update[mr_name][mri_name] = {
					"current_ordered_qty": flt(mr_item.ordered_qty),
					"stock_qty": flt(mr_item.stock_qty),
					"to_add_qty": 0
				}
			
			# Ne kadar qty ekleyeceğimizi hesapla
			available_qty = flt(mr_item.stock_qty) - flt(mr_item.ordered_qty)
			qty_to_add = min(remaining_qty, available_qty)
			
			material_requests_to_update[mr_name][mri_name]["to_add_qty"] += qty_to_add
			remaining_qty -= qty_to_add
	
	# Material Request'leri güncelle
	if not material_requests_to_update:
		return
	
	for mr_name, mr_items_dict in material_requests_to_update.items():
		try:
			# Material Request Item'larını direkt database'de güncelle (submit edilmiş dokümanlar için)
			for mri_name, mri_data in mr_items_dict.items():
				new_ordered_qty = flt(mri_data["current_ordered_qty"]) + flt(mri_data["to_add_qty"])
				frappe.db.set_value("Material Request Item", mri_name, "ordered_qty", new_ordered_qty)
			
			# Material Request'in per_ordered alanını güncelle ve durumunu hesapla
			# Database'den direkt oku
			items_data = frappe.db.sql("""
				SELECT SUM(stock_qty) as total_stock, SUM(ordered_qty) as total_ordered
				FROM `tabMaterial Request Item`
				WHERE parent = %s
			""", mr_name, as_dict=True)
			
			if items_data and items_data[0].total_stock:
				total_ordered = flt(items_data[0].total_ordered or 0)
				total_stock = flt(items_data[0].total_stock)
				per_ordered = (total_ordered / total_stock * 100) if total_stock > 0 else 0
				
				frappe.db.set_value("Material Request", mr_name, "per_ordered", per_ordered)
				
				# Durumu güncelle
				mr_doc = frappe.get_doc("Material Request", mr_name)
				mr_doc.reload()
				mr_doc.set_status(update=True)
				frappe.db.set_value("Material Request", mr_name, "status", mr_doc.status)
				frappe.db.commit()
			
		except Exception as e:
			frappe.log_error(
				title=f"Material Request Güncelleme Hatası: {mr_name}",
				message=f"Sales Order {sales_order.name} için Material Request {mr_name} güncellenirken hata: {str(e)}\nTraceback: {frappe.get_traceback()}"
			)

