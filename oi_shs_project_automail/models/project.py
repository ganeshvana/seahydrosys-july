from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    @api.model
    def send_task_completed_email(self):
        completed_tasks = self.search([('stage_id.name', '=', 'Completed')])
        for task in completed_tasks:
            mail_template = self.env.ref('oi_shs_project_automail.mail_template_task_complete')
            mail_template.send_mail(task.id, force_send=True)
