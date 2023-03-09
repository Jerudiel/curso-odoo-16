{
    'name' : "estate",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'author': "Odoo Community Association (OCA)",
    'website': "http://www.yourcompany.com",
    'license': 'LGPL-3',

    'category': 'Uncategorized',
    'version': '16.0.0.0.1',

    'depends': ['base',
                'board'],

    'installable': True,
    'application': True,

    'data' : [
        "security/ir.model.access.csv",
        "views/estate_property_type_views.xml",
        "views/estate_property_tag_views.xml",
        "views/estate_property_offer_views.xml",
        "views/estate_property_views.xml",
        "views/estate_menus.xml",
    ]
}