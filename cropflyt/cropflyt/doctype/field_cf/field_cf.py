# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FieldCF(Document):
    def after_insert(self):
        update_farmer_land(self.farmer_id)
    
    def on_update(self):
        update_farmer_land(self.farmer_id)
    
def update_farmer_land(farmer):
    total_land = frappe.db.sql("""
			SELECT SUM(area_bigha) as total
			FROM `tabField CF`
			WHERE farmer_id = '{0}'
        """.format(farmer),as_dict=1) 
    
    total = total_land[0]["total"] or 0
    # print("="*100,"Total Land :",total_land[0]["total"])
    # print(total_land)
    
    frappe.db.set_value("Customer",farmer,"custom_total_land_bigha",total)