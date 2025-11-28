"""
Portal sayfalarını navbar'a ekle
"""
import frappe
from frappe import _


def add_portal_links_to_navbar():
	"""Website Settings'e portal sayfalarını ekle"""
	try:
		website_settings = frappe.get_doc("Website Settings")
		
		# Mevcut linkleri kontrol et
		existing_urls = [item.url for item in website_settings.top_bar_items or []]
		
		# Portal pages - use English source strings for translations
		portal_links = [
			{
				"label": _("Stock Status"),  # TR: Stok Durumu, DE: Bestandsstatus, FR: État des stocks, IT: Stato magazzino
				"url": "/portal/stock",
				"right": False,
			},
			{
				"label": _("Sales Orders"),  # TR: Satış Siparişleri, DE: Verkaufsaufträge, FR: Commandes de vente, IT: Ordini di vendita
				"url": "/portal/sales-orders",
				"right": False,
			},
			{
				"label": _("Invoices"),  # TR: Faturalar, DE: Rechnungen, FR: Factures, IT: Fatture
				"url": "/portal/invoices",
				"right": False,
			},
			{
				"label": _("Material Requests"),  # TR: Malzeme Talepleri, DE: Materialanfragen, FR: Demandes de matériel, IT: Richieste materiali
				"url": "/portal/material-requests",
				"right": False,
			},
			{
				"label": _("Stock Entries"),  # TR: Stok Hareketleri, DE: Lagerbewegungen, FR: Mouvements de stock, IT: Movimenti di magazzino
				"url": "/portal/stock-entries",
				"right": False,
			},
		]
		
		added = 0
		for link in portal_links:
			if link["url"] not in existing_urls:
				website_settings.append("top_bar_items", link)
				added += 1
		
		if added > 0:
			website_settings.flags.ignore_permissions = True
			website_settings.save()
			frappe.db.commit()
			
	except frappe.DoesNotExistError:
		pass
	except Exception as e:
		frappe.log_error(
			title="Navbar Portal Links Error",
			message=f"Error adding portal links to navbar: {str(e)}"
		)

