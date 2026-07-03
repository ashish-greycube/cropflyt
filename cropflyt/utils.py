import frappe
from werkzeug.wrappers import Response

@frappe.whitelist(allow_guest=True)
def on_whatsapp_message():
    args = frappe.request.args

    # 1. Handle Meta's Webhook Verification
    if (
        args.get("hub.mode") == "subscribe"
        and args.get("hub.verify_token") == "GC@2026"
    ):
        challenge = args.get("hub.challenge")

        # Return a raw Werkzeug Response with plain text
        return Response(challenge, mimetype="text/plain", status=200)

    # 2. Handle unauthorized requests
    return Response("Forbidden", mimetype="text/plain", status=403)