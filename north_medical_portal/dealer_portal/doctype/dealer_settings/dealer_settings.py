"""
Dealer Settings controller.
"""
from __future__ import annotations

import frappe
from frappe.model.document import Document


class DealerSettings(Document):
	"""Bayi portalı stok transfer ayarlarını saklar."""

	def validate(self) -> None:
		"""Gerekli alanları doğrula."""
		if not self.default_source_warehouse:
			frappe.throw("Kaynak depo zorunludur.")







