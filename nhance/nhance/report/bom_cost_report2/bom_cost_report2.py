
# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from datetime import datetime
import datetime
from datetime import date, timedelta
import calendar
import time
import math
import json
import ast
import sys
#reload(sys)

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	global bom
	bom = ""
	bom = filters.get("bom")
	company = filters.get("company")
	print ("company and filters=========",company)
	print ("bom and filters=========",bom)
	bom_item = bom_details(company , bom)
	total_bom_qty = 0.0
	total_last_purchase_rate = 0.0
	total_item_cose_base_on_last_purchase = 0.0
	total_stock_valuation_price = 0.0
	total_item_cose_based_on_valuation_rate = 0.0
	total_max_purchase = 0.0
	total_avg_purchase = 0.0
	total_min_purchase = 0.0
	total_llp = 0.0
	total_item_amount_based_on_conversion = 0.0
	if bom is not None:
		for bom_i in bom_item:
			bom_name = bom_i.bom_name
			bom_item = bom_i.bo_item
			bo_qty = bom_i.bo_qty
			item_code = bom_i.bi_item
			items_conversion = get_conversion_factore(item_code)
			conversion_factor = 0.0
			for conversion in items_conversion:
				conversion_factor = conversion.conversion_factor
			item_name = bom_i.item_name
			description = bom_i.description
			stock_uom = bom_i.stock_uom
			stock_valuation_price = 0.0
			purchase_order_no = get_purchase_order_no(item_code)
			#print "valuation_prince===========",valuation_prince
			purchase_dict = []
			#print "purchase_order_no=========",purchase_order_no
			for purchase in purchase_order_no:
				purchase_dict.append(purchase.parent)
			stock_ledger_entry = get_stock_ledger_entry(purchase_dict)
			for stock in stock_ledger_entry:
				for stock_details in stock:
					if stock_uom == stock_details.stock_uom:
						stock_valuation_price = stock_details.valuation_rate
			total_stock_valuation_price += stock_valuation_price
			#print "stock_valuation_price==============",stock_valuation_price
			stock_qty = bom_i.bi_qty
			total_bom_qty += stock_qty
			purchase_uom = ""
			valuation_rate = 0.0
			item_group = ""
			last_purchase_rate = 0.0
			check_last_purchase_rate =""
			number_of_purchase = 0
			avg_purchase = 0.0
			max_purchase = 0.0
			min_purchase = 0.0
			last_purchase = 0.0
			item_cose_base_on_last_purchase = 0.0
			item_cose_based_on_valuation_rate = 0.0
			item_details = get_item_details(item_code)
			for code in item_details:
				purchase_uom = code.purchase_uom
				valuation_rate = code.valuation_rate
				item_group = code.item_group
				last_purchase = code.last_purchase_rate
				if last_purchase > 0:
					last_purchase_rate = code.last_purchase_rate
					check_last_purchase_rate = "Y"
				else:
					last_purchase_rate = valuation_rate
					check_last_purchase_rate = "N"
			total_last_purchase_rate +=  last_purchase_rate
			item_cose_base_on_last_purchase = stock_qty * last_purchase_rate
			total_item_cose_base_on_last_purchase += item_cose_base_on_last_purchase
			item_cose_based_on_valuation_rate = stock_valuation_price * last_purchase_rate
			total_item_cose_based_on_valuation_rate += item_cose_based_on_valuation_rate
			number_of_purchase = get_number_of_purchase(item_code)
			for num in number_of_purchase:
				number_of_purchase = num.num_of_purchase
				if last_purchase > 0:
					avg_purchase = round(float(num.avg_purchase),2)
					max_purchase = round(float(num.max_purchase),2)
					min_purchase = round(float(num.min_purchase),2)
				else:
					avg_purchase = valuation_rate
					max_purchase = valuation_rate
					min_purchase = valuation_rate
			total_avg_purchase += avg_purchase
			total_max_purchase += max_purchase
			total_min_purchase += min_purchase
			required_qty = 1
			Amount_valuation_rate = (stock_valuation_price*bo_qty )/required_qty
			amount_last_purchase = 0.0
			if last_purchase_rate == 0:
				amount_last_purchase = (stock_valuation_price*bo_qty )/required_qty
			else :
				amount_last_purchase = (last_purchase_rate * bo_qty)/1
			amount_higher_purchase_rate = 0.0
			amount_lowest_purchase_rate = 0.0
			amount_avg_purchase_rate = 0.0
			if number_of_purchase == 0:
				if last_purchase_rate == 0:
					amount_higher_purchase_rate = (stock_valuation_price*bo_qty )/required_qty
				else:
					amount_higher_purchase_rate = (last_purchase_rate * bo_qty)/1
			else :
				amount_higher_purchase_rate = (max_purchase * bo_qty)/1
			if number_of_purchase == 0:
				if last_purchase_rate == 0:
					amount_lowest_purchase_rate = (stock_valuation_price*bo_qty )/required_qty
				else:
					amount_lowest_purchase_rate = (last_purchase_rate * bo_qty)/1
			else :
				amount_lowest_purchase_rate = (min_purchase * bo_qty)/1
			if number_of_purchase == 0:
				if last_purchase_rate == 0:
					amount_avg_purchase_rate = (stock_valuation_price*bo_qty )/required_qty
				else:
					amount_avg_purchase_rate = (last_purchase_rate * bo_qty)/1
			else :
				amount_avg_purchase_rate = (avg_purchase * bo_qty)/1
			item_amount_based_on_conversion = round(float(last_purchase_rate * bo_qty * conversion_factor),0)
			total_item_amount_based_on_conversion += item_amount_based_on_conversion
			llp = round(float(bo_qty * last_purchase_rate),2)
			total_llp += llp
			data.append([bom_name,item_group,item_name,stock_qty,stock_uom,purchase_uom,conversion_factor,last_purchase_rate,
					item_amount_based_on_conversion,llp,
					item_cose_base_on_last_purchase,stock_valuation_price,item_cose_based_on_valuation_rate,max_purchase,
					avg_purchase,min_purchase,number_of_purchase,check_last_purchase_rate])
	data.append(["","","","","","","","","","","","","",""])
	data.append(["Total","","",total_bom_qty,"","","",total_last_purchase_rate,total_item_amount_based_on_conversion,total_llp,
		total_item_cose_base_on_last_purchase,
		total_stock_valuation_price,total_item_cose_based_on_valuation_rate,total_max_purchase,total_avg_purchase,total_min_purchase])
	return columns, data

