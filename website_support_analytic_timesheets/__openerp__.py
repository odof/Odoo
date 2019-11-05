{
    'name': "Website Help Desk / Support Ticket - Analytic Timesheets",
    'version': "1.0.9",
    'author': "Sythil Tech",
    'category': "Tools",
    'summary':'Track time spend on tickets',
    'license':'LGPL-3',
    'data': [
        'views/website_support_ticket_views.xml',
        'views/website_support_ticket_templates.xml',
        'views/account_analytic_line_views.xml',
        'views/website_support_settings_views.xml',
        'data/account.analytic.account.csv',
    ],
    'demo': [],
    'depends': ['website_support','hr_timesheet_sheet'],
    'images':[
        'static/description/1.jpg',
    ],
    'installable': True,
}