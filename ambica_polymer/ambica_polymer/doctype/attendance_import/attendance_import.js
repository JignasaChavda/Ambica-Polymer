// Copyright (c) 2023, Jignasa Chavda and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Import', {
    refresh: function(frm) {
        frm.add_custom_button(__('Mark Attendance'), function() {
            frappe.call({
                method: 'ambica_polymer.ambica_polymer.doctype.attendance_import.attendance_import.validate',
                args: {
                    docname: frm.docname
                },
                callback: function(r) {
                    if (r.message) {
                        if (r.message.status === 'success') {
                        
                            
                        } else {
                           
                            var errorMessages = r.message.message.split('\n');
                            var $preview = $('<div>');
                            errorMessages.forEach(function(errorMessage) {
                                $preview.append($('<div>').html(errorMessage));
                            });

                           
                            frm.get_field("import_warnings").$wrapper.empty().append($preview);
                        }
                    }
                }
            });
        });
    }
});
