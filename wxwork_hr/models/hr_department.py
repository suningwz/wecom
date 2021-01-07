# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Department(models.Model):

    _inherit = "hr.department"
    _order = "complete_name "

    wxwork_department_id = fields.Integer(
        string="Enterprise WeChat department ID", readonly=True, default="0",
    )

    wxwork_department_parent_id = fields.Integer(
        "Enterprise WeChat parent department ID",
        help="Parent department ID,32-bit integer.Root department is 1",
        readonly=True,
    )
    wxwork_department_order = fields.Char(
        "Enterprise WeChat department sort",
        default="1",
        help="Order value in parent department. The higher order value is sorted first. The value range is[0, 2^32)",
        readonly=True,
    )
    is_wxwork_department = fields.Boolean(
        string="Enterprise WeChat Department", readonly=True, default=False,
    )
