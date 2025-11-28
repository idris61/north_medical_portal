"""
Home / Landing Page - North Medical Germany
Based on https://www.northmedical.de/
"""
import frappe


def get_featured_products():
	"""Homepage'den öne çıkan ürünleri getir"""
	try:
		homepage = frappe.get_cached_doc("Homepage")
		if not homepage:
			return []
		
		# Products field'ı var mı kontrol et
		products = getattr(homepage, 'products', None)
		if not products:
			return []
		
		product_list = []
		for product in list(products)[:6]:  # İlk 6 ürün
			if not product.item_code:
				continue
			
			try:
				# Website Item bilgilerini al
				website_item = frappe.get_cached_doc("Website Item", product.item_code)
				
				# Resim URL'ini düzelt
				image_url = None
				if product.image:
					image_url = product.image
				elif website_item.website_image:
					image_url = website_item.website_image
				elif website_item.thumbnail:
					image_url = website_item.thumbnail
				
				# Route'u düzelt
				route = product.route or website_item.route or ""
				if route and not route.startswith("/"):
					route = f"/{route}"
				elif not route:
					route = f"/{website_item.route}" if website_item.route else "#"
				
				product_list.append({
					"item_code": product.item_code,
					"item_name": product.item_name or website_item.item_name,
					"route": route,
					"image": image_url,
					"description": product.description or website_item.web_long_description or website_item.description or "",
				})
			except Exception as e:
				frappe.log_error(f"Error processing product {product.item_code}: {str(e)}", "Homepage Product Error")
				continue
		
		return product_list
	except Exception as e:
		frappe.log_error(f"Error getting featured products: {str(e)}", "Homepage Featured Products Error")
	
	return []


def get_hero_slides():
	"""Hero carousel için görselleri getir - ERPNext'ten yüklenen görseller"""
	slides = []
	
	# ERPNext'e yüklenen banner görselleri
	north_medical_slides = [
		{
			"image": "/files/north_medical_slider1.png",
			"active": True
		},
		{
			"image": "/files/north_medical_slider2.png",
			"active": False
		}
	]
	
	# Sadece bu 2 görseli ekle
	for slide in north_medical_slides:
		slides.append(slide)
	
	return slides


def get_category_icon(category_name, category_title):
	"""Kategori ismine göre ikon belirle - Profesyonel ikonlar"""
	icon_map = {
		# Temizlik / Cleaning
		"reinigung": "fa-spray-can",
		"cleaning": "fa-spray-can",
		"temizlik": "fa-spray-can",
		"oberfläche": "fa-spray-can",
		"surface": "fa-spray-can",
		
		# Dezenfeksiyon / Disinfection
		"desinfektion": "fa-flask",
		"disinfection": "fa-flask",
		"dezenfeksiyon": "fa-flask",
		
		# Hijyen / Hygiene
		"hygiene": "fa-soap",
		"hijyen": "fa-soap",
		"hygien": "fa-soap",
		
		# Kişisel Koruyucu / Personal Protective Equipment
		"schutz": "fa-hard-hat",
		"protection": "fa-hard-hat",
		"koruma": "fa-hard-hat",
		"koruyucu": "fa-hard-hat",
		"protective": "fa-hard-hat",
		"ppe": "fa-hard-hat",
		"personal": "fa-hard-hat",
		"kişisel": "fa-hard-hat",
		
		# Eldiven / Gloves
		"handschuh": "fa-hand-paper",
		"glove": "fa-hand-paper",
		"eldiven": "fa-hand-paper",
		
		# Maske / Mask
		"maske": "fa-head-side-mask",
		"mask": "fa-head-side-mask",
		
		# Medikal / Medical
		"medizin": "fa-stethoscope",
		"medical": "fa-stethoscope",
		"tıbbi": "fa-stethoscope",
		
		# Giyim / Clothing
		"kleidung": "fa-tshirt",
		"clothing": "fa-tshirt",
		"giyim": "fa-tshirt",
		
		# Aksesuar / Accessories
		"zubehör": "fa-tools",
		"accessory": "fa-tools",
		"aksesuar": "fa-tools",
		
		# Kağıt / Paper
		"papier": "fa-file-alt",
		"paper": "fa-file-alt",
		"kağıt": "fa-file-alt",
		
		# Bez / Cloth
		"tuch": "fa-cut",
		"cloth": "fa-cut",
		"bez": "fa-cut",
		
		# Atık / Waste
		"müll": "fa-trash-alt",
		"waste": "fa-trash-alt",
		"atık": "fa-trash-alt",
	}
	
	# Kategori adını ve başlığını küçük harfe çevir
	search_text = f"{category_name} {category_title}".lower()
	
	# Öncelik sırasına göre kontrol et (daha spesifik olanlar önce)
	priority_keywords = [
		("hygiene", "fa-soap"),
		("hijyen", "fa-soap"),
		("protective", "fa-hard-hat"),
		("koruyucu", "fa-hard-hat"),
		("kişisel", "fa-hard-hat"),
		("disinfection", "fa-flask"),
		("dezenfeksiyon", "fa-flask"),
		("cleaning", "fa-spray-can"),
		("temizlik", "fa-spray-can"),
	]
	
	# Önce öncelikli anahtar kelimeleri kontrol et
	for keyword, icon in priority_keywords:
		if keyword in search_text:
			return icon
	
	# Sonra genel mapping'i kontrol et
	for keyword, icon in icon_map.items():
		if keyword in search_text:
			return icon
	
	# Varsayılan ikon
	return "fa-box"


