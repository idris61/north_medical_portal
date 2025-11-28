"""
Website yapılandırması - North Medical brand stilleri
Tüm içerikler Website Settings'ten yönetilir, burada sadece CSS stilleri tanımlanır
"""
import frappe

# Brand Colors
BRAND_COLORS = {
	"dark_blue": "#2a306a",
	"light_blue": "#0099cc",
	"red": "#d62828",
}

def get_website_css():
	"""Tüm website CSS'leri tek bir fonksiyonda"""
	return f"""
	<style>
	/* Global Typography & Colors */
	* {{
		box-sizing: border-box;
	}}
	
	body {{
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif !important;
		font-size: 16px !important;
		line-height: 1.6 !important;
		color: #333333 !important;
		-webkit-font-smoothing: antialiased;
		-moz-osx-font-smoothing: grayscale;
	}}
	
	h1, h2, h3, h4, h5, h6 {{
		color: {BRAND_COLORS['dark_blue']} !important;
		font-weight: 600 !important;
		line-height: 1.3 !important;
		margin-bottom: 1rem !important;
	}}
	
	h1 {{ font-size: 2.5rem !important; }}
	h2 {{ font-size: 2rem !important; }}
	h3 {{ font-size: 1.75rem !important; }}
	h4 {{ font-size: 1.5rem !important; }}
	h5 {{ font-size: 1.25rem !important; }}
	h6 {{ font-size: 1.1rem !important; }}
	
	p {{
		margin-bottom: 1rem !important;
		color: #333333 !important;
		line-height: 1.6 !important;
	}}
	
	a {{
		color: {BRAND_COLORS['light_blue']} !important;
		text-decoration: none !important;
		transition: color 0.3s ease !important;
	}}
	
	a:hover {{
		color: {BRAND_COLORS['dark_blue']} !important;
		text-decoration: underline !important;
	}}
	
	/* Scrollbar Styles - Mavi */
	::-webkit-scrollbar {{
		width: 12px;
		height: 12px;
	}}
	
	::-webkit-scrollbar-track {{
		background: #f1f1f1;
		border-radius: 10px;
	}}
	
	::-webkit-scrollbar-thumb {{
		background: {BRAND_COLORS['light_blue']};
		border-radius: 10px;
		border: 2px solid #f1f1f1;
	}}
	
	::-webkit-scrollbar-thumb:hover {{
		background: {BRAND_COLORS['dark_blue']};
	}}
	
	/* Firefox Scrollbar */
	* {{
		scrollbar-width: thin;
		scrollbar-color: {BRAND_COLORS['light_blue']} #f1f1f1;
	}}
	
	/* Back to Top Button */
	#back-to-top {{
		position: fixed;
		bottom: 30px;
		right: 30px;
		width: 50px;
		height: 50px;
		background-color: {BRAND_COLORS['light_blue']};
		color: #ffffff;
		border: none;
		border-radius: 50%;
		cursor: pointer;
		display: none;
		align-items: center;
		justify-content: center;
		box-shadow: 0 4px 12px rgba(0, 153, 204, 0.3);
		transition: all 0.3s ease;
		z-index: 1000;
		font-size: 20px;
		line-height: 1;
	}}
	
	#back-to-top:hover {{
		background-color: {BRAND_COLORS['dark_blue']};
		box-shadow: 0 6px 16px rgba(42, 48, 106, 0.4);
		transform: translateY(-3px);
	}}
	
	#back-to-top.show {{
		display: flex;
	}}
	
	#back-to-top svg {{
		width: 24px;
		height: 24px;
		fill: #ffffff;
	}}
	
	/* Navbar Styles */
	.navbar.navbar-light {{
		background-color: #ffffff !important;
		border-bottom: 2px solid {BRAND_COLORS['light_blue']} !important;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
	}}
	
	/* Navbar linklerini ortala */
	.navbar.navbar-light .navbar-collapse .navbar-nav:first-child {{
		justify-content: center !important;
		flex: 1 !important;
		margin: 0 auto !important;
	}}
	
	/* Giriş ve dil seçiciyi sağa yasla */
	.navbar.navbar-light .navbar-nav.ml-auto {{
		justify-content: flex-end !important;
		margin-left: auto !important;
	}}
	
	.navbar.navbar-light .nav-link {{
		color: {BRAND_COLORS['red']} !important;
		font-weight: 700;
		font-size: 16px;
		letter-spacing: 0.5px;
	}}
	
	.navbar.navbar-light .navbar-brand {{
		color: {BRAND_COLORS['dark_blue']} !important;
		font-weight: 600;
	}}
	
	/* Logo boyutunu büyüt */
	.navbar.navbar-light .navbar-brand img {{
		height: 110px !important;
		max-height: 110px !important;
		width: auto !important;
		object-fit: contain;
	}}
	
	.navbar.navbar-light .nav-link:hover {{
		background-color: rgba(214, 40, 40, 0.1) !important;
		color: {BRAND_COLORS['red']} !important;
	}}
	
	.navbar.navbar-light .nav-link.active {{
		color: {BRAND_COLORS['red']} !important;
		border-bottom: 2px solid {BRAND_COLORS['red']} !important;
	}}
	
	#language-picker-nav .nav-link {{
		color: {BRAND_COLORS['red']} !important;
		font-weight: 700;
		font-size: 16px;
	}}
	
	/* En sağdaki arama/dil alanını gizle */
	.navbar-search,
	.form-control.navbar-search,
	.navbar .form-group#language-switcher:not(.hide),
	.navbar input[type="text"][placeholder*="Türkçe"],
	.navbar input[type="text"][placeholder*="Turkish"],
	.navbar input[type="text"].form-control:not(.navbar-search) {{
		display: none !important;
		visibility: hidden !important;
		opacity: 0 !important;
		height: 0 !important;
		width: 0 !important;
		overflow: hidden !important;
		margin: 0 !important;
		padding: 0 !important;
	}}
	
	/* Footer Styles */
	html {{
		height: 100%;
	}}
	
	body {{
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}}
	
	body > .container,
	body > .page-content-wrapper,
	body > div[data-path],
	.page-content-wrapper {{
		flex: 1 0 auto;
		min-height: calc(100vh - 200px);
	}}
	
	.web-footer {{
		background-color: {BRAND_COLORS['dark_blue']} !important;
		border-top: 2px solid {BRAND_COLORS['light_blue']} !important;
		padding: 3rem 0 2rem 0 !important;
		margin-top: auto !important;
		width: 100% !important;
		flex-shrink: 0;
	}}
	
	.web-footer .container {{
		max-width: 1200px;
		margin: 0 auto;
		padding: 0 15px;
	}}
	
	.web-footer,
	.web-footer a,
	.web-footer .footer-link,
	.web-footer .footer-info {{
		color: #ffffff !important;
	}}
	
	.web-footer a:hover {{
		color: {BRAND_COLORS['light_blue']} !important;
		text-decoration: none;
	}}
	
	.web-footer .footer-group-label {{
		color: {BRAND_COLORS['light_blue']} !important;
		font-weight: 700 !important;
		font-size: 1.5rem !important;
		margin-bottom: 0.75rem !important;
	}}
	
	/* Footer Info - Copyright ortalanmış */
	.footer-info {{
		text-align: center !important;
		font-size: 1rem !important;
		color: rgba(255, 255, 255, 0.9) !important;
	}}
	
	.footer-info .row {{
		justify-content: center;
	}}
	
	.footer-col-left,
	.footer-col-right {{
		text-align: center !important;
		font-size: 1rem !important;
	}}
	
	/* Footer Contact Info */
	.footer-contact-info {{
		margin-bottom: 1.5rem;
		padding-bottom: 1.5rem;
		border-bottom: 1px solid rgba(255, 255, 255, 0.2);
		text-align: left;
	}}
	
	.footer-contact-details {{
		max-width: 100%;
		text-align: left;
	}}
	
	.footer-contact-details h5 {{
		color: {BRAND_COLORS['light_blue']} !important;
		font-weight: 700 !important;
		font-size: 1.5rem !important;
		margin-bottom: 0.75rem !important;
		text-align: left;
	}}
	
	.footer-contact-details p {{
		color: rgba(255, 255, 255, 0.9) !important;
		margin-bottom: 0.5rem !important;
		line-height: 1.6 !important;
		font-size: 1.1rem !important;
		text-align: left;
	}}
	
	.footer-contact-details p strong {{
		font-weight: 700 !important;
		font-size: 1.2rem !important;
		color: #ffffff !important;
	}}
	
	/* Footer Links */
	.web-footer .footer-link,
	.web-footer a {{
		font-size: 1rem !important;
		color: rgba(255, 255, 255, 0.9) !important;
	}}
	
	.web-footer .footer-link:hover,
	.web-footer a:hover {{
		color: {BRAND_COLORS['light_blue']} !important;
		font-weight: 600 !important;
	}}
	
	.footer-contact-details a {{
		color: #ffffff !important;
		text-decoration: none;
	}}
	
	.footer-contact-details a:hover {{
		color: {BRAND_COLORS['light_blue']} !important;
		text-decoration: underline;
	}}
	
	/* Login Page Styles */
	/* Login sayfasındaki "ERPNext adresine giriş yapın" yazısını gizle - login.bundle.css'ten sonra yüklenecek */
	.for-login .page-card-head h4,
	.for-email-login .page-card-head h4,
	.for-signup .page-card-head h4,
	.for-forgot .page-card-head h4,
	.for-login-with-email-link .page-card-head h4,
	.page-card-head h4,
	.page-card-head h4:not([style*="display: none"]),
	body .page-card-head h4,
	body .for-login h4,
	body .for-email-login h4,
	body .for-signup h4,
	body .for-forgot h4,
	body .for-login-with-email-link h4 {{
		display: none !important;
		visibility: hidden !important;
		height: 0 !important;
		margin: 0 !important;
		padding: 0 !important;
		overflow: hidden !important;
		font-size: 0 !important;
		line-height: 0 !important;
		opacity: 0 !important;
		position: absolute !important;
		left: -9999px !important;
		width: 0 !important;
		max-width: 0 !important;
	}}
	
	</style>
	"""

