# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    if not filters : filters = {}
    columns, data = [], []
    
    columns = get_columns()
    data = get_data(filters)
    
    if not data :
        frappe.msgprint('No Records Found')
        return columns, data

    return columns, data


def get_columns():
	columns = [
		{
			"fieldname" :"farmer_name",
			"fieldtype" :"Link",
			"label" :_("Farmer Name"),
			"options" : "Customer",
			"width" :150
		},
		{
			"fieldname" :"total_bigha",
			"fieldtype" :"Float",
			"label" :_("Total Bigha"),
			'precision': 2,
			"width" :120
		},
		{
			"fieldname" :"per_bigha_amt",
			"fieldtype" :"Currency",
			"label" :_("Incentive Rate Per Bigha"),
			"options" : "Customer",
			"width" :150
		},
		{
			"fieldname" :"total",
			"fieldtype" :"Currency",
			"label" :_("Total Amount"),
			"width" :120
		},
	]
	
	return columns


def get_data(filters):
    conditions = get_conditions(filters)
    data = frappe.db.sql("""
		SELECT 
			sjc.farmer_id as farmer_name, 
			SUM(sjc.area_sprayed_bigha) as total_bigha,
			p.incentive_rate_per_bigha as per_bigha_amt
		FROM `tabSpray Job Card CF` AS sjc
		RIGHT JOIN `tabPilot CF` AS p
		ON sjc.pilot_name = p.name
		WHERE sjc.status IN ("Completed(Ready For billing)" ,"Billed", "Paid") {0}
		GROUP BY sjc.farmer_id 
		""".format(conditions),as_dict=1,debug=1)
    
    f_data = []
    total_amount = 0
    total_bigha = 0
    per_bigha_amt = 0
    for d in data:
        total = d["total_bigha"] * d["per_bigha_amt"]
        f_data.append({
			"farmer_name":d["farmer_name"],
			"total_bigha":d["total_bigha"],
			"per_bigha_amt":d["per_bigha_amt"],
			"total":total
		})
        
        total_amount += total 
        total_bigha += d["total_bigha"]
        per_bigha_amt = d["per_bigha_amt"]
        
    f_data.append({
		"farmer_name":"Total",
		"total_bigha":total_bigha,
		"per_bigha_amt":per_bigha_amt,
		"total":total_amount
	})
    
    return f_data

def get_conditions(filters):
    conditions = ""

    if filters.get("pilot"):
        conditions += " AND sjc.pilot_name = '{0}'".format(filters["pilot"])

    if filters.get("from_date") and filters.get("to_date"):
        conditions += "AND sjc.scheduled_date BETWEEN '{0}' AND '{1}'".format(filters["from_date"],filters["to_date"])
        
    return conditions