# -*- coding: utf-8 -*-
{
    "name": "Enterprise WeChat Scan Code Widget",
    "author": "RStudio",
    "website": "",
    "sequence": 1,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "wxwork",
    "version": "13.0.0.1",
    "summary": """
        Enterprise WeChat Scan Code,Support QR code and barcode.
        只能在企业微信应用的可信域名下调用(包括子域名)，且可信域名必须有ICP备案且在管理端验证域名归属。
        """,
    "description": """


        """,
    "depends": [
        "wxwork_base",
        "wxwork_agent_jsapi",
    ],
    "external_dependencies": {
        "python": [],
    },
    "data": [
        "views/assets_templates.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
}
