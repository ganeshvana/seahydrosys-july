{
    "name": "Inactivity Session Timeout",
    'summary': """
       This odoo app helps to logout user after inactivity of specific(defined) time.""",
    'description': """
        Automatic Logout After Inactivity of specific(defined) time.
    """,

    "author": "Cybat",
    "website" : "https://www.cybat.net",
    "price": 25.00,
    "currency": 'EUR',
    'version': '16.0.0.1',
    "license": "AGPL-3",
    "depends": ["base", "web"],
    "data": [
        "data/data.xml",
    ],
    "assets": {
        "web.assets_common": [
            "cybat_inactivity_session_logout/static/src/js/logout.js"
        ]
    },
    "installable": True,
    'images': ['static/description/main_screenshot.gif'],
}