def get_translations(lang=None):
	"""Dil bazlı çeviri sözlüğü"""
	lang = lang or frappe.local.lang or "en"
	lang_code = lang.split("-")[0] if "-" in lang else lang
	
	translations = {
		"tr": {
			"contact": "İletişim",
			"email": "E-Posta",
			"tel": "Tel",
			"copyright": "Telif Hakkı 2019 - 2025 | North Medical Germany | Tüm Hakları Saklıdır"
		},
		"en": {
			"contact": "Contact",
			"email": "E-Mail",
			"tel": "Tel",
			"copyright": "Copyright 2019 - 2025 | North Medical Germany | All Rights Reserved"
		},
		"de": {
			"contact": "Kontakt",
			"email": "E-Mail",
			"tel": "Tel",
			"copyright": "Copyright 2019 - 2025 | North Medical Germany | Alle Rechte vorbehalten"
		},
		"fr": {
			"contact": "Contact",
			"email": "E-Mail",
			"tel": "Tél",
			"copyright": "Copyright 2019 - 2025 | North Medical Germany | Tous droits réservés"
		},
		"it": {
			"contact": "Contatto",
			"email": "E-Mail",
			"tel": "Tel",
			"copyright": "Copyright 2019 - 2025 | North Medical Germany | Tutti i diritti riservati"
		}
	}
	
	return translations.get(lang_code, translations["en"])

