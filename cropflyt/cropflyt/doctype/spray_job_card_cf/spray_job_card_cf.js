// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Spray Job Card CF", {
    refresh(frm) {
        frm.set_query("field_id", () => {
            return {
                filters: {
                    farmer_id: frm.doc.farmer_id
                }
            }
        })

        if (frm.doc.status == "Completed(Ready For billing)" && frm.doc.docstatus == 1 && frm.doc.sales_invoice_reference == undefined) {
            frm.add_custom_button("Create Invoice", () => {
                frappe.db.get_single_value("CropFlyt Settings", "service_item").then(value => {
                    if (value) {
                        frappe.model.open_mapped_doc({
                            method: "cropflyt.cropflyt.doctype.spray_job_card_cf.spray_job_card_cf.create_invoice",
                            frm: frm
                        });
                    } else {
                        frappe.throw("Set Item in CropFlyt Settings Then Procced.")
                    }
                })
            })
        }
    },

    crop_type: function (frm) {
        frm.call({
            method: "check_for_existing_field_id_else_create_new",
            doc: frm.doc,
        })
    }
});