# -*- coding: utf-8 -*-
{
    "name": "Enterprise WeChat JSAPI",
    "author": "RStudio",
    "website": "",
    "sequence": 1,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "wxwork",
    "version": "13.0.0.1",
    "summary": """
        
        """,
    "description": """


        """,
    "depends": [
        "wxwork_base",
    ],
    "external_dependencies": {
        "python": [],
    },
    "data": [
        "data/ir_cron_data.xml",
        "data/ir_config_parameter.xml",
        "views/res_config_settings_views.xml",
        "views/ir_cron_views.xml",
        "views/menu.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
}