def get_category_color_index(category_name, category_title):
	"""Kategori ismine göre renk index'i belirle (1-4 arası)"""
	# Kategori adının hash'ini al ve 1-4 arasına map et
	import hashlib
	hash_value = int(hashlib.md5(f"{category_name}{category_title}".encode()).hexdigest(), 16)
	return (hash_value % 4) + 1


def get_news_posts():
	"""Son haberleri getir - Blog Post'lardan"""
	try:
		# Yayınlanmış blog post'ları al
		posts = frappe.get_all(
			"Blog Post",
			filters={
				"published": 1
			},
			fields=["name", "title", "blog_intro", "published_on", "route", "meta_image", "disable_comments"],
			order_by="published_on desc",
			limit=3
		)
		
		# Eğer blog post yoksa, boş liste döndür
		if not posts:
			return []
		
		post_list = []
		for post in posts:
			# Tarih formatla - basit ve güvenli
			formatted_date = ""
			if post.published_on:
				try:
					from frappe.utils import formatdate, getdate
					pub_date = getdate(post.published_on)
					lang = frappe.local.lang or "en"
					if lang == "tr":
						formatted_date = formatdate(pub_date, "dd MMMM yyyy")
					elif lang == "de":
						formatted_date = formatdate(pub_date, "dd. MMMM yyyy")
					elif lang == "fr":
						formatted_date = formatdate(pub_date, "dd MMMM yyyy")
					elif lang == "it":
						formatted_date = formatdate(pub_date, "dd MMMM yyyy")
					else:
						formatted_date = formatdate(pub_date, "MMMM dd, yyyy")
				except:
					formatted_date = str(post.published_on) if post.published_on else ""
			
			# Yorum durumu
			try:
				from frappe import _
				if post.disable_comments:
					comments_status = _("Comments disabled")
				else:
					comments_status = _("Comments enabled")
			except:
				comments_status = "Comments disabled" if post.disable_comments else "Comments enabled"
			
			# Resim URL'ini düzelt
			image_url = None
			if post.meta_image:
				if post.meta_image.startswith("/files/"):
					image_url = post.meta_image
				elif post.meta_image.startswith("http"):
					image_url = post.meta_image
				else:
					image_url = f"/files/{post.meta_image}"
			
			# Blog intro'yu al
			intro_text = post.blog_intro or ""
			
			post_list.append({
				"title": post.title or "",
				"intro": intro_text,
				"date": formatted_date,
				"comments_status": comments_status,
				"route": post.route or f"/blog/{post.name}",
				"image": image_url,
			})
		
		return post_list
	except Exception as e:
		frappe.log_error(f"Error getting news posts: {str(e)}", "Homepage News Error")
		import traceback
		frappe.log_error(traceback.format_exc(), "Homepage News Error Traceback")
		return []


def get_partners():
	"""Ortakları/Markaları getir - Sadece belirli 4 logo"""
	try:
		# Sadece bu 4 markayı göster
		partner_brands = ["Dr. Schumacher", "HARTMANN", "TORK", "SÖHNGEN"]
		
		brand_list = []
		for brand_name in partner_brands:
			# Brand'i bul
			brand = frappe.db.get_value(
				"Brand",
				{"brand": brand_name},
				["name", "brand", "image", "description"],
				as_dict=True
			)
			
			if brand:
				brand_list.append({
					"name": brand.brand or brand.name,
					"image": brand.image,
					"description": brand.description or "",
				})
			else:
				# Brand yoksa, logo URL'lerini direkt kullan
				logo_urls = {
					"Dr. Schumacher": "https://www.northmedical.de/wp-content/uploads/2015/10/70035_20170707131845.jpg",
					"HARTMANN": "https://www.northmedical.de/wp-content/uploads/2020/05/banner-bode3-1.png",
					"TORK": "https://www.northmedical.de/wp-content/uploads/2015/10/70122_20181024090130.png",
					"SÖHNGEN": "https://www.northmedical.de/wp-content/uploads/2015/09/s_hngen.png"
				}
				
				brand_list.append({
					"name": brand_name,
					"image": logo_urls.get(brand_name),
					"description": "",
				})
		
		return brand_list
	except Exception as e:
		frappe.log_error(f"Error getting partners: {str(e)}", "Homepage Partners Error")
		return []


