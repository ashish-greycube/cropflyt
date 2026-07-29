import io
import json
import hmac
import frappe
import hashlib
import pyqrcode
import requests

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
        frappe.db.set_value("Spray Job Card CF", self.custom_spray_job_id, "sales_invoice_status", self.status)

# ==================================================================================
# On Submit Of Sales Invoice QR Generated & Payment Request Created
# ==================================================================================
def on_submit_sales_invoice_create_payment_request(self, method=None):
    # 1. Generate One Time Usable QRCode With Fixed Amount; Customer Can Scan With Any UPI App
    generate_razorpay_qr(self)

    # Create Payment Request For Sales Invoice
    # payment_gateway_account = frappe.get_doc("Payment Gateway Account", {
    #     "company": self.company,
    #     "payment_gateway" : "Razorpay",
    # })
    # if self.status == "Unpaid" and self.custom_spray_job_id:
    #     pr = frappe.new_doc("Payment Request")

    #     pr.payment_request_type = "Inward"
    #     pr.company = self.company
    #     pr.party_type = "Customer"
    #     pr.party = self.customer
    #     pr.party_name = self.customer_name
    #     pr.reference_doctype = "Sales Invoice"
    #     pr.reference_name = self.name
    #     pr.grand_total = self.grand_total
    #     pr.outstanding_amount = self.outstanding_amount
    #     pr.currency = self.currency
    #     pr.party_account_currency = self.currency
    #     pr.email_to = self.owner
    #     pr.payment_gateway_account = payment_gateway_account.name
    #     pr.subject = "Payment Request for {0}".format(self.name)

    #     pr.payment_gateway = payment_gateway_account.payment_gateway
    #     pr.payment_account = payment_gateway_account.payment_account

    #     pr.save(ignore_permissions=True)
    #     pr.submit()

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

# ==================================================================================
# UPI QR Code Function
# ==================================================================================
def generate_razorpay_qr(doc, method=None):
    # Only generate if there is an outstanding amount
    if doc.outstanding_amount <= 0:
        return

    # Only generate if payment mode in Spray Job Card is Razorpay QR
    if not doc.custom_spray_job_id or not doc.custom_payment_method:
        return

    if doc.custom_spray_job_id and doc.custom_payment_method and doc.custom_payment_method != "Razorpay QR":
        return

    # Razorpay credentials 
    razorpay_settings = frappe.get_doc("Razorpay Settings")
    if razorpay_settings:
        API_KEY = razorpay_settings.api_key
        API_SECRET = razorpay_settings.get_password("api_secret")
    else:
        frappe.throw("Can not find Razorpay Settings")

    # Razorpay expects amounts in paise (multiply INR by 100)
    amount_in_paise = int(doc.outstanding_amount * 100)

    URL = "https://api.razorpay.com/v1/payments/qr_codes"
    
    # We pass the Sales Invoice ID in the 'notes' object. 
    payload = {
        "type": "upi_qr",
        "name": f"UPI QR Code For Sales Invoice {doc.name}",
        "usage": "single_use",
        "fixed_amount": True,
        "payment_amount": amount_in_paise,
        "description": f"Payment for Sales Invoice {doc.name}",
        "notes": {
            "sales_invoice": doc.name
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(URL, auth=(API_KEY, API_SECRET), data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        qr_data = response.json()

        # Razorpay returns an image_url for the QR code
        qr_image_url = qr_data.get("image_url")
        
        # Save the URL to your custom field
        frappe.db.set_value("Sales Invoice", doc.name, "custom_qr_code_file_path", qr_image_url)
        frappe.db.set_value("Spray Job Card CF", doc.custom_spray_job_id, "razorpay_qr_code_path", qr_image_url)

    except Exception as e:
        frappe.log_error(title="Razorpay QR Generation Failed", message=str(e))


# ==================================================================================
# Webhook Callback Function
# ==================================================================================
@frappe.whitelist(allow_guest=True)
def on_payment_authorized():
    settings = frappe.get_doc("CropFlyt Settings")
    if not settings:
        frappe.throw("CropFlyt Settings Not Found.")
        return

    if settings and (not settings.default_paid_to_account or not settings.default_paid_from_account):
        frappe.throw("Please set Default Paid To & Paid From Accounts in Cropflyt Settings")
        return

    
    WEBHOOK_SECRET = settings.get_password("webhook_secret", raise_exception=False)
    data = frappe.request.get_data()
    
    received_signature = frappe.get_request_header("X-Razorpay-Signature")
    if not received_signature:
        frappe.log_error(title="signature error", message="Signature Not Received")

    # Calculate expected HMAC hex digest using SHA256
    expected_signature = hmac.new(
        bytes(WEBHOOK_SECRET, 'utf-8'),
        data,
        hashlib.sha256
    ).hexdigest()

    # Securely compare signatures to protect against timing attacks
    if not hmac.compare_digest(expected_signature, received_signature):
        frappe.log_error(title="Invalid webhook signature verification failed.", message="frappe.PermissionError")
    
    # Set user as Administrator to avoid permission issue
    frappe.set_user("Administrator")
    
    event_data = json.loads(data)
    event = event_data.get("event")
    
    if event == "payment.captured":  
        payload = event_data.get("payload", {})
        payment_entity = payload.get("payment", {}).get("entity", {})
        notes = payment_entity.get("notes", "")

        amount_paid = payment_entity.get("amount") / 100 
        if notes: 
            invoice_id = notes.get("sales_invoice")
            invoice = frappe.get_doc("Sales Invoice", invoice_id)
            if invoice.docstatus == 1 and invoice.outstanding_amount > 0:
                try:
                    pe = frappe.new_doc("Payment Entry") 
                    pe.update({
                        "payment_type": "Receive",
                        "party_type": "Customer",
                        "party": invoice.customer,
                        "paid_amount": amount_paid,
                        "received_amount": amount_paid,
                        "paid_from" : settings.default_paid_from_account,
                        "paid_to": settings.default_paid_to_account,
                        "paid_from_account_currency" : "INR",
                        "paid_to_account_currency" : "INR",
                        "reference_no": payment_entity.get("id"),
                        "reference_date" : frappe.utils.today()
                    })

                    pe.append("references", {
                        "reference_doctype": "Sales Invoice",
                        "reference_name": invoice.name,
                        "allocated_amount": amount_paid
                    })

                    pe.insert(ignore_permissions=True)
                    pe.submit()
                    frappe.db.commit()
                except Exception as e:
                    frappe.log_error(title="Crashed", message=frappe.get_traceback())