def bom_list():
	list = frappe.db.sql()
def get_columns():
	return [
		_("BOM") + "::110",
		_("Item Group ") + "::110",
		_("Bom Item ") + "::110",
		_("Bom Item Qty") + "::110",
		_("Stock UOM") + "::110",
		_("Purchase UOM") + "::110",
		_("Conversion Factor")+"::110",
		_("Last Purchase Price") + "::130",
		_("Total Bom Item Cost Based on conversion Price")+"::180",
		_("LLP")+"::50",
		_("Total Bom Item Cost Based on Last Purchase Price") + "::180",
		_("Current Valuation Rate") + "::130",
		_("Total Bom Item Cost Based on Current Valuation Rate")+"::180",
		_("Last N Purchases - Highest") + "::160",
		_("Last N Purchases - Average") + "::160",
		_("Last N Purchases - Lowest") + "::160",
		_("Number of Purchase Transactions that exist") + "::250",
		_("Was there Last Purchase Price? ") + "::150"

	]
'''
def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " and bo.company = %s" % frappe.db.escape(filters.get("company"), percent=False)
	if filters.get("bom"):
		conditions += " and bi.parent = %s" % frappe.db.escape(filters.get("bom"), percent=False)
	return conditions
'''
def bom_details(company , bom):
	#conditions = get_conditions(company , bom)
	#print ("conditions-------------",conditions)
	bom_detail = frappe.db.sql("""select
										bo.name as bom_name, bo.company, bo.item as bo_item, bo.quantity as bo_qty, bo.project,bi.item_name,
										bi.item_code as bi_item,bi.description, bi.stock_qty as bi_qty,bi.stock_uom
								from
										`tabBOM` bo, `tabBOM Explosion Item` bi
								where
										bo.name = bi.parent and bo.is_active=1 and bo.docstatus = 1 and bo.company = '"""+company+"""' and bi.parent = '"""+bom+"""'

							    order by
								 		bi.item_code""", as_dict=1)
	return bom_detail

def get_item_details(item_code):
	item_detail = frappe.db.sql("""select
											purchase_uom,valuation_rate,item_group,last_purchase_rate
									from
											`tabItem`
									where
											item_code = %s""",(item_code), as_dict =1)
	return item_detail

def get_number_of_purchase(item_code):
	purchase = frappe.db.sql("""select
										count(parent) as num_of_purchase,avg(rate) as avg_purchase,MAX(rate) as max_purchase,
										MIN(rate) as min_purchase
								from
										`tabPurchase Order Item`
								where
										item_code = %s and docstatus = 1""",(item_code), as_dict=1)
	return purchase
def get_purchase_order_no(item_code):
	purchase_order = frappe.db.sql("""select
													parent
											from
													`tabPurchase Order Item`
	 									where
													item_code = '"""+item_code+"""' and docstatus =1
										order by parent
									""", as_dict =1)
	return purchase_order
def get_stock_ledger_entry(purchase_dict):
	purchase_stock_valuation = []
	for purchase in purchase_dict:
		#print "purchase order =============",purchase
		stock_entry = frappe.db.sql("""select
											sl.stock_uom,sl.valuation_rate, pri.purchase_order
									from
											`tabStock Ledger Entry` sl, `tabPurchase Receipt Item` pri
									where
											pri.parent = sl.voucher_no and
											pri.purchase_order IN  ('"""+purchase+"""')
								    order by
											sl.name""",as_dict=1)
		purchase_stock_valuation.append(stock_entry)
	return purchase_stock_valuation

def get_conversion_factore(item_code):
	conversion = frappe.db.sql("""select conversion_factor from `tabUOM Conversion Detail` where parent = '"""+item_code+"""'""", as_dict=1)
	return conversion
