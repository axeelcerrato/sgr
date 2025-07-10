# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class RiskReportWizard(models.TransientModel):
    """
    Wizard para generar reportes dinámicos de gestión de riesgos
    
    Permite filtrar y personalizar la información que se incluirá 
    en el reporte PDF generado.
    """
    _name = 'risk.report.wizard'
    _description = 'Wizard de Reporte Dinámico de Riesgos'

    # =============================
    # CAMPOS DE FILTROS PRINCIPALES
    # =============================
    
    report_title = fields.Char(
        string='Título del Reporte',
        default='Reporte de Gestión de Riesgos',
        required=True,
        help='Título que aparecerá en la portada del reporte'
    )
    
    # Filtros de fechas
    date_from = fields.Date(
        string='Fecha Desde',
        default=lambda self: date.today().replace(day=1),  # Primer día del mes actual
        required=True,
        help='Fecha de inicio para filtrar riesgos'
    )
    
    date_to = fields.Date(
        string='Fecha Hasta',
        default=fields.Date.today,
        required=True,
        help='Fecha final para filtrar riesgos'
    )
    
    # Filtros por tipo de riesgo
    include_isms = fields.Boolean(
        string='Incluir ISMS (Seguridad de Información)',
        default=True,
        help='Incluir riesgos de Seguridad de la Información'
    )
    
    include_comp = fields.Boolean(
        string='Incluir COMP (Cumplimiento)',
        default=True,
        help='Incluir riesgos de Cumplimiento Normativo'
    )
    
    include_orm = fields.Boolean(
        string='Incluir ORM (Operacionales)',
        default=True,
        help='Incluir riesgos Operacionales'
    )
    
    # Filtros por categorías
    category_ids = fields.Many2many(
        comodel_name='risk.category',
        string='Categorías Específicas',
        domain=[('active', '=', True)],
        help='Seleccionar categorías específicas (vacío = todas)'
    )
    
    # Filtros por departamentos
    department_ids = fields.Many2many(
        comodel_name='hr.department',
        string='Departamentos',
        help='Seleccionar departamentos específicos (vacío = todos)'
    )
    
    # Filtros por responsables
    responsible_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Responsables',
        help='Seleccionar responsables específicos (vacío = todos)'
    )
    
    # Filtros por nivel de riesgo
    include_low = fields.Boolean(
        string='Riesgos Bajos',
        default=True,
        help='Incluir riesgos de nivel bajo'
    )
    
    include_medium = fields.Boolean(
        string='Riesgos Medios',
        default=True,
        help='Incluir riesgos de nivel medio'
    )
    
    include_high = fields.Boolean(
        string='Riesgos Altos',
        default=True,
        help='Incluir riesgos de nivel alto'
    )
    
    include_critical = fields.Boolean(
        string='Riesgos Críticos',
        default=True,
        help='Incluir riesgos de nivel crítico'
    )
    
    # =============================
    # OPCIONES DE CONTENIDO
    # =============================
    
    include_summary = fields.Boolean(
        string='Incluir Resumen Ejecutivo',
        default=True,
        help='Incluir página de resumen con estadísticas clave'
    )
    
    include_matrix = fields.Boolean(
        string='Incluir Matriz de Riesgos',
        default=True,
        help='Incluir matriz visual de probabilidad vs impacto'
    )
    
    include_risk_details = fields.Boolean(
        string='Incluir Detalles de Riesgos',
        default=True,
        help='Incluir lista detallada de cada riesgo'
    )
    
    include_charts = fields.Boolean(
        string='Incluir Gráficos',
        default=True,
        help='Incluir gráficos de distribución y análisis'
    )
    
    include_action_plans = fields.Boolean(
        string='Incluir Planes de Acción',
        default=True,
        help='Incluir información sobre planes de evaluación asociados'
    )
    
    include_methodology = fields.Boolean(
        string='Incluir Metodología',
        default=False,
        help='Incluir sección explicativa de la metodología utilizada'
    )
    
    # =============================
    # OPCIONES ADICIONALES
    # =============================
    
    group_by_type = fields.Boolean(
        string='Agrupar por Tipo',
        default=True,
        help='Agrupar riesgos por tipo (ISMS, COMP, ORM) en el reporte'
    )
    
    group_by_category = fields.Boolean(
        string='Agrupar por Categoría',
        default=False,
        help='Agrupar riesgos por categoría en el reporte'
    )
    
    sort_by_risk_level = fields.Boolean(
        string='Ordenar por Nivel de Riesgo',
        default=True,
        help='Ordenar riesgos por nivel (crítico → bajo)'
    )
    
    # =============================
    # CAMPOS CALCULADOS
    # =============================
    
    estimated_risks = fields.Integer(
        string='Riesgos Estimados',
        compute='_compute_estimated_risks',
        help='Número estimado de riesgos que incluirá el reporte'
    )
    
    # =============================
    # MÉTODOS COMPUTADOS
    # =============================
    
    @api.depends('date_from', 'date_to', 'include_isms', 'include_comp', 'include_orm',
                 'category_ids', 'department_ids', 'responsible_ids',
                 'include_low', 'include_medium', 'include_high', 'include_critical')
    def _compute_estimated_risks(self):
        """
        Calcula el número estimado de riesgos que incluirá el reporte
        """
        for wizard in self:
            domain = wizard._build_risk_domain()
            wizard.estimated_risks = self.env['risk.management'].search_count(domain)
    
    def _build_risk_domain(self):
        """
        Construye el dominio de búsqueda basado en los filtros seleccionados
        """
        domain = []
        
        # Filtro por fechas
        if self.date_from:
            domain.append(('identification_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('identification_date', '<=', self.date_to))
        
        # Filtro por tipos de riesgo
        risk_types = []
        if self.include_isms:
            risk_types.append('ISMS')
        if self.include_comp:
            risk_types.append('COMP')
        if self.include_orm:
            risk_types.append('ORM')
        
        if risk_types:
            domain.append(('risk_type', 'in', risk_types))
        else:
            # Si no se selecciona ningún tipo, no mostrar nada
            domain.append(('id', '=', False))
        
        # Filtro por categorías
        if self.category_ids:
            domain.append(('category_id', 'in', self.category_ids.ids))
        
        # Filtro por departamentos
        if self.department_ids:
            domain.append(('department_id', 'in', self.department_ids.ids))
        
        # Filtro por responsables
        if self.responsible_ids:
            domain.append(('responsible_id', 'in', self.responsible_ids.ids))
        
        # Filtro por niveles de riesgo
        risk_levels = []
        if self.include_low:
            risk_levels.append('low')
        if self.include_medium:
            risk_levels.append('medium')
        if self.include_high:
            risk_levels.append('high')
        if self.include_critical:
            risk_levels.append('critical')
        
        if risk_levels:
            domain.append(('risk_level', 'in', risk_levels))
        else:
            # Si no se selecciona ningún nivel, no mostrar nada
            domain.append(('id', '=', False))
        
        return domain
    
    def _get_filtered_risks(self):
        """
        Obtiene los riesgos filtrados según los criterios seleccionados
        """
        domain = self._build_risk_domain()
        
        # Definir orden
        order = 'identification_date desc'
        if self.sort_by_risk_level:
            # Ordenar por nivel de riesgo: crítico, alto, medio, bajo
            order = 'stage_sequence, identification_date desc'
        
        return self.env['risk.management'].search(domain, order=order)
    
    def _get_report_statistics(self, risks):
        """
        Calcula estadísticas para el reporte
        """
        total = len(risks)
        
        # Estadísticas por nivel
        critical = len(risks.filtered(lambda r: r.risk_level == 'critical'))
        high = len(risks.filtered(lambda r: r.risk_level == 'high'))
        medium = len(risks.filtered(lambda r: r.risk_level == 'medium'))
        low = len(risks.filtered(lambda r: r.risk_level == 'low'))
        
        # Estadísticas por tipo
        isms = len(risks.filtered(lambda r: r.risk_type == 'ISMS'))
        comp = len(risks.filtered(lambda r: r.risk_type == 'COMP'))
        orm = len(risks.filtered(lambda r: r.risk_type == 'ORM'))
        
        # Planes de acción
        total_plans = self.env['evaluation.plan'].search_count([
            ('risk_id', 'in', risks.ids)
        ])
        
        completed_plans = self.env['evaluation.plan'].search_count([
            ('risk_id', 'in', risks.ids),
            ('stage', '=', 'completed')
        ])
        
        return {
            'total_risks': total,
            'critical_risks': critical,
            'high_risks': high,
            'medium_risks': medium,
            'low_risks': low,
            'isms_risks': isms,
            'comp_risks': comp,
            'orm_risks': orm,
            'total_plans': total_plans,
            'completed_plans': completed_plans,
            'critical_percentage': round((critical / total * 100) if total > 0 else 0, 1),
            'high_percentage': round((high / total * 100) if total > 0 else 0, 1),
            'completion_rate': round((completed_plans / total_plans * 100) if total_plans > 0 else 0, 1)
        }
    
    # =============================
    # VALIDACIONES
    # =============================
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """
        Valida que las fechas sean coherentes
        """
        for wizard in self:
            if wizard.date_from and wizard.date_to:
                if wizard.date_from > wizard.date_to:
                    raise models.ValidationError(
                        'La fecha de inicio debe ser anterior a la fecha final.'
                    )
                
                # Validar que no sea un rango muy grande (más de 2 años)
                if (wizard.date_to - wizard.date_from).days > 730:
                    raise models.ValidationError(
                        'El rango de fechas no puede ser mayor a 2 años. '
                        'Seleccione un período más específico.'
                    )
    
    @api.constrains('include_isms', 'include_comp', 'include_orm')
    def _check_risk_types(self):
        """
        Valida que al menos un tipo de riesgo esté seleccionado
        """
        for wizard in self:
            if not (wizard.include_isms or wizard.include_comp or wizard.include_orm):
                raise models.ValidationError(
                    'Debe seleccionar al menos un tipo de riesgo para el reporte.'
                )
    
    @api.constrains('include_low', 'include_medium', 'include_high', 'include_critical')
    def _check_risk_levels(self):
        """
        Valida que al menos un nivel de riesgo esté seleccionado
        """
        for wizard in self:
            if not (wizard.include_low or wizard.include_medium or 
                   wizard.include_high or wizard.include_critical):
                raise models.ValidationError(
                    'Debe seleccionar al menos un nivel de riesgo para el reporte.'
                )
    
    # =============================
    # MÉTODOS DE ACCIÓN
    # =============================
    
    def action_generate_report(self):
        """
        Acción principal para generar el reporte PDF
        """
        self.ensure_one()
        
        # Validar que hay riesgos para reportar
        if self.estimated_risks == 0:
            raise models.UserError(
                'No hay riesgos que coincidan con los criterios seleccionados. '
                'Ajuste los filtros e intente nuevamente.'
            )
        
        # Crear contexto con los datos del wizard
        context = {
            'wizard_data': {
                'report_title': self.report_title,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'include_summary': self.include_summary,
                'include_matrix': self.include_matrix,
                'include_risk_details': self.include_risk_details,
                'include_charts': self.include_charts,
                'include_action_plans': self.include_action_plans,
                'include_methodology': self.include_methodology,
                'group_by_type': self.group_by_type,
                'group_by_category': self.group_by_category,
                'sort_by_risk_level': self.sort_by_risk_level,
            }
        }
        
        # Generar el reporte PDF
        return self.env.ref('sgr.action_report_risk_dynamic').with_context(context).report_action(self)
    
    def action_preview_data(self):
        """
        Acción para previsualizar los datos que se incluirán en el reporte
        """
        self.ensure_one()
        
        risks = self._get_filtered_risks()
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Vista Previa: {len(risks)} Riesgos',
            'res_model': 'risk.management',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', risks.ids)],
            'context': {'search_default_group_by_type': 1},
            'target': 'new',
        }
    
    def action_reset_filters(self):
        """
        Restaura los filtros a los valores por defecto
        """
        self.write({
            'date_from': date.today().replace(day=1),
            'date_to': date.today(),
            'include_isms': True,
            'include_comp': True,
            'include_orm': True,
            'category_ids': [(5, 0, 0)],  # Limpiar relación many2many
            'department_ids': [(5, 0, 0)],
            'responsible_ids': [(5, 0, 0)],
            'include_low': True,
            'include_medium': True,
            'include_high': True,
            'include_critical': True,
            'include_summary': True,
            'include_matrix': True,
            'include_risk_details': True,
            'include_charts': True,
            'include_action_plans': True,
            'include_methodology': False,
            'group_by_type': True,
            'group_by_category': False,
            'sort_by_risk_level': True,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'risk.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    # =============================
    # MÉTODOS DE UTILIDAD
    # =============================
    
    @api.model
    def default_get(self, fields_list):
        """
        Establece valores por defecto inteligentes
        """
        defaults = super(RiskReportWizard, self).default_get(fields_list)
        
        # Si hay riesgos en el sistema, usar la fecha del más antiguo como inicio
        oldest_risk = self.env['risk.management'].search([], order='identification_date asc', limit=1)
        if oldest_risk:
            # Tomar desde el inicio del mes del riesgo más antiguo
            defaults['date_from'] = oldest_risk.identification_date.replace(day=1)
        
        return defaults