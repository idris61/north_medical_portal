"""
Malzeme Talepleri Sayfası
"""
import frappe
from north_medical_portal.utils.helpers import validate_dealer_access
from north_medical_portal.www.api.material_request import get_material_requests


def get_context(context):
	"""Sayfa context'ini hazırla"""
	# Portal sidebar'ı göster
	context.no_cache = 1
	context.show_sidebar = True
	
	user_company = validate_dealer_access()
	
	requests_data = get_material_requests()
	
	context.update({
		"company": user_company,
		"material_requests": requests_data.get("material_requests", []),
		"has_requests": len(requests_data.get("material_requests", [])) > 0,
	})











