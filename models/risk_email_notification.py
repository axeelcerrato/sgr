# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime


class RiskEmailNotification(models.Model):
    """
    Modelo para manejar notificaciones por correo de riesgos
    """
    _name = 'risk.email.notification'
    _description = 'Notificaciones por Correo de Riesgos'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(
        string='Asunto',
        required=True,
        help='Asunto del correo enviado'
    )
    
    notification_type = fields.Selection([
        ('critical_risk', 'Riesgo Crítico Identificado'),
        ('plan_overdue', 'Plan de Acción Vencido'),
    ], string='Tipo de Notificación', required=True)
    
    risk_id = fields.Many2one(
        'risk.management',
        string='Riesgo Relacionado',
        help='Riesgo que generó la notificación'
    )
    
    plan_id = fields.Many2one(
        'evaluation.plan',
        string='Plan Relacionado',
        help='Plan que generó la notificación'
    )
    
    recipients = fields.Text(
        string='Destinatarios',
        help='Lista de correos que recibieron la notificación'
    )
    
    sent_date = fields.Datetime(
        string='Fecha de Envío',
        default=fields.Datetime.now,
        help='Fecha y hora en que se envió el correo'
    )
    
    mail_message_id = fields.Many2one(
        'mail.message',
        string='Mensaje de Correo',
        help='Referencia al mensaje de correo enviado'
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Enviado'),
        ('failed', 'Fallido'),
    ], string='Estado', default='draft')


