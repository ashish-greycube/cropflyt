# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class SprayJobCardCF(Document):
    def validate(self):
        if self.status == "Completed(Ready For billing)" and not self.post_spray_photo_reference:
            frappe.throw("Please upload Post-Spray Photo before marking the job as Completed.")
            
        if self.completion_date and self.completion_date < self.scheduled_date:
            frappe.throw("Completion Date Must be Greater Than Or Equal to Scheduled Date")
            
        total_amount = 0
        for row in self.expense_tracking:
            total_amount += row.amount
            
        self.expense_total_amount = total_amount
        
        area = frappe.db.get_value("Field CF",self.field_id,"area_bigha")
        if(self.area_sprayed_bigha > area):
            frappe.throw("Area Sprayed Bigha is Greater than The Actual Area of Field.")
            
    def before_validate(self):
        for row in self.expense_tracking:
            row.amount = (row.quantity or 0) * (row.rate or 0)
    

@frappe.whitelist()
def create_invoice(source_name, target_doc=None):
    area_sprayed = frappe.db.get_value("Spray Job Card CF", source_name,"area_sprayed_bigha")
    item = frappe.db.get_single_value("CropFlyt Settings","service_item")
    
    def set_missing_values(source,target):
        target.append("items",{
        "item_code":item,
        "qty":area_sprayed
        })
        target.status="Draft"
        
    doclist = get_mapped_doc(
        "Spray Job Card CF", 
        source_name, 
        {
            "Spray Job Card CF": {
                "doctype": "Sales Invoice",
                "field_map": {
                    "name":"custom_spray_job_id",
                    "farmer_id": "customer"
                }
            }
        }, 
        target_doc,
        set_missing_values
    )
    doclist.run_method("set_missing_values")
    doclist.run_method("calculate_taxes_and_totals")
    
    return doclist