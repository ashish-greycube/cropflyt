// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Spray Job Card CF", {
	refresh(frm) {
        frm.set_query("field_id",()=>{
            return{
                filters:{
                    farmer_id:frm.doc.farmer_id
                }
            }
        })
        
        if(frm.doc.status == "Completed(Ready For billing)" && frm.doc.docstatus == 1){
            frm.add_custom_button("Create Invoice",()=>{
                frappe.db.get_single_value("CropFlyt Settings","service_item").then(value=>{
                    if(value){
                        frappe.model.open_mapped_doc({
                            method: "cropflyt.cropflyt.doctype.spray_job_card_cf.spray_job_card_cf.create_invoice", 
                            frm:frm
                        });
                    }else{
                        frappe.throw("Set Item in CropFlyt Settings Then Procced.")
                    }
                })
            })
        }
	}, 
    completion_date(frm){
        if(frm.doc.completion_date && (frm.doc.completion_date < frm.doc.scheduled_date)){
            frappe.throw("Completion Date Must be Greater Than Or Equal to Scheduled Date")
        }
    }

});


frappe.ui.form.on('Drone Flight Detail', {
    drone_details_add: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.drone_id = frm.doc.drone_assigned
        row.pilot_name = frm.doc.pilot_name
    }
});
