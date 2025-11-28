"""
Material Request detay sayfası - Özel permission kontrolü ile
"""
import frappe
from frappe import _
from erpnext.accounts.doctype.payment_request.payment_request import (
	ALLOWED_DOCTYPES_FOR_PAYMENT_REQUEST,
	get_amount,
)
from north_medical_portal.utils.helpers import get_user_company, is_admin_user


def get_context(context):
	context.no_cache = 1
	context.show_sidebar = True
	
	# Material Request name'i al
	mr_name = frappe.form_dict.name
	if not mr_name:
		frappe.throw(_("Material Request name is required"), frappe.ValidationError)
	
	# Material Request'i al
	context.doc = frappe.get_doc("Material Request", mr_name)
	if hasattr(context.doc, "set_indicator"):
		context.doc.set_indicator()

	context.parents = [{"label": _("Material Requests"), "route": "/portal/material-requests"}]
	context.title = context.doc.name
	
	# Material Request için özel permission kontrolü
	if not has_material_request_permission(context.doc):
		frappe.throw(_("Not Permitted"), frappe.PermissionError)

	# Material Request için özel print format
	context.print_format = "Material Request Portal"

	# Material Request için özel item bilgileri
	context.doc.items = get_more_items_info(context.doc.items, context.doc.name)
	
	# Item resimlerini ekle
	for item in context.doc.items:
		item_image = frappe.db.get_value("Item", item.item_code, "image")
		item.thumbnail = item_image
		if item_image:
			item.image_url = frappe.utils.get_url(item_image)


def has_material_request_permission(doc):
	"""
	Material Request için özel permission kontrolü
	"""
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


def get_more_items_info(items, material_request):
	"""Material Request item'larına ek bilgiler ekle"""
	from frappe.utils import flt
	
	for item in items:
		item.customer_provided = frappe.get_value("Item", item.item_code, "is_customer_provided_item")
		item.work_orders = frappe.db.sql(
			"""
			select
				wo.name, wo.status, wo_item.consumed_qty
			from
				`tabWork Order Item` wo_item, `tabWork Order` wo
			where
				wo_item.item_code=%s
				and wo_item.consumed_qty=0
				and wo_item.parent=wo.name
				and wo.status not in ('Completed', 'Cancelled', 'Stopped')
			order by
				wo.name asc""",
			item.item_code,
			as_dict=1,
		)
		item.delivered_qty = flt(
			frappe.db.sql(
				"""select sum(transfer_qty)
						from `tabStock Entry Detail` where material_request = %s
						and item_code = %s and docstatus = 1""",
				(material_request, item.item_code),
			)[0][0]
		)
	return items

