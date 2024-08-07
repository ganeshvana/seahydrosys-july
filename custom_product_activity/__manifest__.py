{
    'name': 'Custom Product Activity',
    'version': '1.0',
    'summary': 'Show schedule activity status in product list view',
    'description': 'Updates the product list view with the latest schedule activity status',
    'author': 'OI',
    'depends': ['base', 'product', 'mail'],
    'data': [
        'views/product_views.xml',
    ],
    'installable': True,
    'application': False,
}
