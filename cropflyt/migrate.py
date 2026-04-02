import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.desk.page.setup_wizard.setup_wizard import make_records

def after_migrate():
    custom_fields = {
        "Customer" : [
            {
                'fieldname' : 'custom_district',
                'fieldtype' : 'Link',
                'label' : 'District',
                'options' : 'District CF',
                'insert_after' : 'territory',
                'allow_in_quick_entry': 1,
                'reqd': 1,
                'is_custom_field' : 1,
                'is_system_generated' : 0,
            },
            {
                'fieldname' : 'custom_village',
                'fieldtype' : 'Link',
                'label' : 'Village',
                'options' : 'Village CF',
                'insert_after' : 'custom_district',
                'allow_in_quick_entry': 1,
                'reqd': 1,
                'is_custom_field' : 1,
                'is_system_generated' : 0,
            },
            {
                'fieldname' : 'custom_primary_crop',
                'fieldtype' : 'Link',
                'label' : 'Primary Crop',
                'options' : 'Crop Type CF',
                'insert_after' : 'gender',
                'allow_in_quick_entry': 1,
                'reqd': 1,
                'is_custom_field' : 1,
                'is_system_generated' : 0,
            },
            {
                'fieldname' : 'custom_total_land_bigha',
                'fieldtype' : 'Float',
                'label' : 'Total Land Bigha',
                'insert_after' : 'custom_primary_crop',
                'precision': 2,
                'is_custom_field' : 1,
                'read_only': 1,  
                'is_system_generated' : 0,
            },
            {
                'fieldname' : 'custom_notes',
                'fieldtype' : 'Small Text',
                'label' : 'Notes',
                'insert_after' : 'custom_village',
                'is_custom_field' : 1,
                'allow_in_quick_entry': 1,
                'is_system_generated' : 0,
            },
        ],
        "Sales Invoice" : [
            {
                'fieldname' : 'custom_spray_job_id',
                'fieldtype' : 'Link',
                'label' : 'Spray Job Id',
                'options' : 'Spray Job Card CF',
                'insert_after' : 'customer',
                'read_only': 1, 
                'is_custom_field' : 1,
                'is_system_generated' : 0,
            },
            {
                'fieldname' : 'custom_farmer_mobile_no',
                'fieldtype' : 'Data',
                'label' : 'Farmer Mobile No',
                'insert_after' : 'custom_spray_job_id',
                'read_only': 1, 
                'is_custom_field' : 1,
                'is_system_generated' : 0,
            }
        ],
        "Lead":[
            {
                'fieldname' : 'custom_info_section',
                'fieldtype' : 'Section Break',
                'insert_after' : 'phone_ext',
                'is_custom_field' : 1,
                'is_system_generated' : 0,
            },
            {
                'fieldname' : 'custom_district',
                'fieldtype' : 'Link',
                'label' : 'District',
                'options' : 'District CF',
                'insert_after' : 'custom_info_section',
                'allow_in_quick_entry': 1,
                'reqd': 1,
                'is_custom_field' : 1,
                'is_system_generated' : 0,
            },
            {
                'fieldname' : 'custom_village',
                'fieldtype' : 'Link',
                'label' : 'Village',
                'options' : 'Village CF',
                'insert_after' : 'custom_district',
                'allow_in_quick_entry': 1,
                'reqd': 1,
                'is_custom_field' : 1,
                'is_system_generated' : 0,
            },
            {
                'fieldname' : 'custom_info_column_break',
                'fieldtype' : 'Column Break',
                'insert_after' : 'custom_village',
                'is_custom_field' : 1,
                'is_system_generated' : 0,
            },
            {
                'fieldname' : 'custom_primary_crop',
                'fieldtype' : 'Link',
                'label' : 'Crop Type',
                'options' : 'Crop Type CF',
                'insert_after' : 'custom_info_column_break',
                'allow_in_quick_entry': 1,
                'reqd': 1,
                'is_custom_field' : 1,
                'is_system_generated' : 0,
            },
            {
                'fieldname' : 'custom_crop_column_break',
                'fieldtype' : 'Column Break',
                'insert_after' : 'custom_primary_crop',
                'is_custom_field' : 1,
                'is_system_generated' : 0,
            },
            {
                'fieldname' : 'custom_total_land_bigha',
                'fieldtype' : 'Float',
                'label' : 'Total Land Bigha',
                'insert_after' : 'custom_crop_column_break',
                'precision': 2,
                'is_custom_field' : 1, 
                'is_system_generated' : 0,
            },
        ]
    }
    
    print("Adding Custom Fields In Customer and Sales Invoice and Lead")
    for dt, fields in custom_fields.items():
        print("*******\n %s: " % dt, [d.get("fieldname") for d in fields])
    create_custom_fields(custom_fields)