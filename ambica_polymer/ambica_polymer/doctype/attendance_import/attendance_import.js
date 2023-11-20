// Copyright (c) 2023, Jignasa Chavda and contributors
// For license information, please see license.txt



frappe.ui.form.on('Attendance Import', {
    refresh: function (frm) {
        frm.get_field('import_warnings').$wrapper.empty().append(frm.doc.error_row);
       
        frm.add_custom_button(__('Mark Attendance'), () => frm.trigger('mark_attendance'));
        frm.add_custom_button(__('Export Failed Logs'), () => frm.trigger('export_error_records'));
    },
    mark_attendance: function(frm){
        
        frappe.call({
            method: 'ambica_polymer.ambica_polymer.doctype.attendance_import.attendance_import.validate',
            args: {
                docname: frm.docname
            },
            callback: function (r) {
                if (r.message && r.message.status === 'success') {
                    frappe.msgprint("Attendance Marked Successfully");

                }
                else{
                    if (r.message && r.message.status === 'error') {
                        // frm.error_row.clear()
                        frm.toggle_display('preview', true);
                        frm.get_field('import_warnings').$wrapper.empty().append(r.message.message);
                        frm.save();
                        // reloadPage = true;
                        
                    }
                    if ($preview) {
                        frm.toggle_display('preview', true);
                        frm.get_field('import_warnings').$wrapper.empty().append($preview);
                        frm.save();
                       
                    }
                }

            }
            
        });
        // if (reloadPage == true) {
        //     window.location.reload(); // Reload the page if the flag is set
        // }
    },
    export_error_records: function(frm) {
            frappe.call({
                method: 'ambica_polymer.ambica_polymer.doctype.attendance_import.attendance_import.collect_error_records',
                args: {
                    docname: frm.docname
                },
                callback: function(r) {
                    if (r.message) {
                        // Check if there are error records to export
                        if (r.message && r.message.length > 0) {
                            // Create a CSV string with custom field names as the first row
                            const csvContent = "data:text/csv;charset=utf-8," 
                                + Object.keys(r.message[0]).join(',') + '\n'
                                + r.message.map(row => Object.values(row).map(value => value || "").join(',')).join('\n');
        
                            // Create a temporary anchor element to trigger the download
                            const anchor = document.createElement('a');
                            anchor.href = encodeURI(csvContent);
                            anchor.target = '_blank';
                            anchor.download = 'Error_Records.csv';
                            anchor.click();
                        }
                    }
                }
            });
        }
});

























