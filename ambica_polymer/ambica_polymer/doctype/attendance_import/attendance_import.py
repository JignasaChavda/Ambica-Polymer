# Copyright (c) 2023, Jignasa Chavda and contributors
# For license information, please see license.txt

import calendar
from datetime import date, datetime
import frappe
from frappe.utils import get_html_format
from frappe.utils import get_link_to_form
from frappe.model.document import Document
from hrms.hr.utils import validate_active_employee
from hrms.hr.doctype.attendance.attendance import has_overlapping_timings

@frappe.whitelist(allow_guest=True)
def validate(docname):
    doc = frappe.get_doc("Attendance Import", docname)
    error_messages = {}  # Use a dictionary to store error messages by row
    salary_slip_errors = []
    validate_salary_slip(salary_slip_errors, doc)

    import_warning = []  # Use a list to store error messages for each row

    for child in doc.get("attendance_details"):
        error_messages[child.idx] = []  # Initialize error messages list for this row
        emp_link = get_link_to_form("Employee", child.employee)
        emp_name = child.employee_name

        validate_active_employee(child.employee)
        validate_import_date(child, doc.import_date, error_messages[child.idx])
        validate_shift(child, error_messages[child.idx])
        validate_ctc_approval(child, error_messages[child.idx])
        validate_DOL(child, error_messages[child.idx])
        validate_week_off(child, error_messages[child.idx])
        validate_time(child, error_messages[child.idx])
        validate_attendance(child, error_messages[child.idx])
        validate_workhours(child, error_messages[child.idx])

        error_messages_list = error_messages[child.idx]
        if error_messages_list:
            error_heading = f"<b>Error in Row {child.idx}</b>"
            import_warning.append(error_heading)
            import_warning.extend([f"• {message}" for message in error_messages_list])
            import_warning.append("<br>")

    if salary_slip_errors:
        salary_error_heading = "<b>Salary Slip Errors:</b>"
        import_warning.append("<br>")
        import_warning.append(salary_error_heading)
        for error in salary_slip_errors:
            salary_error_message = f"• {error} "
            import_warning.append("<br>")
            import_warning.append(salary_error_message)

    # error_records = collect_error_records(doc)  # Pass 'doc' to the function

    response = {
        "status": "success" if not import_warning else "error",
        "message": "\n\n".join(import_warning),
        "error_records": error_records
    }

    return response


@frappe.whitelist(allow_guest=True)
def collect_error_records(doc):
    frappe.msgprint("hello")
    error_records = []

    for child in doc.get("attendance_details"):
        error_messages = error_messages[child.idx]
        if error_messages:
            error_data = {
                "Row": child.idx,
                "Employee": child.employee,
                "Employee Name": child.employee_name,
                "Errors": error_messages
            }
            error_records.append(error_data)

    return error_records

def validate_import_date(child, import_date, error_messages):
    if child.attendance_date != import_date:
        error_messages.append(f"Import date and attendance date must be the same for this entry.")

def validate_shift(child, error_messages):
    if child.shift:
        shift_type = frappe.get_doc("Shift Type", child.shift)
        if not shift_type:
            error_messages.append(f"Shift <b>'{child.shift}'</b> does not exist.")

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
                
        if promotion_names:
            error_messages.append(f"CTC approval records of employee <b>{child.employee} : {child.employee_name}</b> are not submitted yet for the following promotions <b>{', '.join(promotion_names)}</b>")
            
def validate_DOL(child,error_messages):
    attendance_date = child.attendance_date
    date_of_leaving = frappe.get_value("Employee", child.employee, 'relieving_date')
    
    
    if date_of_leaving and attendance_date and date_of_leaving < attendance_date:
        error_messages.append(f"Date of Leaving of employee <b>{child.employee} : {child.employee_name}</b> is less than the Attendance Date for this entry.")
        
 
