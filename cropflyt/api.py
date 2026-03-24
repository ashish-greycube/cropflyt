import frappe

def validate_customer_number(self, method=None):
    if self.custom_farmer_mobile_no and len(self.custom_farmer_mobile_no) > 10:
        frappe.throw("Invalid input: Mobile no must be equal to 10 digit.")
        return