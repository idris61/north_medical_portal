"""
Portal Settings menüsünü düzenle:
1. Stok Özeti'nden birini kaldır (duplicate)
2. Stok Özeti'ni Sevkiyatlar'ın altına taşı
3. Issues'ı "Talepler" olarak değiştir
"""
import frappe


def fix_portal_menu():
	"""Portal Settings menüsünü düzenle"""
	try:
		portal_settings = frappe.get_doc("Portal Settings", "Portal Settings")
		
		# 1. Stok Özeti duplicate'lerini bul ve birini kaldır
		stock_summary_items = [d for d in portal_settings.get("menu", []) if d.get("route") == "/portal/stock"]
		if len(stock_summary_items) > 1:
			# İlkini tut, diğerlerini kaldır
			for item in stock_summary_items[1:]:
				portal_settings.remove(item)
			print(f"✅ {len(stock_summary_items) - 1} duplicate Stok Özeti menü öğesi kaldırıldı")
		
		# 2. Issues'ı "Talepler" olarak değiştir
		issues_items = [d for d in portal_settings.get("menu", []) if d.get("route") == "/issues"]
		for item in issues_items:
			if item.title == "Issues" or item.title == "Sorunlar":
				item.title = "Talepler"
				print(f"✅ Issues menü öğesi 'Talepler' olarak değiştirildi")
		
		# 3. Stok Özeti'ni Sevkiyatlar'ın altına taşı
		# Önce menü öğelerini sıralayalım
		menu_items = list(portal_settings.menu)
		
		# Sevkiyatlar'ın index'ini bul
		shipments_idx = None
		stock_summary_idx = None
		
		for idx, item in enumerate(menu_items):
			if item.route == "/shipments":
				shipments_idx = idx
			elif item.route == "/portal/stock":
				stock_summary_idx = idx
		
		# Eğer Stok Özeti varsa ve Sevkiyatlar'ın altında değilse, taşı
		if stock_summary_idx is not None and shipments_idx is not None:
			if stock_summary_idx != shipments_idx + 1:
				# Stok Özeti'ni kaldır
				stock_item = menu_items.pop(stock_summary_idx)
				# Sevkiyatlar'ın hemen altına ekle
				menu_items.insert(shipments_idx + 1, stock_item)
				# Menüyü yeniden set et
				portal_settings.menu = []
				for item in menu_items:
					portal_settings.append("menu", item)
				print(f"✅ Stok Özeti menü öğesi Sevkiyatlar'ın altına taşındı")
		
		# Değişiklikleri kaydet
		portal_settings.flags.ignore_permissions = True
		portal_settings.save()
		frappe.db.commit()
		
		print("\n✅ Portal Settings menüsü başarıyla düzenlendi")
		print("\nGüncel menü sırası:")
		for idx, item in enumerate(portal_settings.menu, 1):
			print(f"  {idx}. {item.title} - Route: {item.route} - Enabled: {item.enabled}")
		
	except Exception as e:
		frappe.log_error(
			title="Portal Settings Menu Fix Error",
			message=f"Error fixing portal menu: {str(e)}"
		)
		print(f"❌ Hata: {str(e)}")
		raise