def validate_week_off(child, error_messages):
    week_off = frappe.get_value("Employee", child.employee, 'week_off')

    if not week_off:
         error_messages.append(f"WeekOff of employee <b>{child.employee} : {child.employee_name}</b> is null in employee master.")
    else:
        Holiday_List = frappe.get_value("Employee", child.employee, 'holiday_list')

        holiday_child = frappe.get_all("Holiday",filters = {"parent":Holiday_List, "holiday_date":child.attendance_date, "weekly_off":1}, fields=["holiday_date", "weekly_off"])

        if child.status == "Week Off" and not holiday_child:
            error_messages.append(f"WeekOff mismatched for employee <b>{child.employee} : {child.employee_name}</b>")
       
        elif child.status in ["Present"] and holiday_child:       
            error_messages.append(f"WeekOff mismatched for employee <b>{child.employee} : {child.employee_name}</b>")
            
           
def validate_time(child,error_messages):
    if child.in_time is None:
        error_messages.append(f"In time is missing for employee <b>{child.employee} : {child.employee_name}</b> in this record")
    
    if child.out_time is None:
        error_messages.append(f"Out time is missing for employee <b>{child.employee} : {child.employee_name}</b> in this record")
        

def validate_attendance(child,error_messages):
    if child.attendance_date:
        atte_record = frappe.get_value("Attendance", filters= {"employee":child.employee, "attendance_date":child.attendance_date},fieldname="name")
    
        atte_link = get_link_to_form("Attendance", atte_record)
       
        if atte_record:
            error_messages.append(f"Attendance for <b>{child.employee} : {child.employee_name}</b> is already marked for the date <b>{child.attendance_date}</b>: {atte_link}")


def validate_workhours(child, error_messages):
    if child.working_hours and child.working_hours >= 24.00:
        error_messages.append(f"Working hours for employee <b>{child.employee} : {child.employee_name}</b> on <b>{child.attendance_date}</b> exceed <b>24</b> hours. Marking the employee as Absent.")
        child.status = "Absent"


def validate_salary_slip(salary_slip_errors,doc):
    first_day_of_current_month = frappe.utils.get_first_day(doc.import_date)
    last_day_of_current_month = frappe.utils.get_last_day(doc.import_date)

    first_day_of_previous_month = frappe.utils.add_months(first_day_of_current_month, -1)
    last_day_of_previous_month = frappe.utils.add_days(first_day_of_current_month, -1)

    validate_previous_month_salaryslip(salary_slip_errors,first_day_of_previous_month,last_day_of_previous_month)
    validate_current_month_salaryslip(salary_slip_errors,first_day_of_current_month,last_day_of_current_month)
    



def validate_previous_month_salaryslip(salary_slip_errors, first_day_of_previous_month, last_day_of_previous_month):
    salary_slip_exists = frappe.get_all(
        "Salary Slip",
        filters={
            "start_date": ["<=", first_day_of_previous_month],
            "end_date": [">=", last_day_of_previous_month],
            "docstatus": 0,
        },
        fields=["name"],
    )

    if salary_slip_exists:
        salary_slip_links = []
        for pre_record in salary_slip_exists:
            salary_slip = pre_record.name
            salaryslip_link = get_link_to_form("Salary Slip", salary_slip)
            salary_slip_links.append(f"&nbsp&nbsp&nbsp&nbsp Sal Slip{salaryslip_link}")
        salary_slip_errors.append(
            f"Salary Slip for the previous month of <b>{first_day_of_previous_month.strftime('%B, %Y')}</b> has not been submitted yet:\n" + "\n".join(salary_slip_links)
        )

def validate_current_month_salaryslip(salary_slip_errors, first_day_of_current_month, last_day_of_current_month):
    salary_slip_exists = frappe.get_all(
        "Salary Slip",
        filters={
            "start_date": ["<=", first_day_of_current_month],
            "end_date": [">=", last_day_of_current_month],
            "docstatus": 1,
        },
        fields=["name"],
    )

    if salary_slip_exists:
        salary_slip_links = []
        for pre_record in salary_slip_exists:
            salary_slip = pre_record.name
            salaryslip_link = get_link_to_form("Salary Slip", salary_slip)
            salary_slip_links.append(f"&nbsp&nbsp&nbsp&nbsp Sal Slip{salaryslip_link}")
        salary_slip_errors.append(
            f"Salary Slip for the month of <b>{first_day_of_current_month.strftime('%B, %Y')}</b> has already been submitted:\n" + "\n".join(salary_slip_links)
        )



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








      




	