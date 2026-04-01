# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChemicalCF(Document):
	def validate(self):
		acre_to_bigha = frappe.db.get_single_value("CropFlyt Settings","acre_to_bigha_conversion")
		if acre_to_bigha and acre_to_bigha > 0:
			self.dose_per_bigha = self.recommended_dose_per_acre / acre_to_bigha
		else:
			frappe.throw("Please set the value of <b>Acre To Bigha</b> in Cropflyt Settings")