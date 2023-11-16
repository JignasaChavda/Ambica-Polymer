# Copyright (c) 2023, Jignasa Chavda and contributors
# For license information, please see license.txt

from datetime import datetime
import frappe
from frappe.utils import get_html_format
from frappe.utils import get_link_to_form
from frappe.model.document import Document
from hrms.hr.utils import validate_active_employee




@frappe.whitelist(allow_guest=True)
def validate(docname):
    doc = frappe.get_doc("Attendance Import", docname)
    error_messages = [] 

    for child in doc.get("attendance_details"):
        validate_active_employee(child.employee)
        validate_import_date(child, doc.import_date, error_messages)
        validate_shift(child, error_messages)
        validate_ctc_approval(child,error_messages)
        validate_DOL(child,error_messages)
        validate_week_off(child,error_messages)

    #     mark_attendance(child)
    
    if error_messages:
        response = {
            "status": "error",
            "message": "\n".join(error_messages)
        }
    else:
        response = {
                "status": "success",
                "message": "Attendance Marked successfully"
            }
    return response


def validate_import_date(child, import_date, error_messages):
    if child.attendance_date != import_date:
        error_messages.append(f"<b>Error in Row {child.idx}:</b> Import date and attendance date must be the same for this entry.")

def validate_shift(child, error_messages):
    if child.shift:
        shift_type = frappe.get_doc("Shift Type", child.shift)
        if not shift_type:
            error_messages.append(f"<b>Error in Row {child.idx}:</b> Shift <b>'{child.shift}'</b> does not exist.")

def validate_ctc_approval(child, error_messages):
    filters = {
        "employee": child.employee,
        "docstatus": "Draft",
        "revised_ctc": (">", 0)  # Revised CTC is not zero
    }
    employee_promotion = frappe.get_all("Employee Promotion", filters=filters, fields=["name","current_ctc", "revised_ctc"])
    
    promotion_names = []

    if employee_promotion:
        for promotion in employee_promotion:
            promotion_name = promotion.name
            if promotion.current_ctc != promotion.revised_ctc:
                promotion_link = get_link_to_form("Employee Promotion", promotion_name)
                promotion_names.append(promotion_link)

                emp_link = get_link_to_form("Employee", child.employee, child.employee_name)
                emp_name = child.employee_name
                emp_full_link = f'<a href="{emp_link}"></a>'
               
                
        if promotion_names:
            error_messages.append(f"<b>Error in Row {child.idx}:</b> CTC approval records of employee <b>{emp_full_link}</b> are not submitted yet for the following promotions <b>{', '.join(promotion_names)}</b>")
            
def validate_DOL(child,error_messages):
    attendance_date = child.attendance_date
    date_of_leaving = frappe.get_value("Employee", child.employee, 'relieving_date')
    
    if date_of_leaving and attendance_date and date_of_leaving < attendance_date:
        error_messages.append(f"<b>Error in Row {child.idx}:</b> Date of Leaving of employee <b>{child.employee} : {child.employee_name}</b> is less than the Attendance Date for this entry.")
        
 
def validate_week_off(child, error_messages):
    week_off = frappe.get_value("Employee", child.employee, 'week_off')

    if not week_off:
         error_messages.append(f"<b>Error in Row {child.idx}:</b> WeekOff of employee <b>{child.employee} : {child.employee_name}</b> is null in employee master.")
    












def mark_attendance(child):
    atte_record = frappe.new_doc("Attendance")
    atte_record.employee = child.employee
    atte_record.status = child.status
    atte_record.attendance_date = child.attendance_date

    in_time_delta = child.in_time
    out_time_delta = child.out_time

    if in_time_delta is not None:
        in_time = (datetime.min + in_time_delta).time()
        in_datetime = datetime.combine(child.attendance_date, in_time)
        atte_record.in_time = in_datetime

    if out_time_delta is not None:
        out_time = (datetime.min + out_time_delta).time()
        out_datetime = datetime.combine(child.attendance_date, out_time)
        atte_record.out_time = out_datetime

    atte_record.shift = child.shift
    atte_record.leave_type = child.leave_type
    atte_record.leave_application = child.leave_application
    atte_record.remarks = child.remarks
    atte_record.insert(ignore_permissions=True)
    atte_record.submit()







class AttendanceImport(Document):
    pass








      




	