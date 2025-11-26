"""
Portal sayfalarını navbar'a ekle
"""
import frappe
from frappe import _


def add_portal_links_to_navbar():
	"""Website Settings'e portal sayfalarını ekle"""
	print("\n" + "="*60)
	print("NAVBAR'A PORTAL SAYFALARI EKLEME")
	print("="*60)
	
	try:
		website_settings = frappe.get_doc("Website Settings")
		
		# Mevcut linkleri kontrol et
		existing_urls = [item.url for item in website_settings.top_bar_items or []]
		
		# Portal sayfaları - Translation key'leri kullan
		portal_links = [
			{
				"label": _("Stok Durumu"),  # TR: Stok Durumu, DE: Bestandsstatus, EN: Stock Status, FR: État des stocks, IT: Stato magazzino
				"url": "/portal/stock",
				"right": False,
			},
			{
				"label": _("Satış Siparişleri"),  # TR: Satış Siparişleri, DE: Verkaufsaufträge, EN: Sales Orders, FR: Commandes de vente, IT: Ordini di vendita
				"url": "/portal/sales-orders",
				"right": False,
			},
			{
				"label": _("Faturalar"),  # TR: Faturalar, DE: Rechnungen, EN: Invoices, FR: Factures, IT: Fatture
				"url": "/portal/invoices",
				"right": False,
			},
			{
				"label": _("Malzeme Talepleri"),  # TR: Malzeme Talepleri, DE: Materialanfragen, EN: Material Requests, FR: Demandes de matériel, IT: Richieste materiali
				"url": "/portal/material-requests",
				"right": False,
			},
			{
				"label": _("Stok Hareketleri"),  # TR: Stok Hareketleri, DE: Lagerbewegungen, EN: Stock Entries, FR: Mouvements de stock, IT: Movimenti di magazzino
				"url": "/portal/stock-entries",
				"right": False,
			},
		]
		
		added = 0
		for link in portal_links:
			if link["url"] not in existing_urls:
				website_settings.append("top_bar_items", link)
				print(f"  ✅ {link['label']} eklendi")
				added += 1
			else:
				print(f"  ⚠️  {link['label']} zaten mevcut")
		
		if added > 0:
			website_settings.flags.ignore_permissions = True
			website_settings.save()
			frappe.db.commit()
			print(f"\n✅ {added} link navbar'a eklendi")
		else:
			print("\n✅ Tüm linkler zaten mevcut")
			
	except frappe.DoesNotExistError:
		print("  ⚠️  Website Settings bulunamadı")
	except Exception as e:
		print(f"  ❌ Hata: {str(e)}")
		frappe.log_error(
			title="Navbar Portal Links Error",
			message=f"Error adding portal links to navbar: {str(e)}"
		)


if __name__ == "__main__":
	add_portal_links_to_navbar()
	
	print("\n" + "="*60)
	print("NAVBAR GÜNCELLEMESİ TAMAMLANDI")
	print("="*60)