def get_footer_contact_html(lang=None):
	"""Dil bazlı footer contact HTML döndürür"""
	trans = get_translations(lang)
	
	return f"""<h5 class="footer-group-label">{trans['contact']}</h5>
<p><strong>North Medical Germany</strong></p>
<p>Medzenith GmbH</p>
<p>Mühlenweg 131-139, 22844 Norderstedt</p>
<p><a href="mailto:info@north-medical-germany.com">{trans['email']}: info@north-medical-germany.com</a></p>
<p><a href="tel:+494021995055">{trans['tel']}: +49 40 21 99 50 55</a></p>"""

def get_back_to_top_html():
	"""Back to Top butonu HTML ve JavaScript"""
	return """
	<!-- Back to Top Button -->
	<button id="back-to-top" aria-label="Back to top">
		<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
			<path d="M18 15l-6-6-6 6"/>
		</svg>
	</button>
	
	<script>
	(function() {
		// Back to Top Button
		const backToTopButton = document.getElementById('back-to-top');
		
		if (!backToTopButton) return;
		
		// Show/hide button based on scroll position
		window.addEventListener('scroll', function() {
			if (window.pageYOffset > 300) {
				backToTopButton.classList.add('show');
			} else {
				backToTopButton.classList.remove('show');
			}
		});
		
		// Smooth scroll to top
		backToTopButton.addEventListener('click', function(e) {
			e.preventDefault();
			window.scrollTo({
				top: 0,
				behavior: 'smooth'
			});
		});
	})();
	</script>
	"""

