from . import __version__ as _version

app_name = "north_medical_portal"
app_title = "North Medical Portal"
app_publisher = "North Medical"
app_description = "Bayi portal sistemi - Stok takibi, malzeme talepleri ve satış siparişleri yönetimi"
app_email = "info@north-medical-germany.com"
app_license = "MIT"
app_version = _version

required_apps = ["erpnext"]

# Website Configuration
update_website_context = [
	"north_medical_portal.utils.website.update_website_context"
]

# Installation
after_install = "north_medical_portal.setup.install.after_install"

# After Migrate - Portal menu'yu düzenle
after_migrate = "north_medical_portal.setup.fix_portal_menu.fix_portal_menu"

# App After Init - Override ERPNext permissions for admin and portal lists
app_after_init = [
	"north_medical_portal.utils.override_erpnext_permissions.override_erpnext_permissions",
	"north_medical_portal.utils.override_portal_lists.override_post_process"
]

# Document Events
doc_events = {
	"Delivery Note": {
		"on_submit": "north_medical_portal.utils.delivery_note.transfer_stock_to_customer_warehouse"
	},
	"Sales Order": {
		"on_submit": "north_medical_portal.utils.sales_order.update_material_request_from_sales_order"
	}
}

# Scheduled Tasks
scheduler_events = {
	"daily": [
		"north_medical_portal.utils.stock.check_reorder_levels"
	],
}

# Website Routes
website_route_rules = [
	{"from_route": "/home", "to_route": "home"},
	{"from_route": "/portal/stock", "to_route": "portal/stock"},
	{"from_route": "/portal/sales-orders", "to_route": "portal/sales-orders"},
	{"from_route": "/portal/invoices", "to_route": "portal/invoices"},
	{"from_route": "/portal/purchase-orders", "to_route": "portal/purchase-orders"},
	{"from_route": "/portal/purchase-invoices", "to_route": "portal/purchase-invoices"},
	{"from_route": "/portal/material-requests", "to_route": "portal/material-requests"},
	{"from_route": "/portal/stock-entries", "to_route": "portal/stock-entries"},
	{"from_route": "/portal/material-issue", "to_route": "portal/material-issue"},
	{"from_route": "/portal/material-issue/new", "to_route": "portal/material-issue/new"},
	{"from_route": "/portal/material-issue/edit/<name>", "to_route": "portal/material-issue/edit"},
	{"from_route": "/portal/stock-entry/<name>", "to_route": "portal/stock-entry"},
	{"from_route": "/portal/material-request/<name>", "to_route": "portal/material-request-detail"},
]

# Fixtures
fixtures = ["Custom Field", "Property Setter"]

# Overriding Methods
override_whitelisted_methods = {
	"frappe.www.login.get_context": "north_medical_portal.www.login.get_context"
}

# Website Permissions
has_website_permission = {
	"Material Request": "north_medical_portal.utils.material_request_permission.has_website_permission",
	"Purchase Order": "north_medical_portal.utils.portal_permissions.has_website_permission_for_purchase_order",
	"Purchase Invoice": "north_medical_portal.utils.portal_permissions.has_website_permission_for_purchase_invoice",
	"Stock Entry": "north_medical_portal.utils.portal_permissions.has_website_permission_for_stock_entry"
}

# Portal Menu Items (via hooks - sidebar'a eklenir)
# Not: Portal Settings'e otomatik eklenmez, setup script ile eklenir
portal_menu_items = [
	{
		"title": "Stock Summary",  # Use English source text for translation
		"route": "/portal/stock",
		"reference_doctype": None,
		"role": "Customer",
		"enabled": 1
	}
]

