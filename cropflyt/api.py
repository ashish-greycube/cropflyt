import frappe
import pyqrcode
import io

def create_customer_contact(self, method=None):
    if self.custom_mobile_no and self.customer_name:
        contact = frappe.new_doc("Contact")
        contact.first_name = self.customer_name

        contact.append('phone_nos', {
            'phone': self.custom_mobile_no,
            'is_primary_phone': 1
        })

        contact.append('links', {
            'link_doctype': 'Customer',
            'link_name': self.name
        })

        contact.is_primary_contact = 1
        contact.save(ignore_permissions=True)

def set_sales_invoice_reference(self, method=None):
    if self.custom_spray_job_id:
        frappe.db.set_value("Spray Job Card CF", self.custom_spray_job_id, "sales_invoice_reference", self.name)

def on_submit_sales_invoice_create_payment_request(self, method=None):
    payment_gateway_account = frappe.get_doc("Payment Gateway Account", {
        "company": self.company,
        "payment_gateway" : "Razorpay",
    })
    if self.status == "Unpaid" and self.custom_spray_job_id:
        pr = frappe.new_doc("Payment Request")

        pr.payment_request_type = "Inward"
        pr.company = self.company
        pr.party_type = "Customer"
        pr.party = self.customer
        pr.party_name = self.customer_name
        pr.reference_doctype = "Sales Invoice"
        pr.reference_name = self.name
        pr.grand_total = self.grand_total
        pr.outstanding_amount = self.outstanding_amount
        pr.currency = self.currency
        pr.party_account_currency = self.currency
        pr.email_to = self.owner
        pr.payment_gateway_account = payment_gateway_account.name
        pr.subject = "Payment Request for {0}".format(self.name)

        pr.payment_gateway = payment_gateway_account.payment_gateway
        pr.payment_account = payment_gateway_account.payment_account

        pr.save(ignore_permissions=True)
        pr.submit()

def after_insert_save_qr_code_to_sales_invoice(self, method=None):
    if self.reference_doctype and self.reference_name:
        qr = pyqrcode.create(self.payment_url)
        buffer = io.BytesIO()
        qr.png(buffer, scale=4)
        buffer.seek(0)

        _file = frappe.new_doc("File")
        _file.update({
            "file_name": "QR-{0}-{1}.png".format(self.name, self.creation),
            "is_private": 0,
            "content": buffer.getvalue(),
            "file_type": "PNG",
        })
        _file.insert(ignore_permissions=True)

        frappe.db.set_value(self.reference_doctype, self.reference_name, "custom_qr_code_file_path", _file.file_url)


@frappe.whitelist(allow_guest=True)
def on_payment_authorized(response):
    frappe.errprint(response)
    frappe.errprint("="*30)
    data = frappe.request.get_data()
    event_data = frappe.parse_json(data)
    frappe.errprint(data, event_data)
    event = event_data.get("event")
    
    if event == "payment.captured":
        payload = event_data.get("payload", {})
        payment_entity = payload.get("payment", {}).get("entity", {})
        references = payment_entity.get("notes", {})
        amount_paid = payment_entity.get("amount") / 100 

        if references:
            invoice_id = references[0].get("sales_invoice_id")
            invoice = frappe.get_doc("Sales Invoice", invoice_id)
            if invoice.docstatus == 1 and invoice.outstanding_amount > 0:
                pe = frappe.new_doc("Payment Entry") 
                pe.update({
                    "payment_type": "Receive",
                    "party_type": "Customer",
                    "party": invoice.customer,
                    "paid_amount": amount_paid,
                    "received_amount": amount_paid,
                })

                pe.append("references", {
                    "reference_doctype": "Sales Invoice",
                    "reference_name": invoice.name,
                    "allocated_amount": amount_paid
                })

                pe.insert(ignore_permisssions=True)
                pe.submit()