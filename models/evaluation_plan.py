# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date


class EvaluationPlan(models.Model):
    """
    Modelo para gestionar los Planes de Evaluación de Riesgos
    
    Este modelo permite crear y gestionar planes de evaluación con diferentes etapas
    similares al funcionamiento del CRM de Odoo, con seguimiento de tareas
    relacionadas con la evaluación de riesgos.
    """
    _name = 'evaluation.plan'
    _description = 'Plan de Evaluación de Riesgos'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Hereda funcionalidades de seguimiento
    _order = 'create_date desc'  # Ordenar por fecha de creación descendente
    _rec_name = 'title'  # Campo que se usa como nombre del registro

    # =============================
    # CAMPOS PRINCIPALES
    # =============================
    
    title = fields.Char(
        string='Título',
        required=True,
        tracking=True,  # Permite seguimiento en el chatter
        help='Título descriptivo del plan de evaluación'
    )
    
    risk_id = fields.Many2one(
        comodel_name='risk.management',
        string='Riesgo',
        required=True,
        tracking=True,
        help='Riesgo al cual está asociado este plan de evaluación',
        ondelete='cascade'  # Si se elimina el riesgo, se elimina el plan
    )
    
    assigned_to = fields.Many2one(
        comodel_name='hr.employee',
        string='Asignado a',
        required=True,
        tracking=True,
        # Por defecto el usuario actual
        help='Usuario responsable de ejecutar este plan de evaluación'
    )
    
    start_date = fields.Date(
        string='Fecha de Inicio',
        required=True,
        tracking=True,
        default=fields.Date.today,  # Por defecto la fecha actual
        help='Fecha en que debe iniciarse la ejecución del plan'
    )
    
    due_date = fields.Date(
        string='Fecha de Vencimiento',
        required=True,
        tracking=True,
        help='Fecha límite para completar el plan de evaluación'
    )

    
    task_ids = fields.One2many(
        comodel_name='evaluation.plan.task',
        inverse_name='plan_id',
        string='Tareas',
        help='Lista de tareas asociadas a este plan'
    )

    task_count = fields.Integer(
        string='Número de Tareas',
        compute='_compute_task_count',
        help='Cantidad total de tareas en el plan'
    )

    tasks_done_count = fields.Integer(
        string='Tareas Completadas',
        compute='_compute_task_count',
        help='Cantidad de tareas completadas'
    )


    
    # =============================
    # CAMPOS DE ESTADO Y CONTROL
    # =============================
    
    stage = fields.Selection([
        ('todo', 'Por hacer'),
        ('in_progress', 'En progreso'),
        ('completed', 'Completada')
    ], 
        string='Etapa',
        default='todo',
        required=True,
        tracking=True,
        group_expand='_group_expand_state',
        help='Etapa actual del plan de evaluación'
    )
    
    color = fields.Integer(
        string='Color',
        default=0,
        help='Color para la vista Kanban'
    )
    
    priority = fields.Selection([
        ('0', 'Baja'),
        ('1', 'Normal'), 
        ('2', 'Alta'),
        ('3', 'Crítica')
    ],
        string='Prioridad',
        default='1',
        tracking=True,
        help='Prioridad del plan de evaluación'
    )
    
    # =============================
    # CAMPOS DESCRIPTIVOS
    # =============================
    
    description = fields.Text(
        string='Descripción',
        help='Descripción detallada del plan de evaluación y las actividades a realizar'
    )
    
    notes = fields.Text(
        string='Notas',
        help='Notas adicionales sobre el progreso o comentarios del plan'
    )
    
    # =============================
    # CAMPOS CALCULADOS
    # =============================
    
    progress = fields.Float(
        string='Progreso (%)',
        compute='_compute_progress',
        store=True,
        help='Porcentaje de progreso basado en la etapa actual'
    )
    
    days_to_due = fields.Integer(
        string='Días para Vencimiento',
        compute='_compute_days_to_due',
        help='Número de días restantes hasta la fecha de vencimiento'
    )
    
    is_overdue = fields.Boolean(
        string='Vencido',
        compute='_compute_is_overdue',
        help='Indica si el plan está vencido'
    )
    
    # =============================
    # CAMPOS DE INFORMACIÓN
    # =============================
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        help='Compañía a la que pertenece el plan'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está desmarcado, el plan se oculta sin eliminarlo'
    )

    # =============================
    # MÉTODOS COMPUTADOS
    # =============================
    
    @api.depends('stage', 'task_ids', 'task_ids.state')
    def _compute_progress(self):
        """
        Calcula el progreso basado en la etapa actual y las tareas completadas
        """
        for record in self:
            if record.stage == 'completed':
                record.progress = 100.0
            elif record.stage == 'todo':
                record.progress = 0.0
            elif record.stage == 'in_progress':
                # Si hay tareas, calcular el progreso basado en ellas
                if record.task_count > 0:
                    progress_percentage = (record.tasks_done_count / record.task_count) * 100
                    # El progreso mínimo en 'in_progress' es 10%, máximo 90%
                    record.progress = max(10.0, min(90.0, progress_percentage))
                else:
                    record.progress = 50.0
            else:
                record.progress = 0.0
    
    @api.depends('task_ids', 'task_ids.state')
    def _compute_task_count(self):
        """
        Calcula el número de tareas totales y completadas
        """
        for record in self:
            tasks = record.task_ids
            record.task_count = len(tasks)
            record.tasks_done_count = len(tasks.filtered(lambda t: t.state == 'done'))

    def _check_all_tasks_done(self):
        """
        Verifica si todas las tareas están completadas
        y muestra una notificación
        """
        for record in self:
            if record.task_count > 0 and record.task_count == record.tasks_done_count:
                record.message_post(
                    body='✅ Todas las tareas han sido completadas',
                    message_type='notification'
                )
    
    @api.depends('due_date')
    def _compute_days_to_due(self):
        """
        Calcula los días restantes hasta el vencimiento
        """
        today = date.today()
        for record in self:
            if record.due_date:
                delta = record.due_date - today
                record.days_to_due = delta.days
            else:
                record.days_to_due = 0
    
    @api.depends('due_date', 'stage')
    def _compute_is_overdue(self):
        """
        Determina si el plan está vencido
        """
        today = date.today()
        for record in self:
            if record.due_date and record.stage != 'completed':
                record.is_overdue = record.due_date < today
            else:
                record.is_overdue = False

    @api.depends('activity_ids', 'activity_ids.state')
    def _compute_activity_count(self):
        """
        Calcula el número de actividades totales y completadas
        """
        for record in self:
            activities = record.activity_ids
            record.activity_count = len(activities)
            record.activities_done_count = len(activities.filtered(lambda a: a.state == 'done'))


    # =============================
    # VALIDACIONES
    # =============================
    
    @api.constrains('start_date', 'due_date')
    def _check_dates(self):
        """
        Valida que la fecha de vencimiento sea posterior a la fecha de inicio
        """
        for record in self:
            if record.start_date and record.due_date:
                if record.due_date < record.start_date:
                    raise models.ValidationError(
                        'La fecha de vencimiento debe ser posterior a la fecha de inicio.'
                    )
    
    @api.constrains('stage', 'task_ids', 'task_ids.state')
    def _check_tasks_before_complete(self):
        """
        Valida que todas las tareas estén completadas antes de marcar el plan como completado
        """
        for record in self:
            if record.stage == 'completed' and record.task_count > 0:
                incomplete_tasks = record.task_ids.filtered(
                    lambda t: t.state not in ['done', 'cancelled']
                )
                if incomplete_tasks:
                    task_names = ', '.join(incomplete_tasks.mapped('name'))
                    raise models.ValidationError(
                        f'No se puede completar el plan porque hay tareas pendientes: {task_names}'
                    )

    # =============================
    # MÉTODOS DE ACCIÓN
    # =============================
    
    def action_start_progress(self):
        """
        Cambia la etapa a 'En progreso'
        """
        for record in self:
            if record.stage == 'todo':
                record.write({
                    'stage': 'in_progress'
                })
                record.message_post(
                    body=f'Plan de evaluación iniciado por {self.env.user.name}',
                    message_type='notification'
                )
        return True
    
    def action_complete(self):
        """
        Cambia la etapa a 'Completada'
        """
        for record in self:
            if record.stage in ['todo', 'in_progress']:
                # Verificar si hay tareas pendientes
                if record.task_count > 0:
                    incomplete_tasks = record.task_ids.filtered(
                        lambda t: t.state not in ['done', 'cancelled']
                    )
                    if incomplete_tasks:
                        task_names = ', '.join(incomplete_tasks.mapped('name'))
                        raise models.ValidationError(
                            f'No se puede completar el plan porque hay tareas pendientes: {task_names}'
                        )
                
                record.write({
                    'stage': 'completed'
                })
                record.message_post(
                    body=f'Plan de evaluación completado por {self.env.user.name}',
                    message_type='notification'
                )
        return True
    
    def action_reset_to_todo(self):
        """
        Regresa la etapa a 'Por hacer'
        """
        for record in self:
            if record.stage in ['in_progress', 'completed']:
                record.write({
                    'stage': 'todo'
                })
                record.message_post(
                    body=f'Plan de evaluación reiniciado por {self.env.user.name}',
                    message_type='notification'
                )
        return True

    # =============================
    # MÉTODOS OVERRIDE
    # =============================
    
    @api.model
    def create(self, vals):
        """
        Override del método create para personalizar la creación
        """
        # Mensaje automático al crear
        record = super(EvaluationPlan, self).create(vals)
        record.message_post(
            body=f'Plan de evaluación creado y asignado a {record.assigned_to.name}',
            message_type='notification'
        )
        return record
    
    def write(self, vals):
        """
        Override del método write para seguimiento de cambios
        """
        # Seguimiento de cambio de responsable
        if 'assigned_to' in vals:
            old_user = self.assigned_to
            new_user = self.env['hr.employee'].browse(vals['assigned_to'])
            if old_user != new_user:
                self.message_post(
                    body=f'Plan reasignado de {old_user.name} a {new_user.name}',
                    message_type='notification'
                )
        
        return super(EvaluationPlan, self).write(vals)

    # =============================
    # MÉTODOS DE BÚSQUEDA
    # =============================
    
    @api.model
    def get_overdue_plans(self):
        """
        Retorna los planes vencidos
        """
        return self.search([
            ('is_overdue', '=', True),
            ('active', '=', True)
        ])
    
    @api.model
    def get_my_plans(self):
        """
        Retorna los planes asignados al usuario actual
        """
        return self.search([
            ('assigned_to', '=', self.env.user.id),
            ('active', '=', True)
        ])
    
    @api.model
    def _group_expand_state(self, states, domain, order):
        return ['todo', 'in_progress', 'completed']