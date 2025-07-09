# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date


class EvaluationPlanTask(models.Model):
    """
    Modelo para gestionar las tareas de un Plan de Evaluación
    
    Este modelo permite crear tareas específicas dentro de cada plan de evaluación
    para un seguimiento más detallado del progreso.
    """
    _name = 'evaluation.plan.task'
    _description = 'Tarea del Plan de Evaluación'
    _order = 'sequence, id'
    _rec_name = 'name'

    # =============================
    # CAMPOS PRINCIPALES
    # =============================
    
    name = fields.Char(
        string='Nombre de la Tarea',
        required=True,
        help='Descripción breve de la tarea a realizar'
    )
    
    plan_id = fields.Many2one(
        comodel_name='evaluation.plan',
        string='Plan de Evaluación',
        required=True,
        ondelete='cascade',
        help='Plan de evaluación al que pertenece esta tarea'
    )
    
    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help='Orden de la tarea en la lista'
    )
    
    # =============================
    # CAMPOS DE ESTADO
    # =============================
    
    state = fields.Selection([
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('done', 'Completada'),
        ('cancelled', 'Cancelada')
    ],
        string='Estado',
        default='pending',
        required=True,
        help='Estado actual de la tarea'
    )
    
    # Campo de prioridad eliminado según solicitud
    
    # =============================
    # CAMPOS DE FECHAS
    # =============================
    
    date_deadline = fields.Date(
        string='Fecha Límite',
        help='Fecha límite para completar esta tarea'
    )
    
    date_done = fields.Datetime(
        string='Fecha de Completado',
        readonly=True,
        help='Fecha y hora en que se completó la tarea'
    )
    
    # =============================
    # CAMPOS DESCRIPTIVOS
    # =============================
    
    description = fields.Text(
        string='Descripción Detallada',
        help='Descripción completa de la tarea y los pasos a seguir'
    )
    
    responsible_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Responsable',
        help='Empleado responsable de esta tarea específica'
    )
    
    # =============================
    # CAMPOS CALCULADOS
    # =============================
    
    is_overdue = fields.Boolean(
        string='Vencida',
        compute='_compute_is_overdue',
        help='Indica si la tarea está vencida'
    )
    
    days_to_deadline = fields.Integer(
        string='Días para Vencimiento',
        compute='_compute_days_to_deadline',
        help='Número de días restantes hasta la fecha límite'
    )
    
    progress = fields.Float(
        string='Progreso (%)',
        default=0.0,
        help='Porcentaje de progreso de la tarea'
    )
    
    # =============================
    # MÉTODOS COMPUTADOS
    # =============================
    
    @api.depends('date_deadline', 'state')
    def _compute_is_overdue(self):
        """
        Determina si la tarea está vencida
        """
        today = date.today()
        for record in self:
            if record.date_deadline and record.state not in ['done', 'cancelled']:
                record.is_overdue = record.date_deadline < today
            else:
                record.is_overdue = False
    
    @api.depends('date_deadline')
    def _compute_days_to_deadline(self):
        """
        Calcula los días restantes hasta el vencimiento
        """
        today = date.today()
        for record in self:
            if record.date_deadline:
                delta = record.date_deadline - today
                record.days_to_deadline = delta.days
            else:
                record.days_to_deadline = 0
    
    # =============================
    # MÉTODOS DE ACCIÓN
    # =============================
    
    def action_start(self):
        """
        Inicia la tarea
        """
        self.ensure_one()
        if self.state == 'pending':
            self.state = 'in_progress'
            # Actualizar el progreso
            if self.progress == 0:
                self.progress = 25.0
        return True
    
    def action_done(self):
        """
        Marca la tarea como completada
        """
        self.ensure_one()
        self.write({
            'state': 'done',
            'date_done': fields.Datetime.now(),
            'progress': 100.0
        })
        # Verificar si todas las tareas están completadas
        self.plan_id._check_all_tasks_done()
        return True
    
    def action_cancel(self):
        """
        Cancela la tarea
        """
        self.ensure_one()
        self.state = 'cancelled'
        return True
    
    def action_reset(self):
        """
        Reinicia la tarea a pendiente
        """
        self.ensure_one()
        self.write({
            'state': 'pending',
            'date_done': False,
            'progress': 0.0
        })
        return True
    
    # =============================
    # MÉTODOS OVERRIDE
    # =============================
    
    @api.model
    def create(self, vals):
        """
        Override para asignar secuencia automática
        """
        # Si no se especifica responsable, intentar obtener el empleado del usuario asignado al plan
        if 'responsible_id' not in vals and 'plan_id' in vals:
            plan = self.env['evaluation.plan'].browse(vals['plan_id'])
            # Buscar el empleado relacionado con el usuario asignado
            employee = self.env['hr.employee'].search([
                ('user_id', '=', plan.assigned_to.id)
            ], limit=1)
            if employee:
                vals['responsible_id'] = employee.id
        
        # Asignar secuencia si no se especifica
        if 'sequence' not in vals and 'plan_id' in vals:
            last_task = self.search([
                ('plan_id', '=', vals['plan_id'])
            ], order='sequence desc', limit=1)
            vals['sequence'] = last_task.sequence + 10 if last_task else 10
        
        return super(EvaluationPlanTask, self).create(vals)