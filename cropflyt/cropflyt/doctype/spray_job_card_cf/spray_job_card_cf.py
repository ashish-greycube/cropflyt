# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class SprayJobCardCF(Document):
    def on_submit(self):
        self.create_sales_invoice_on_submit()

    def validate(self):
        self.validate_sprayed_area()
        self.calculate_expense_amount()  
            
    def calculate_expense_amount(self):
        total_amount = 0
        for row in self.expense_tracking:
            row.amount = (row.quantity or 0) * (row.rate or 0)
            total_amount += row.amount
        self.expense_total_amount = total_amount

    def validate_sprayed_area(self):
        area = frappe.db.get_value("Field CF", self.field_id,"area_bigha")
        if area > 0 and self.area_sprayed_bigha > area:
            frappe.throw("Area Sprayed Bigha is Greater than The Actual Area of Field.")

    def create_sales_invoice_on_submit(self):
        if self.area_sprayed_bigha > 0:
            if frappe.db.get_value("CropFlyt Settings", "CropFlyt Settings", "service_item"):
                invoice = frappe.new_doc("Sales Invoice")
                invoice.update({
                    'status': "Draft",
                    'customer': self.farmer_id,
                    'due_date': frappe.utils.today(),
                    'company': frappe.defaults.get_global_default("company") or "CROPFLYT Technologies LLP",
                    'custom_spray_job_id': self.name,
                    'custom_payment_method': self.payment_method
                })

                invoice.append("items", {
                    "item_code": frappe.db.get_value("CropFlyt Settings", "CropFlyt Settings", "service_item"),
                    "qty" : self.area_sprayed_bigha,
                })

                invoice.save(ignore_permissions=True)
                invoice.submit()
                self.reload()
                frappe.msgprint("Sales Invoice {0} Created Successfully.".format(invoice.name), alert=True)
            else:
                frappe.throw("Please set the Service Item in CropFlyt Settings.")

    @frappe.whitelist()
    def check_for_existing_field_id_else_create_new(self):
        if self.crop_type and self.farmer_id:
            isExisting = frappe.db.exists("Field CF", {"crop_type": self.crop_type, "farmer_id": self.farmer_id})
            if isExisting:
                self.field_id = frappe.db.get_value("Field CF", {"crop_type": self.crop_type, "farmer_id": self.farmer_id}, "name")
            else:
                field_doc = frappe.new_doc("Field CF")
                field_doc.crop_type = self.crop_type
                field_doc.farmer_id = self.farmer_id
                field_doc.area_bigha = self.area_sprayed_bigha
                field_doc.save()
                self.field_id = field_doc.name
        else:
            frappe.throw("Please select Farmer ID first.")

    @frappe.whitelist()
    def set_sales_invoice_status(self):
        if self.sales_invoice_reference:
            si_status = frappe.db.get_value("Sales Invoice", self.sales_invoice_reference, "status")
            frappe.db.set_value("Spray Job Card CF", self.name, "sales_invoice_status", si_status)


@frappe.whitelist()
def create_invoice(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.company = frappe.defaults.get_global_default("company") or "CROPFLYT Technologies LLP"
        target.due_date = frappe.utils.today()
        target.status = "Draft"
        target.append("items", {
            "item_code": frappe.db.get_value("CropFlyt Settings", "CropFlyt Settings", "service_item"),
            "qty" : source.area_sprayed_bigha,
        })

    doc = get_mapped_doc("Spray Job Card CF", source_name, {
        "Spray Job Card CF" : {
            "doctype": "Sales Invoice",
            "field_map": {
                "name" : "custom_spray_job_id",
                "farmer_id": "customer",
                "mobile_number":"custom_farmer_mobile_no"
            }
        }
    }, target_doc, set_missing_values)

    doc.run_method("set_missing_values")
    doc.run_method("calculate_taxes_and_totals")

    return doc