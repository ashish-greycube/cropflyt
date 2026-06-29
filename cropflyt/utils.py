import frappe
from frappe import Response

@frappe.whitelist(allow_guest=True)
def on_whatsapp_message():
    request = frappe.request

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    VERIFY_TOKEN = "GC@2026"

    if mode == "subscribe" and token == VERIFY_TOKEN:
        response = Response()
        response.status_code = 200
        response.set_data(challenge)
        response.content_type = "text/plain"
        return response