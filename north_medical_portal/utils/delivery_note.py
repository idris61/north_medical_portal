"""
Delivery Note için özel işlemler
"""
import frappe
from frappe import _
from frappe.utils import nowdate, nowtime


def transfer_stock_to_customer_warehouse(doc, method):
	"""
	Delivery Note submit edildiğinde, müşterinin deposuna stok transferi yap
	
	Delivery Note'daki warehouse'dan (Mamuller - NM) müşterinin deposuna (Bayi-1 - NM)
	Stock Entry (Material Transfer) oluştur
	"""
	try:
		if doc.is_return:
			return
		
		# Müşterinin warehouse'ını bul
		customer_warehouse = frappe.db.sql("""
			SELECT name
			FROM `tabWarehouse`
			WHERE company = %s
			AND name LIKE %s
			AND disabled = 0
			AND is_group = 0
			LIMIT 1
		""", (doc.company, f"%{doc.customer}%"), as_dict=True)
		
		if not customer_warehouse:
			# Müşteri warehouse bulunamadı, transfer yapma
			frappe.log_error(
				_("Müşteri için depo bulunamadı: {0}").format(doc.customer),
				_("Delivery Note Stok Transfer Hatası")
			)
			return
		
		customer_wh = customer_warehouse[0].name
		
		# Transfer edilecek item'ları topla
		transfer_items = []
		for item in doc.items:
			# Item'ın warehouse'ı müşteri warehouse'ından farklıysa transfer et
			if item.warehouse and item.warehouse != customer_wh:
				# Stok item kontrolü
				is_stock_item = frappe.db.get_value("Item", item.item_code, "is_stock_item")
				if is_stock_item:
					transfer_items.append({
						"item_code": item.item_code,
						"qty": item.qty,
						"stock_qty": item.stock_qty,
						"uom": item.uom,
						"stock_uom": item.stock_uom,
						"from_warehouse": item.warehouse,
						"to_warehouse": customer_wh
					})
		
		if not transfer_items:
			# Transfer edilecek item yok
			return
		
		# Stock Entry (Material Transfer) oluştur
		stock_entry = frappe.new_doc("Stock Entry")
		stock_entry.stock_entry_type = "Material Transfer"
		stock_entry.purpose = "Material Transfer"
		stock_entry.company = doc.company
		stock_entry.posting_date = doc.posting_date
		stock_entry.posting_time = doc.posting_time
		stock_entry.remarks = f"Delivery Note {doc.name} için otomatik stok transferi"
		
		# Items ekle
		for item_data in transfer_items:
			# Valuation rate'ı al
			valuation_rate = frappe.db.get_value(
				"Stock Ledger Entry",
				{
					"item_code": item_data["item_code"],
					"warehouse": item_data["from_warehouse"],
					"is_cancelled": 0
				},
				"valuation_rate",
				order_by="posting_date DESC, posting_time DESC, creation DESC"
			) or 1.0
			
			stock_entry.append("items", {
				"item_code": item_data["item_code"],
				"qty": item_data["qty"],
				"stock_qty": item_data["stock_qty"],
				"uom": item_data["uom"],
				"stock_uom": item_data["stock_uom"],
				"s_warehouse": item_data["from_warehouse"],
				"t_warehouse": item_data["to_warehouse"],
				"basic_rate": valuation_rate,
				"allow_zero_valuation_rate": 1
			})
		
		# Stock Entry'yi kaydet ve submit et
		stock_entry.flags.ignore_permissions = True
		stock_entry.insert()
		
		# Item sayısını kontrol et
		if len(stock_entry.items) != len(transfer_items):
			frappe.log_error(
				_("Stock Entry'de item sayısı uyumsuz: Beklenen {0}, Oluşturulan {1}").format(
					len(transfer_items), len(stock_entry.items)
				),
				_("Delivery Note Stok Transfer Hatası")
			)
			# Stock Entry'yi sil
			frappe.delete_doc("Stock Entry", stock_entry.name, force=1, ignore_permissions=True)
			return
		
		stock_entry.submit()
		
		# Submit sonrası kontrol: Tüm item'lar için SLE oluşmuş mu?
		sle_count = frappe.db.count("Stock Ledger Entry", {
			"voucher_type": "Stock Entry",
			"voucher_no": stock_entry.name,
			"is_cancelled": 0
		})
		
		expected_sle_count = len(transfer_items) * 2  # Her item için source ve target warehouse
		
		if sle_count < expected_sle_count:
			frappe.log_error(
				_("Stock Entry {0} için SLE sayısı yetersiz: Beklenen {1}, Oluşturulan {2}").format(
					stock_entry.name, expected_sle_count, sle_count
				),
				_("Delivery Note Stok Transfer Hatası")
			)
		
		frappe.msgprint(
			_("Stok transferi oluşturuldu: {0}").format(stock_entry.name),
			indicator="green"
		)
		
	except Exception as e:
		# Hata durumunda log tut
		# Error log başlığı 140 karakter limiti var, bu yüzden kısaltıyoruz
		error_title = _("DN Stok Transfer Hatası")
		error_message = _("DN {0} stok transfer hatası: {1}").format(
			doc.name, str(e)[:100]  # Mesajı da kısaltıyoruz
		)
		frappe.log_error(
			error_message,
			error_title
		)
		# Hata olsa bile Delivery Note submit işlemini durdurmamak için exception'ı tekrar fırlatmıyoruz
		# Çünkü bu bir hook ve Delivery Note'un submit edilmesini engellememeli

