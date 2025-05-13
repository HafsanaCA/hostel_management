# -*- coding: utf-8 -*-
{
    'name': "Hostel Management",
    'version': '1.0',
    'depends': ['base','mail', 'product', 'account','website', 'website_sale','point_of_sale'],
    'author': "Bessie Porter",
    'description': """
    This is a Hostel Management System
    """,
    'data': [
        'data/ir.sequence_data.xml',
        'data/hostel_facility_data.xml',
        'data/product_product_data.xml',
        'data/mail_template_data.xml',
        'data/mail_template_action_data.xml',
        'data/ir_cron_data.xml',
        'data/user_creation_data.xml',
        'data/website_menu_data.xml',
        'views/room_management.xml',
        'views/student_information.xml',
        'views/hostel_facility.xml',
        'views/leave_request.xml',
        'views/account_move.xml',
        'views/cleaning_service.xml',
        'views/student_registration_template.xml',
        'views/hostel_room_snippet_template.xml',
        'views/room_detailed_page.xml',
        'views/website_bom_cart_display_views.xml',
        'report/ir_actions_report.xml',
        'report/hostel_report_template.xml',
        'wizard/student_report_wizard.xml',
        'wizard/leave_request_report_wizard.xml',
        'views/hostel_management.xml',
        'security/security_group.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'hostel_management/static/src/js/action_manager.js',
        ],
        'web.assets_frontend': [
            'hostel_management/static/src/js/latest_room.js',
            '/hostel_management/static/src/xml/latest_rooms_content.xml',
            'hostel_management/static/src/css/room_style.css',
        ],
    },

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
