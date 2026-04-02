// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Technician Incentive Report"] = {
	filters: [
		{
			"fieldname": "pilot",
			"label": __("Pilot"),
			"fieldtype": "Link",
			"options":"Pilot CF",
			"reqd": 1,
		},
		{
			"fieldname":"from_date",
			"fieldtype":"Date",
			"label":__("From Date"),
			"default":frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname":"to_date",
			"fieldtype":"Date",
			"label":__("To Date"),
			"default":frappe.datetime.get_today()
		},
	],
	"formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        if(data.farmer_name == "Total"){
			value = `<span style="font-weight: bold;">${value}</span>`;
		}
        return value;
    }
};
