# -*- coding: utf-8 -*-

import json
from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import except_orm, Warning, RedirectWarning, AccessDenied
import odoo.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def auth_oauth_wxwork(self, provider, validation):
        # def auth_oauth_wxwork(self, provider, params):
        """
        允许一键登录和扫码登录且标记了企业微信的用户登录系统
        :param provider:
        :param validation:
        :return:
        """
        auth_endpoint = "https://open.weixin.qq.com/connect/oauth2/authorize"
        qr_auth_endpoint = "https://open.work.weixin.qq.com/wwopen/sso/qrConnect"

        wxwork_providers = (
            self.env["auth.oauth.provider"].sudo().search([("id", "=", provider),])
        )

        # print(provider, validation)
        if (
            auth_endpoint in wxwork_providers["auth_endpoint"]
            or qr_auth_endpoint in wxwork_providers["auth_endpoint"]
        ):
            oauth_userid = validation["UserId"]
            oauth_user = self.search(
                [("oauth_uid", "=", oauth_userid), ("is_wxwork_user", "=", True)]
            )
            if not oauth_user or len(oauth_user) > 1:
                return AccessDenied
            # return user credentials
            return (self.env.cr.dbname, oauth_user.login, oauth_userid)
        else:
            return AccessDenied

    @api.model
    def _check_credentials(self, password, env):
        # password为企业微信的用户ID
        try:
            return super(ResUsers, self)._check_credentials(password, env)
        except AccessDenied:
            passwd_allowed = (
                env["interactive"] or not self.env.user._rpc_api_keys_only()
            )
            if passwd_allowed and self.env.user.active:
                res = self.sudo().search(
                    [("id", "=", self.env.uid), ("oauth_uid", "=", password)]
                )
                if res:
                    return
            raise
            # res = self.sudo().search(
            #     [("id", "=", self.env.uid), ("oauth_uid", "=", password)]
            # )
            # if not res:
            #     raise
