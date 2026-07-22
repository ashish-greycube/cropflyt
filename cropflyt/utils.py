import frappe
import json
from werkzeug.wrappers import Response
from frappe.integrations.utils import create_request_log

@frappe.whitelist(allow_guest=True)
def on_whatsapp_message():
    # 1. Handle Meta's GET Verification Handshake
    if frappe.request.method == "GET":
        params = frappe.request.args
        
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge")
        
        MY_VERIFY_TOKEN = ""
        
        if mode == "subscribe" and token == MY_VERIFY_TOKEN:
            return Response(challenge, mimetype='text/plain', status=200)
        else:
            return Response("Forbidden", mimetype='text/plain', status=403)

    # 2. Handle Meta's POST Event Notifications (Status Drops & Incoming Messages)
    elif frappe.request.method == "POST":
        integration_request = None
        try:
            # Parse Meta's payload data
            data = json.loads(frappe.request.data)
            
            # Log the full payload and grab the document object
            integration_request = create_request_log(
                data=frappe._dict(data),
                integration_type="Remote",
                service_name="Whatsapp Webhook Response",
            )
            
            has_errors = False

            if "entry" in data:
                for entry in data["entry"]:
                    for change in entry.get("changes", []):
                        value = change.get("value", {})
                        
                        # Process Message Outbound Statuses (Sent, Delivered, Read, Failed)
                        if "statuses" in value:
                            for status_update in value["statuses"]:
                                message_id = status_update.get("id")
                                recipient_id = status_update.get("recipient_id")
                                
                                # If there's an error block, log it explicitly
                                if "errors" in status_update:
                                    has_errors = True
                                    for error in status_update["errors"]:
                                        error_code = error.get("code")
                                        error_msg = error.get("message")
                                        
                                        frappe.log_error(
                                            title=f"WhatsApp Message Failed ({message_id})",
                                            message=f"To: {recipient_id}\nError Code: {error_code}\nMessage: {error_msg}"
                                        )
            
            # Update status using frappe.db.set_value
            if integration_request:
                status = "Failed" if has_errors else "Completed"
                frappe.db.set_value("Integration Request", integration_request.name, "status", status)

            return Response("EVENT_RECEIVED", mimetype='text/plain', status=200)

        except Exception as e:
            frappe.log_error(title="WhatsApp Webhook Exception", message=frappe.get_traceback())
            
            # If a syntax/runtime exception occurs, update status to Failed
            if integration_request:
                frappe.db.set_value("Integration Request", integration_request.name, "status", "Failed")
                
            return Response("EVENT_RECEIVED", mimetype='text/plain', status=200)