def get_categories():
	"""Tüm kategorileri getir - carousel için"""
	try:
		# Website'de gösterilecek kategorileri al
		categories = frappe.get_all(
			"Item Group",
			filters={
				"show_in_website": 1,
				"is_group": 0  # Sadece ürün içeren kategoriler
			},
			fields=["name", "item_group_name", "route", "image"],
			order_by="lft asc"
		)
		
		# Eğer yeterli kategori yoksa, is_group=1 olanları da ekle
		if len(categories) < 3:
			group_categories = frappe.get_all(
				"Item Group",
				filters={
					"show_in_website": 1,
					"is_group": 1
				},
				fields=["name", "item_group_name", "route", "image"],
				order_by="lft asc",
				limit=10
			)
			categories.extend(group_categories)
		
		# Kategori bilgilerini hazırla
		category_list = []
		for cat in categories[:12]:  # Maksimum 12 kategori
			# Ürün sayısını kontrol et
			product_count = frappe.db.count("Website Item", {
				"published": 1,
				"item_group": cat.name
			})
			
			if product_count > 0:  # Sadece ürünü olan kategoriler
				# URL encode için kategori adını düzelt
				import urllib.parse
				encoded_name = urllib.parse.quote(cat.name)
				
				# Kategori ismine göre ikon belirle
				icon = get_category_icon(cat.name, cat.item_group_name)
				
				# Kategori ismine göre renk gradient belirle
				color_index = get_category_color_index(cat.name, cat.item_group_name)
				
				# Kategori ismini çevir
				from webshop.webshop.utils.translation import get_translated_text
				translated_title = get_translated_text(cat.name)
				if not translated_title or translated_title == cat.name:
					# Eğer çeviri yoksa, item_group_name kullan
					translated_title = cat.item_group_name or cat.name
				
				category_list.append({
					"name": cat.name,
					"title": translated_title,
					"url": f"/all-products?item_group={encoded_name}",
					"image": cat.image,
					"product_count": product_count,
					"icon": icon,
					"color_index": color_index
				})
		
		return category_list
	except Exception as e:
		frappe.log_error(f"Error getting categories: {str(e)}", "Homepage Categories Error")
		return []


def get_context(context):
	"""Sayfa context'ini hazırla"""
	context.title = "North Medical Germany"
	context.body_class = "home-page"
	
	# FontAwesome CDN ekle
	if context.get("head_include"):
		if "font-awesome" not in context.head_include.lower():
			context.head_include += '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" integrity="sha512-1ycn6IcaQQ40/MKBW2W4Rhis/DbILU74C1vSrLJxCq57o941Ym01SwNsOMqvEBFlcgUa6xLiPY/NS5R+E6ztJQ==" crossorigin="anonymous" referrerpolicy="no-referrer" />'
	else:
		context.head_include = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" integrity="sha512-1ycn6IcaQQ40/MKBW2W4Rhis/DbILU74C1vSrLJxCq57o941Ym01SwNsOMqvEBFlcgUa6xLiPY/NS5R+E6ztJQ==" crossorigin="anonymous" referrerpolicy="no-referrer" />'
	
	# Hero carousel görselleri
	context.hero_slides = get_hero_slides()
	
	# Kategoriler (carousel için)
	context.categories = get_categories()
	context.has_categories = len(context.categories) > 0
	
	# Website Settings'den banner_image al (about section için)
	context.banner_image = None
	context.footer_logo = None
	try:
		website_settings = frappe.get_cached_doc("Website Settings")
		if website_settings and hasattr(website_settings, 'banner_image') and website_settings.banner_image:
			context.banner_image = website_settings.banner_image
		if website_settings and hasattr(website_settings, 'footer_logo') and website_settings.footer_logo:
			context.footer_logo = website_settings.footer_logo
	except Exception as e:
		frappe.log_error(f"Error getting website settings: {str(e)}", "Website Settings Error")
	
	# Öne çıkan ürünler
	context.featured_products = get_featured_products()
	context.has_featured_products = len(context.featured_products) > 0
	
	# Haberler
	context.news_posts = get_news_posts()
	context.has_news = len(context.news_posts) > 0
	
	# Ortaklar / Markalar
	context.partners = get_partners()
	context.has_partners = len(context.partners) > 0
	
	context.no_cache = 1

