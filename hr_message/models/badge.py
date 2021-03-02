# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions


class BadgeUser(models.Model):
    _inherit = "gamification.badge.user"

    def _send_badge(self):
        """
        向用户发送通知以接收徽章 

        不验证徽章授予的约束。 
        将用户添加到owner_ids（如果需要，请创建badge_user） 
        统计计数器增加 
        :param ids: 将会收到徽章的徽章用户list(int)
        """
        user_info = (
            self.env["res.users"]
            .browse(int(self.user_id))
            .read(["notification_type", "wxwork_id"])
        )
        notification_type = user_info[0]["notification_type"]
        wxwork_id = user_info[0]["wxwork_id"]
        print("通知类型", notification_type)
        if notification_type == "wxwork":
            # 消息模板
            template = self.env.ref("hr_message.message_template_badge_received")

        else:
            # 邮件模板
            template = self.env.ref("gamification.email_template_badge_received")

        for badge_user in self:
            self.env["mail.thread"].message_post_with_template(
                template.id,
                model=badge_user._name,
                res_id=badge_user.id,
                composition_mode="mass_mail",
                # `website_forum` 触发 `_cron_update`，触发模板'Received Badge'的方法，该模板的`badge_user.user_id.partner_id.ids'等于`[8]`，然后传递给`self.env ['mail.compose .message'].create（...）`，它需要一个命令列表而不是ID列表。 在master中，这什么也没做，最后composer.partner_ids是[]而不是[8]
                # 我相信这行是无用的，它将从模板本身（`partner_to`）接收必须将模板发送到的伙伴。
                # 因此，下一行毫无意义。
                # partner_ids=badge_user.user_id.partner_id.ids,
            )

        return True
