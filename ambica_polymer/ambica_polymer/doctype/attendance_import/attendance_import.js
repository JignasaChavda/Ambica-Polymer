// Copyright (c) 2023, Jignasa Chavda and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Import', {
    refresh: function(frm) {
        frm.toggle_display('preview', false);
        frm.trigger('preview_file');

        frm.add_custom_button(__('Mark Attendance'), () => frm.trigger('mark_attendance'));
        frm.add_custom_button(__('Export Failed Logs'), () => frm.trigger('export_error_records'));
    },
    preview_file: function(frm) {
        if ($preview) {
            frm.toggle_display('preview', true);
            frm.get_field('import_warnings').$wrapper.html($preview);
        }
    },
    mark_attendance: function(frm) {
        frappe.call({
            method: 'ambica_polymer.ambica_polymer.doctype.attendance_import.attendance_import.validate',
            args: {
                docname: frm.docname
            },
            callback: function(r) {
                if (r.message) {
                    if (r.message.status === 'success') {
                        frappe.msgprint(r.message.message);
                    } else {
                        var errorMessages = r.message.message.split('\n');
                        var $preview = $('<div>');

                        // Iterate through error messages and add them with proper line spacing
                        var inErrorBlock = false;
                        errorMessages.forEach(function(errorMessage) {
                            if (errorMessage.startsWith('Error in Row')) {
                                if (inErrorBlock) {
                                    $preview.append($('<div>&nbsp;</div>')); // Add a blank line between error blocks
                                }
                                inErrorBlock = true;
                            }
                            $preview.append($('<div>').html(errorMessage));
                        });

                        if ($preview) {
                            frm.toggle_display('preview', true);
                            frm.get_field('import_warnings').$wrapper.empty().append($preview);
                            frm.save();
                        }
                    }
                }
            }
        });
    },
    export_error_records: function(frm) {
        frappe.call({
            method: 'ambica_polymer.ambica_polymer.doctype.attendance_import.attendance_import.collect_error_records', // Replace with your actual method path
            args: {
                doc: frm.docname
            },
            callback: function(r) {
                if (r.message) {
                    // Check if there are error records to export
                    if (r.message.error_records && r.message.error_records.length > 0) {
                        // Define the field mapping for your child table
                        const fieldMapping = {
                            "employee": "child_table_field1",
                            "employee_name": "child_table_field2",
                            "department": "department",
                            "company": "company",
                            "attendance_date": "attendance_date",
                            "status": "status",
                            "in_time": "in_time",
                            "out_time": "out_time",
                            "shift": "shift",
                            "working_hours": "working_hours",
                            "late_hours": "late_hours",
                            "early_hours": "early_hours",
                            "leave_type": "leave_type",
                            "leave_application": "leave_application",
                            "weekly_off": "weekly_off",
                            "holiday": "holiday",
                            "remarks": "remarks" 
                            // ... add mappings for other fields ...
                        };

                        // Create a CSV string with custom field names as the first row
                        const csvContent = "data:text/csv;charset=utf-8," 
                            + Object.keys(fieldMapping).join(',') + '\n'
                            + r.message.error_records.map(row => Object.keys(fieldMapping).map(customField => row[fieldMapping[customField]] || "").join(',')).join('\n');

                        // Create a temporary anchor element to trigger the download
                        const anchor = document.createElement('a');
                        anchor.href = encodeURI(csvContent);
                        anchor.target = '_blank';
                        anchor.download = 'Error_Records.csv';
                        anchor.click();
                    } else {
                        frappe.msgprint('No error records to export.');
                    }
                }
            }
        });
    }
});



















