import frappe

@frappe.whitelist()
def check_for_existing_field_id_else_create_new(crop_type, farmer_id):
    if crop_type and farmer_id:
        # frappe.session.user is resolved from the mobile app's api_key/api_secret,
        # so these checks apply against whichever user the app is logged in as.
        frappe.has_permission("Field CF", ptype="read", throw=True)

        field_id = None
        isExisting = frappe.db.exists("Field CF", {"crop_type": crop_type, "farmer_id": farmer_id})
        if isExisting:
            field_id = frappe.db.get_value("Field CF", {"crop_type": crop_type, "farmer_id": farmer_id}, "name")
        else:
            field_doc = frappe.new_doc("Field CF")
            field_doc.crop_type = crop_type
            field_doc.farmer_id = farmer_id
            field_doc.check_permission("create")
            field_doc.save()
            frappe.db.commit()
            field_id = field_doc.name
        return field_id
    return "Provide Croptype & Farmer ID to check for existing field"

@frappe.whitelist()
def create_sales_invoice_on_submit(docname):
    self = None
    if docname:
        self = frappe.get_doc("Spray Job Card CF", docname)
        self.check_permission("read")
    if self and self.area_sprayed_bigha > 0:
        if frappe.db.get_value("CropFlyt Settings", "CropFlyt Settings", "service_item"):
            invoice = frappe.new_doc("Sales Invoice")
            invoice.update({
                'status': "Draft",
                'customer': self.farmer_id,
                'due_date': frappe.utils.today(),
                'company': frappe.defaults.get_global_default("company") or "CROPFLYT Technologies LLP",
                'custom_spray_job_id': self.name,
            })

            invoice.append("items", {
                "item_code": frappe.db.get_value("CropFlyt Settings", "CropFlyt Settings", "service_item"),
                "qty" : self.area_sprayed_bigha,
            })

            invoice.check_permission("create")
            invoice.save()
            invoice.check_permission("submit")
            invoice.submit()
            frappe.db.commit()
            return "Sales Invoice Created Successfully: {0}".format(invoice.name)
        else:
            return "Please set the Service Item in CropFlyt Settings."
    else:
        return "Cannot create sales invoice for sprayed areas 0 Bigha"