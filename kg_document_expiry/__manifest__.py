# -*- coding: utf-8 -*-
{
    "name": "Document Expiry",
    "summary": "Set Expiry Date for Document",
    "version": "15.0.1.0.0",
    'category': 'Productivity/Documents',
    'author': "Klystron Global",
    'maintainer': "Ameen",
    "license": "OPL-1",
    'website': 'https://www.klystronglobal.com',

    "depends": ["web", "documents", "hr"],
    "data": [
        'views/email_template.xml',
        'views/documents_views.xml',
        'views/cron_jobs.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'kg_document_expiry/static/src/js/document_expiry.js',
        ],
    },
    'images': ['static/description/logo.png'],
    "installable": True,
}
