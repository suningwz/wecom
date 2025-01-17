# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException


class Department(models.Model):

    _inherit = "hr.department"
    # _order = "wecom_department_order asc,complete_name"
    # _order = "display_name"

    category_ids = fields.Many2many(
        "hr.employee.category",
        "department_category_rel",
        "dmp_id",
        "category_id",
        groups="hr.group_hr_manager",
        string="Tags",
    )

    wecom_department_id = fields.Integer(
        string="WeCom department ID", readonly=True, default="0",
    )

    wecom_department_parent_id = fields.Integer(
        "WeCom parent department ID",
        help="Parent department ID,32-bit integer.Root department is 1",
        readonly=True,
    )
    wecom_department_order = fields.Char(
        "WeCom department sort",
        default="1",
        help="Order value in parent department. The higher order value is sorted first. The value range is[0, 2^32]",
        readonly=True,
    )
    is_wecom_department = fields.Boolean(
        string="WeCom Department", readonly=True, default=False,
    )

    def remove_obj_from_tag(self):
        """
        从标签中移除部门
        """
        # category_id = self.env.context.get("category_id")
        # print("执行删除成员---部门")

        # self.category_ids = False
