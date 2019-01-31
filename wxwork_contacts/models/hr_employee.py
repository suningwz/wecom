# -*- coding: utf-8 -*-

from odoo import api, fields, models
from ..api.CorpApi import *
from ..helper.common import *
import logging,platform
import threading
import time

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = '企业微信员工'
    _order = 'wxwork_user_order'

    wxwork_id = fields.Char(string='企微用户Id', readonly=True)
    alias = fields.Char(string='别名', readonly=True)
    department_ids = fields.Many2many('hr.department', string='企微多部门', readonly=True)
    qr_code = fields.Binary(string='个人二维码', help='员工个人二维码，扫描可添加为外部联系人', readonly=True)
    wxwork_user_order = fields.Char(
        '企微用户排序',
        default='0',
        help='部门内的排序值，默认为0。数量必须和department一致，数值越大排序越前面。值范围是[0, 2^32)',
        readonly=True,
    )
    is_wxwork_employee = fields.Boolean('企微员工', readonly=True)

    @api.multi
    def sync_employee(self):
        params = self.env['ir.config_parameter'].sudo()
        corpid = params.get_param('wxwork.corpid')
        secret = params.get_param('wxwork.contacts_secret')
        sync_department_id = params.get_param('wxwork.contacts_sync_hr_department_id')
        api = CorpApi(corpid, secret)
        try:
            response = api.httpCall(
                CORP_API_TYPE['USER_LIST'],
                {
                    'department_id': sync_department_id,
                    'fetch_child': '1',
                }
            )
            start = time.time()
            for obj in response['userlist']:
                threaded_sync = threading.Thread(target=self.run, args=[obj])
                threaded_sync.start()
            end = time.time()
            times = end - start
            result = True
        except BaseException as e:
            print(repr(e))
            result = False
        return times,result

    @api.multi
    def run(self, obj):
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            env = self.sudo().env['hr.employee']
            domain = ['|', ('active', '=', False),
                      ('active', '=', True)]
            records = env.search(
                domain + [
                    ('wxwork_id', '=', obj['userid']),
                    ('is_wxwork_employee', '=', True)],
                limit=1)

            try:
                if len(records) > 0:
                    self.update_employee(records, obj)
                else:
                    self.create_employee(records, obj)
            except Exception as e:
                print(repr(e))
            new_cr.commit()
            new_cr.close()

    @api.multi
    def create_employee(self,records, obj):
        department_ids = []
        for department in obj['department']:
            department_ids.append(self.get_employee_parent_department(department))

        img_path = self.env['ir.config_parameter'].sudo().get_param('wxwork.contacts_img_path')
        if (platform.system() == 'Windows'):
            avatar_file = img_path.replace("\\","/") + "/avatar/" + obj['userid'] + ".jpg"
            qr_code_file = img_path.replace("\\","/")  + "/qr_code/" + obj['userid'] + ".png"
        else:
            avatar_file = img_path + "avatar/" + obj['userid'] + ".jpg"
            qr_code_file = img_path + "qr_code/" + obj['userid'] + ".png"

        try:
            records.create({
                'wxwork_id': obj['userid'],
                'name': obj['name'],
                'gender': Common(obj['gender']).gender(),
                'marital': None, # 不生成婚姻状况
                'image': self.encode_image_as_base64(avatar_file),
                'mobile_phone': obj['mobile'],
                'work_phone': obj['telephone'],
                'work_email': obj['email'],
                'active': obj['enable'],
                'alias': obj['alias'],
                'department_ids': [(6, 0, department_ids)],
                'wxwork_user_order': obj['order'],
                'qr_code': self.encode_image_as_base64(qr_code_file),
                'is_wxwork_employee': True,
            })
            result = True
        except Exception as e:
            print('创建员工错误：%s - %s' % (obj['name'], repr(e)))
            result = False
        return result

    @api.multi
    def update_employee(self,records, obj):
        department_ids = []
        for department in obj['department']:
            department_ids.append(self.get_employee_parent_department(department))
        img_path = self.env['ir.config_parameter'].sudo().get_param('wxwork.contacts_img_path')
        if (platform.system() == 'Windows'):
            avatar_file = img_path.replace("\\","/") + "/avatar/" + obj['userid'] + ".jpg"
            qr_code_file = img_path.replace("\\","/")  + "/qr_code/" + obj['userid'] + ".png"
        else:
            avatar_file = img_path + "avatar/" + obj['userid'] + ".jpg"
            qr_code_file = img_path + "qr_code/" + obj['userid'] + ".png"
        try:
            records.write({
                'name': obj['name'],
                'gender': Common(obj['gender']).gender(),
                'image': self.encode_image_as_base64(avatar_file),
                'mobile_phone': obj['mobile'],
                'work_phone': obj['telephone'],
                'work_email': obj['email'],
                'active': obj['enable'],
                'alias': obj['alias'],
                'department_ids': [(6, 0, department_ids)],
                'wxwork_user_order': obj['order'],
                'qr_code': self.encode_image_as_base64(qr_code_file),
                'is_wxwork_employee': True
            })
            result = True
        except Exception as e:
            print('更新员工错误：%s - %s' % (obj['name'], repr(e)))
            result = False

        return result

    @api.multi
    def encode_image_as_base64(self,image_path):
        # if not self.sync_img:
        #     return None
        if not os.path.exists(image_path):
            pass
        else:
            try:
                with open(image_path, "rb") as f:
                    encoded_string = base64.b64encode(f.read())
                return encoded_string
            except BaseException as e:
                return None
                # pass

    @api.multi
    def get_employee_parent_department(self,department_id):
        try:
            departments = self.env['hr.department'].search([
                ('wxwork_department_id', '=', department_id),
                ('is_wxwork_department', '=', True)],
                limit=1)
            if len(departments) > 0:
                return departments.id
        except BaseException:
            pass

    @api.multi
    def update_leave_employee(self):
        """
                比较企业微信和odoo的员工数据，且设置离职odoo员工active状态
                """
        params = self.env['ir.config_parameter'].sudo()
        corpid = params.get_param('wxwork.corpid')
        secret = params.get_param('wxwork.contacts_secret')
        sync_department_id = params.get_param('wxwork.contacts_sync_hr_department_id')
        api = CorpApi(corpid, secret)

        try:
            response = api.httpCall(
                CORP_API_TYPE['USER_LIST'],
                {
                    'department_id': sync_department_id,
                    'fetch_child': '1',
                }
            )
            list_user = []
            list_employee = []

            for obj in response['userlist']:
                list_user.append(obj['userid'])

            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            env = self.sudo().env['hr.employee']

            domain = ['|', ('active', '=', False),
                      ('active', '=', True)]
            records = env.search(
                domain + [
                    ('is_wxwork_employee', '=', True)
                ])

            for employee in records:
                list_employee.append(employee.wxwork_id)

            list_user_leave = list(set(list_employee).difference(set(list_user)))

            start = time.time()


            for obj in list_user_leave:
                employee = records.search([
                    ('wxwork_id', '=', obj)
                ])
                threaded = threading.Thread(target=self.set_employee_active, args=[employee])
                threaded.start()
                # self.set_employee_active(employee)
            end = time.time()
            self.times = end - start

            self.result = True
        except BaseException:
            self.result = False

        return self.times, self.result

    @api.multi
    def set_employee_active(self,records):
        records.write({
            'active': False,
        })

    @api.multi
    def sync_user_from_employee(self):
        with api.Environment.manage():
            domain = ['|', ('active', '=', False),
                      ('active', '=', True)]
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            employees = self.sudo().env['hr.employee'].search(domain)
            users = self.sudo().env['res.users'].search(domain)
            start = time.time()
            for employee in employees:
                user = users.search([
                    ('wxwork_id', '=', employee.wxwork_id),
                    ('is_wxwork_user', '=', True)
                ],limit=1)
                result = threaded_sync = threading.Thread(target=self.user_run, args=[employee,user])
                threaded_sync.start()
            end = time.time()
            times = end - start

            return times,result

    @api.multi
    def user_run(self,employee,user):
        try:
            if len(user) >0:
                self.update_user(employee,user)
            else:
                self.create_user(employee,user)
        except Exception as e:
            print(repr(e))

    @api.multi
    def create_user(self, employee, user):
        groups_id = self.sudo().env['res.groups'].search([('id', '=', 9), ], limit=1).id
        email = None if not employee.work_email else employee.work_email
        image = None if not employee.image else employee.image
        user.create({
            'name': employee.name,
            'login': employee.wxwork_id,
            'oauth_uid': employee.wxwork_id,
            'password': Common(8).random_passwd(),
            'email': email,
            'wxwork_id': employee.wxwork_id,
            'image': image,
            # 'qr_code': employee.qr_code,
            'active': employee.active,
            'wxwork_user_order': employee.wxwork_user_order,
            'mobile': employee.mobile_phone,
            'phone': employee.work_phone,
            'is_wxwork_user': True,
            'is_moderator': False,
            'is_company': False,
            'supplier': False,
            'employee': True,
            'share': False,
            'groups_id': [(6, 0, [groups_id])],  # 设置用户为门户用户
        })
        return True

    @api.multi
    def update_user(self, employee, user):
        user.write({
            'name': employee.name,
            'oauth_uid': employee.wxwork_id,
            'active': employee.active,
            'wxwork_user_order': employee.wxwork_user_order,
            'is_wxwork_user': True,
            'employee': True,
            'mobile': employee.mobile_phone,
            'phone': employee.work_phone,
        })