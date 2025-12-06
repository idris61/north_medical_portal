from frappe.model.document import Document


class ProductBadge(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		badge_alt_text: DF.Data | None
		badge_image: DF.AttachImage
		badge_link: DF.Data | None
		badge_name: DF.Data
		display_order: DF.Int
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types
	pass





