# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import datetime
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

from hrms.hr.utils import update_employee_work_history, validate_active_employee

@frappe.whitelist(allow_guest=True)
def Update_employee_details():
	today = frappe.utils.nowdate()
	promotions = frappe.get_all("Employee Promotion", filters={"docstatus": 1, "based_on": "On Effective Date", "effective_date": today})
	print("\n", promotions, "\n")

	# if promotions:  
	# 	print("\n\n\nHello\n\n\n")
	# 	for promotion in promotions:
	# 		print(promotion.name)

	# 		employee = frappe.get_doc("Employee", promotion.employee)
	# 		Emp_Details = frappe.get_all("Employee Property History", filters={"parent": promotion.name}, fields=['property', 'current', 'new', 'fieldname'], order_by="idx Asc")

	# 		for data in Emp_Details:
	# 			Property = data.property
	# 			Current_value = data.current
	# 			New_value = data.new
	# 			Fieldname = data.fieldname

	# 			setattr(employee, Fieldname, New_value)
	# 			employee.save()

	# 			for record in employee.employee_old_details:
	# 				if record.property == Property:
	# 					Old_promotion_datetime = datetime.datetime.strptime(str(record.to_date), "%Y-%m-%d")
	# 					After_old_promotion_date = Old_promotion_datetime + datetime.timedelta(days=1)
	# 					From_date = After_old_promotion_date
	# 					break
	# 			else:
	# 				ans_from_date = datetime.datetime.strptime(str(employee.creation), "%Y-%m-%d %H:%M:%S.%f")
	# 				From_date = ans_from_date.date()

	# 			promotion_date_datetime = datetime.datetime.strptime(promotion.promotion_date, "%Y-%m-%d")
	# 			one_day_before_promotion = promotion_date_datetime - datetime.timedelta(days=1)

	# 			Child_history = employee.append("employee_old_details", {})
	# 			Child_history.property = Property
	# 			Child_history.old_value = Current_value
	# 			Child_history.employee_promotion = promotion.name
	# 			Child_history.field_name = Fieldname
	# 			Child_history.from_date = From_date
	# 			Child_history.to_date = one_day_before_promotion

	# 		employee.save()
		
	# else:
	# 	print("\n\n\nNo promotions today\n\n\n")
    


class EmployeePromotion(Document):
	
	def validate(self):
		validate_active_employee(self.employee)

	# def before_submit(self):
	# 	if getdate(self.promotion_date) > getdate():
	# 		frappe.throw(
	# 			_("Employee Promotion cannot be submitted before Promotion Date"),
	# 			frappe.DocstatusTransitionError,
	# 		)


	def on_submit(self):
		
		if self.based_on == "On Approval":

			employee = frappe.get_doc("Employee", self.employee)
			Emp_Details = frappe.get_all("Employee Property History", filters={"parent": self.name}, fields=['property', 'current', 'new', 'fieldname'], order_by="idx Asc")

			for data in Emp_Details:
				Property = data.property
				Current_value = data.current
				New_value = data.new
				Fieldname = data.fieldname

				setattr(employee, Fieldname, New_value)
				employee.save()

				for record in employee.employee_old_details:
					if record.property == Property:
						Old_promotion_datetime = datetime.datetime.strptime(str(record.to_date), "%Y-%m-%d")
						After_old_promotion_date = Old_promotion_datetime + datetime.timedelta(days=1)
						From_date = After_old_promotion_date
						break
				else:
					ans_from_date = datetime.datetime.strptime(str(employee.creation), "%Y-%m-%d %H:%M:%S.%f")
					From_date = ans_from_date.date()

				promotion_date_datetime = datetime.datetime.strptime(self.promotion_date, "%Y-%m-%d")
				one_day_before_promotion = promotion_date_datetime - datetime.timedelta(days=1)

				Child_history = employee.append("employee_old_details", {})
				Child_history.property = Property
				Child_history.old_value = Current_value
				Child_history.employee_promotion = self.name
				Child_history.field_name = Fieldname
				Child_history.from_date = From_date
				Child_history.to_date = one_day_before_promotion

			employee.save()


	def on_cancel(self):
		employee = frappe.get_doc("Employee", self.employee)
		Emp_Details = frappe.get_all("Employee History in Company", filters={"employee_promotion": self.name}, fields=['name', 'old_value', 'field_name'])
		for data in Emp_Details:
			Current_value = data.old_value
			Fieldname = data.field_name
			cur_name = data.name
			setattr(employee, Fieldname, Current_value)
			employee.save()
			frappe.get_doc('Employee History in Company', cur_name).delete()
			
		
