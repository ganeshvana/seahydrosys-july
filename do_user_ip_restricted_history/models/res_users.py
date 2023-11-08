# -*- coding: utf-8 -*-

from odoo import api, models, fields, registry, SUPERUSER_ID, _
from odoo.http import request
from odoo.exceptions import AccessDenied


class ResUsers(models.Model):
    _inherit = 'res.users'

    login_ips = fields.One2many('login.ips', 'user_id', string='User IP')

    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        with registry(db).cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            ip_address = request.httprequest.environ['REMOTE_ADDR']
            user_id = env['res.users'].sudo().search([('login', '=', login)])
            if user_id.login_ips:
                ip_list = []
                ip_list = user_id.login_ips.mapped('ip_address')
                if ip_address not in ip_list:
                    raise AccessDenied(_("Not allowed to login from this IP Address"))
        return super(ResUsers, cls)._login(db, login, password, user_agent_env=user_agent_env)

    def _check_credentials(self, password, env):
        result = super(ResUsers, self)._check_credentials(password, env)
        ip_address = request.httprequest.environ['REMOTE_ADDR']
        vals = {'user_id': self.id,
                'ip_address': ip_address
                }
        self.env['login.history'].sudo().create(vals)
        return result


class AllowedIPs(models.Model):
    _name = 'login.ips'
    _description = 'Allowed IP Addresses'
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users', string='User')
    ip_address = fields.Char(string='Allowed IP Addresses')


class LoginDetail(models.Model):
    _name = 'login.history'
    _description = 'Login History'
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users', string='User')
    ip_address = fields.Char(string="IP Address")
    login_date = fields.Datetime(string="Login Date Time", default=lambda self: fields.datetime.now())