def update_website_context(context):
	"""Website context'e CSS ekle ve custom field'ları ekle"""
	# Override portal sidebar items function for language-aware caching
	# This is done here because update_website_context is called after all modules are loaded
	try:
		import frappe.website.utils
		from north_medical_portal.utils.portal_menu import get_portal_sidebar_items
		if not hasattr(frappe.website.utils.get_portal_sidebar_items, '_overridden'):
			frappe.website.utils.get_portal_sidebar_items = get_portal_sidebar_items
			frappe.website.utils.get_portal_sidebar_items._overridden = True
	except (ImportError, AttributeError):
		pass
	# Login sayfası için özel işlemler
	if hasattr(frappe.local, 'request') and frappe.local.request:
		path = getattr(frappe.local.request, 'path', '') or ''
		if path == "/login" or path.endswith("/login"):
			# no_header'ı False yaparak navbar'ı göster
			context.no_header = False
			# Login sayfası için ekstra JavaScript ekle
			if context.get("head_include"):
				context["head_include"] += """
<script>
(function() {
	function removeLoginH4() {
		var h4s = document.querySelectorAll('.page-card-head h4');
		h4s.forEach(function(h4) { h4.remove(); });
	}
	removeLoginH4();
	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', removeLoginH4);
	}
	window.addEventListener('load', removeLoginH4);
	if (window.MutationObserver) {
		var obs = new MutationObserver(function() { removeLoginH4(); });
		obs.observe(document.body, { childList: true, subtree: true });
	}
})();
</script>
"""
			else:
				context["head_include"] = """
<script>
(function() {
	function removeLoginH4() {
		var h4s = document.querySelectorAll('.page-card-head h4');
		h4s.forEach(function(h4) { h4.remove(); });
	}
	removeLoginH4();
	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', removeLoginH4);
	}
	window.addEventListener('load', removeLoginH4);
	if (window.MutationObserver) {
		var obs = new MutationObserver(function() { removeLoginH4(); });
		obs.observe(document.body, { childList: true, subtree: true });
	}
})();
</script>
"""
	
	# CSS ekle
	if context.get("head_include"):
		context["head_include"] += get_website_css()
	else:
		context["head_include"] = get_website_css()
	
	# Back to Top butonu ekle
	if context.get("body_include"):
		context["body_include"] += get_back_to_top_html()
	else:
		context["body_include"] = get_back_to_top_html()
	
	# Dil bazlı içerikler - Frappe'de lang frappe.local.lang'da
	lang = frappe.local.lang or "en"
	trans = get_translations(lang)
	
	# Footer contact HTML - Dil bazlı
	context["footer_contact_html"] = get_footer_contact_html(lang)
	
	# Copyright - Dil bazlı (Website Settings'teki değeri override et)
	context["copyright"] = trans["copyright"]
	
	return context
