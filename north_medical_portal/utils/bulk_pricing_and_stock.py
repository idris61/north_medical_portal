import frappe


def setup_standard_buying_and_stock(
	buy_price_list: str = "Varsayılan Alış",
	default_sell_price_list: str = "Standard Selling",
	target_warehouse: str = "Mamuller - NM",
	default_factor: float = 0.8,
	default_qty: float = 1000.0,
) -> dict:
	"""Set a standard buying price for all stock items and create stock for each.

	- For each active stock Item:
	  - Find its lowest selling Item Price (any selling=1 price list).
	  - Create/update a buying Item Price in `buy_price_list` at (selling_rate * default_factor).
	- Create a single Stock Entry (Material Receipt) that adds `default_qty`
	  of each Item to `target_warehouse` at the computed buying rate.

	Returns a summary dict (for logging / debugging).
	"""

	summary = {
		"items_processed": 0,
		"prices_created": 0,
		"prices_updated": 0,
		"items_without_selling_price": 0,
		"stock_entry": None,
	}

	items = frappe.get_all(
		"Item",
		filters={"disabled": 0, "is_stock_item": 1},
		fields=["name", "item_name", "stock_uom"],
	)

	if not items:
		return summary

	# Price list & company info
	buy_pl_doc = frappe.get_doc("Price List", buy_price_list)
	buy_currency = buy_pl_doc.currency

	company = frappe.defaults.get_defaults().get("company") or frappe.db.get_value(
		"Company", {}, "name"
	)

	buying_rates: dict[str, float] = {}

	for item in items:
		item_code = item.name
		summary["items_processed"] += 1

		# En düşük satış fiyatını bul (herhangi bir selling=1 Item Price'tan)
		selling_prices = frappe.get_all(
			"Item Price",
			filters={"item_code": item_code, "selling": 1},
			fields=["name", "price_list_rate", "currency", "price_list"],
			order_by="price_list_rate asc",
			limit_page_length=1,
		)

		if not selling_prices:
			summary["items_without_selling_price"] += 1
			continue

		sp = selling_prices[0]
		sell_rate = sp.price_list_rate or 0
		if not sell_rate:
			summary["items_without_selling_price"] += 1
			continue

		# Alış fiyatını satıştan daha düşük olacak şekilde hesapla
		buy_rate = round(float(sell_rate) * float(default_factor), 2)
		if buy_rate >= sell_rate:
			buy_rate = max(sell_rate - 0.01, 0)

		currency = sp.currency or buy_currency

		# Buying price list'te kayıt var mı kontrol et
		existing = frappe.get_all(
			"Item Price",
			filters={"item_code": item_code, "price_list": buy_price_list},
			limit_page_length=1,
		)

		if existing:
			ip = frappe.get_doc("Item Price", existing[0].name)
			ip.price_list_rate = buy_rate
			ip.currency = currency
			ip.buying = 1
			ip.selling = 0
			ip.flags.ignore_permissions = True
			ip.save()
			summary["prices_updated"] += 1
		else:
			ip = frappe.get_doc(
				{
					"doctype": "Item Price",
					"price_list": buy_price_list,
					"price_list_rate": buy_rate,
					"buying": 1,
					"selling": 0,
					"item_code": item_code,
					"currency": currency,
				}
			)
			ip.flags.ignore_permissions = True
			ip.insert()
			summary["prices_created"] += 1

		buying_rates[item_code] = buy_rate

	# Stok girişi (Material Receipt) – her ürün için default_qty adet
	if not buying_rates:
		return summary

	# Warehouse'un account'unu uygun bir detay hesaba güncelle (grup hesap sorununu çözmek için)
	warehouse_doc = frappe.get_doc("Warehouse", target_warehouse)
	stock_account = "Fertige Erzeugnisse und Waren (Bestand) - NM"
	
	# Eğer warehouse'un account'u grup hesap ise, detay hesaba güncelle
	if warehouse_doc.account and frappe.db.get_value("Account", warehouse_doc.account, "is_group"):
		warehouse_doc.account = stock_account
		warehouse_doc.flags.ignore_permissions = True
		warehouse_doc.save(ignore_permissions=True)
		frappe.db.commit()

	se = frappe.new_doc("Stock Entry")
	se.stock_entry_type = "Material Receipt"
	se.company = company

	for item in items:
		item_code = item.name
		if item_code not in buying_rates:
			continue

		se.append(
			"items",
			{
				"item_code": item_code,
				"t_warehouse": target_warehouse,
				"qty": default_qty,
				"uom": item.stock_uom,
				"conversion_factor": 1,
				"basic_rate": buying_rates[item_code],
			},
		)

	if se.items:
		se.flags.ignore_permissions = True
		se.insert()
		# Submit etmeyi deneyelim
		try:
			se.submit()
			summary["stock_entry_status"] = "submitted"
		except Exception as e:
			# Submit başarısız olursa taslak olarak bırak
			frappe.log_error(f"Stock Entry submit failed: {str(e)}", "Stock Entry Submit Error")
			summary["stock_entry_status"] = "draft"
			summary["stock_entry_error"] = str(e)
		summary["stock_entry"] = se.name

	return summary


@frappe.whitelist()
def delete_and_recreate_stock_entry(warehouse="Mamuller - NM", default_qty=1000):
	"""
	Mevcut Stock Entry'yi silip yeniden oluştur (warehouse account düzeltmesiyle birlikte)
	"""
	# Eski Stock Entry'yi sil
	old_se = frappe.db.exists("Stock Entry", {"name": "MAT-STE-2025-00001"})
	if old_se:
		try:
			se_doc = frappe.get_doc("Stock Entry", old_se)
			if se_doc.docstatus == 0:
				se_doc.flags.ignore_permissions = True
				se_doc.delete()
				frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Error deleting old Stock Entry: {str(e)}", "Delete Stock Entry Error")
	
	# Yeniden oluştur
	return setup_standard_buying_and_stock(target_warehouse=warehouse, default_qty=default_qty)