class RiskManagement(models.Model):
    """
    Extender el modelo de gestión de riesgos para agregar funcionalidad de correos
    """
    _inherit = 'risk.management'
    
    email_notifications_count = fields.Integer(
        string='Notificaciones Enviadas',
        compute='_compute_email_notifications'
    )
    
    def _compute_email_notifications(self):
        """Contar las notificaciones enviadas para este riesgo"""
        for record in self:
            record.email_notifications_count = self.env['risk.email.notification'].search_count([
                ('risk_id', '=', record.id)
            ])
    
    def action_view_email_notifications(self):
        """Ver las notificaciones enviadas para este riesgo"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Notificaciones - {self.title}',
            'res_model': 'risk.email.notification',
            'view_mode': 'tree,form',
            'domain': [('risk_id', '=', self.id)],
            'context': {'default_risk_id': self.id},
        }
    
    def send_critical_risk_notification(self):
        """Enviar notificación de riesgo crítico"""
        if self.risk_level == 'critical':
            template = self.env.ref('sgr.email_template_critical_risk', raise_if_not_found=False)
            if template:
                # Obtener destinatarios
                recipients = self._get_critical_risk_recipients()
                
                if recipients:
                    # Preparar el contexto
                    context = {
                        'risk_title': self.title,
                        'risk_number': self.request_number,
                        'risk_level': self.risk_level,
                        'responsible_name': self.responsible_id.name,
                        'department_name': self.department_id.name,
                        'identification_date': self.identification_date,
                        'description': self.description,
                        'company_name': self.company_id.name,
                    }
                    
                    # Enviar correo
                    mail_id = template.with_context(context).send_mail(
                        self.id, 
                        force_send=True,
                        email_values={
                            'email_to': ', '.join(recipients),
                            'subject': f'🚨 RIESGO CRÍTICO IDENTIFICADO - {self.request_number}'
                        }
                    )
                    
                    # Registrar la notificación
                    self.env['risk.email.notification'].create({
                        'name': f'Riesgo Crítico: {self.title}',
                        'notification_type': 'critical_risk',
                        'risk_id': self.id,
                        'recipients': ', '.join(recipients),
                        'mail_message_id': mail_id,
                        'state': 'sent'
                    })
                    
                    # Mensaje en el chatter
                    self.message_post(
                        body=f"📧 Notificación de riesgo crítico enviada a: {', '.join(recipients)}",
                        message_type='notification'
                    )
    
    def _get_critical_risk_recipients(self):
        """Obtener lista de correos para notificaciones de riesgo crítico"""
        recipients = []
        
        # Responsable del riesgo
        if self.responsible_id and self.responsible_id.work_email:
            recipients.append(self.responsible_id.work_email)
        
        # Usuarios con rol de Gestor de Riesgos
        risk_managers = self.env['res.users'].search([
            ('groups_id', 'in', self.env.ref('sgr.group_risk_manager').id)
        ])
        for manager in risk_managers:
            if manager.email and manager.email not in recipients:
                recipients.append(manager.email)
        
        # Jefe del departamento (si existe)
        if self.department_id and self.department_id.manager_id and self.department_id.manager_id.work_email:
            if self.department_id.manager_id.work_email not in recipients:
                recipients.append(self.department_id.manager_id.work_email)
        
        return recipients
    
    @api.model
    def create(self, vals):
        """Override create para enviar notificación automática"""
        record = super(RiskManagement, self).create(vals)
        
        # Enviar notificación si es riesgo crítico
        if record.risk_level == 'critical':
            record.send_critical_risk_notification()
        
        return record
    
    def write(self, vals):
        """Override write para detectar cambios a riesgo crítico"""
        # Verificar si se está cambiando a riesgo crítico
        old_levels = {record.id: record.risk_level for record in self}
        
        result = super(RiskManagement, self).write(vals)
        
        # Enviar notificación si cambió a crítico
        for record in self:
            if (record.risk_level == 'critical' and 
                old_levels.get(record.id) != 'critical'):
                record.send_critical_risk_notification()
        
        return result


class EvaluationPlan(models.Model):
    """
    Extender el modelo de planes de evaluación para correos
    """
    _inherit = 'evaluation.plan'
    
    email_notifications_count = fields.Integer(
        string='Notificaciones Enviadas',
        compute='_compute_email_notifications'
    )
    
    def _compute_email_notifications(self):
        """Contar las notificaciones enviadas para este plan"""
        for record in self:
            record.email_notifications_count = self.env['risk.email.notification'].search_count([
                ('plan_id', '=', record.id)
            ])
    
    def send_overdue_plan_notification(self):
        """Enviar notificación de plan vencido"""
        if self.is_overdue and self.stage != 'completed':
            template = self.env.ref('sgr.email_template_plan_overdue', raise_if_not_found=False)
            if template:
                # Obtener destinatarios
                recipients = self._get_plan_overdue_recipients()
                
                if recipients:
                    # Preparar el contexto
                    context = {
                        'plan_title': self.title,
                        'risk_title': self.risk_id.title,
                        'risk_number': self.risk_id.request_number,
                        'assigned_to': self.assigned_to.name,
                        'due_date': self.due_date,
                        'days_overdue': abs(self.days_to_due),
                        'progress': self.progress,
                        'company_name': self.company_id.name,
                    }
                    
                    # Enviar correo
                    mail_id = template.with_context(context).send_mail(
                        self.id,
                        force_send=True,
                        email_values={
                            'email_to': ', '.join(recipients),
                            'subject': f'⏰ PLAN DE ACCIÓN VENCIDO - {self.title}'
                        }
                    )
                    
                    # Registrar la notificación
                    self.env['risk.email.notification'].create({
                        'name': f'Plan Vencido: {self.title}',
                        'notification_type': 'plan_overdue',
                        'plan_id': self.id,
                        'risk_id': self.risk_id.id,
                        'recipients': ', '.join(recipients),
                        'mail_message_id': mail_id,
                        'state': 'sent'
                    })
                    
                    # Mensaje en el chatter
                    self.message_post(
                        body=f"📧 Notificación de plan vencido enviada a: {', '.join(recipients)}",
                        message_type='notification'
                    )
    
    def _get_plan_overdue_recipients(self):
        """Obtener lista de correos para notificaciones de plan vencido"""
        recipients = []
        
        # Responsable asignado
        if self.assigned_to and self.assigned_to.work_email:
            recipients.append(self.assigned_to.work_email)
        
        # Usuarios con rol de Gestor de Riesgos
        risk_managers = self.env['res.users'].search([
            ('groups_id', 'in', self.env.ref('sgr.group_risk_manager').id)
        ])
        for manager in risk_managers:
            if manager.email and manager.email not in recipients:
                recipients.append(manager.email)
        
        return recipients
    
    @api.model
    def check_overdue_plans(self):
        """Método cron para verificar planes vencidos"""
        today = date.today()
        overdue_plans = self.search([
            ('due_date', '<', today),
            ('stage', '!=', 'completed'),
            ('active', '=', True)
        ])
        
        for plan in overdue_plans:
            # Verificar si ya se envió notificación hoy
            notification_today = self.env['risk.email.notification'].search([
                ('plan_id', '=', plan.id),
                ('notification_type', '=', 'plan_overdue'),
                ('sent_date', '>=', datetime.combine(today, datetime.min.time())),
            ])
            
            if not notification_today:
                plan.send_overdue_plan_notification()