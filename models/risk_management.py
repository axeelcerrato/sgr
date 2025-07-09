from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RiskManagement(models.Model):
    """
    Modelo principal para la gestión de riesgos empresariales
    Permite registrar, evaluar y dar seguimiento a los riesgos identificados
    """
    _name = 'risk.management'
    _description = 'Gestión de Riesgos'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_number desc'
    _rec_name = 'title'
    
    # Nuevo campo Tipo
    risk_type = fields.Selection([
        ('ISMS', 'ISMS - Seguridad de la Información'),
        ('COMP', 'COMP - Cumplimiento Normativo'),
        ('ORM', 'ORM - Riesgos Operacionales')
    ], 
        string='Tipo',
        required=True,
        default='ORM',
        tracking=True,
        help='Tipo de gestión de riesgo'
    )
    
    # Número de solicitud automático basado en tipo
    request_number = fields.Char(
        string='Número de Solicitud',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo',
        help='Número único de identificación del riesgo basado en el tipo'
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        help='Compañía a la que pertenece el riesgo'
    )
    
    # Información básica del riesgo
    title = fields.Char(
        string='Título',
        required=True,
        tracking=True,
        help='Título descriptivo del riesgo identificado'
    )
    
    description = fields.Text(
        string='Descripción',
        required=True,
        help='Descripción detallada del riesgo y sus posibles consecuencias'
    )
    
    # Categorización
    category_id = fields.Many2one(
        'risk.category',
        string='Categoría',
        required=True,
        domain=[('active', '=', True)],
        help='Categoría a la que pertenece este riesgo'
    )
    
    # Información de seguimiento
    created_by = fields.Many2one(
        'res.users',
        string='Creado por',
        default=lambda self: self.env.user,
        readonly=True,
        help='Usuario que identificó y registró el riesgo'
    )
    
    identification_date = fields.Date(
        string='Fecha de Identificación',
        default=fields.Date.context_today,
        required=True,
        tracking=True,
        help='Fecha en que se identificó el riesgo'
    )

    stage_sequence = fields.Integer(
        string='Secuencia de Etapa',
        compute='_compute_stage_sequence',
        store=True
    )

    @api.depends('stage')
    def _compute_stage_sequence(self):
        stage_order = {
            'draft': 1,        # Borrador
            'evaluated': 2,    # Evaluado  
            'treatment': 3,    # En Tratamiento
            'closed': 4,       # Cerrado
            'cancelled': 5     # Cancelado
        }
        for record in self:
            record.stage_sequence = stage_order.get(record.stage, 0)
    
    # Etapas del proceso
    stage = fields.Selection([
        ('draft', 'Borrador'),
        ('evaluated', 'Evaluado'),
        ('treatment', 'En Tratamiento'),
        ('closed', 'Cerrado'),
        ('cancelled', 'Cancelado')
    ], string='Etapa', default='draft', required=True, tracking=True,
       help='Etapa actual del proceso de gestión del riesgo')
    
    # Evaluación de riesgo - Impacto
    impact = fields.Selection([
        ('20', 'Insignificante (20%)'),
        ('40', 'Menor (40%)'),
        ('60', 'Moderado (60%)'),
        ('80', 'Mayor (80%)'),
        ('100', 'Catastrófico (100%)')
    ], string='Impacto', required=True, tracking=True,
       help='Nivel de impacto que tendría la materialización del riesgo')
    
    # Evaluación de riesgo - Probabilidad
    probability = fields.Selection([
        ('20', 'Improbable (20%)'),
        ('40', 'Posible (40%)'),
        ('60', 'Ocasional (60%)'),
        ('80', 'Probable (80%)'),
        ('100', 'Frecuente (100%)')
    ], string='Probabilidad', required=True, tracking=True,
       help='Probabilidad de que ocurra el riesgo')
    
    # Campos de cálculo automático
    risk_score = fields.Float(
        string='Puntuación del Riesgo',
        compute='_compute_risk_score',
        store=True,
        help='Puntuación calculada: Probabilidad × Impacto'
    )
    
    risk_level = fields.Selection([
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
        ('critical', 'Crítico')  
    ],
        string='Nivel de Riesgo',
        compute='_compute_risk_level',
        store=True,
        tracking=True,
        help='Nivel calculado basado en la puntuación de riesgo'
    )
    
    # Departamento
    department_id = fields.Many2one(
        'hr.department',
        string='Departamento',
        required=True,
        tracking=True,
        help='Departamento al que pertenece este riesgo'
    )
    
    # Responsable (Empleado)
    responsible_id = fields.Many2one(
        'hr.employee',
        string='Responsable/Asignado',
        required=True,
        tracking=True,
        help='Empleado responsable de gestionar este riesgo'
    )
    
    # Tipos de riesgo
    inherent_risk_level = fields.Selection([
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
        ('critical', 'Crítico')  
    ],
        string='Nivel de Riesgo Inherente',
        compute='_compute_inherent_risk_level',
        store=True,
        help='Nivel de riesgo sin controles aplicados'
    )
    
    residual_risk_level = fields.Selection([
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
        ('critical', 'Crítico')  
    ],
        string='Nivel de Riesgo Residual',
        default='low',
        help='Nivel de riesgo después de aplicar controles'
    )
    
    inherent_risk = fields.Text(
        string='Riesgo Inherente',
        help='Descripción del riesgo sin considerar controles existentes'
    )
    
    residual_risk = fields.Text(
        string='Riesgo Residual',
        help='Descripción del riesgo después de aplicar controles y medidas de mitigación'
    )
    
    # Matriz de riesgo 5x5
    matriz_visual = fields.Html(
        string='Matriz Visual',
        compute='_compute_matriz_visual',
        help='Representación visual de la matriz de riesgo 5x5'
    )
    
    # Campos adicionales para mejor gestión
    priority = fields.Selection([
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica')
    ], string='Prioridad', compute='_compute_priority', store=True, help='Prioridad calculada automáticamente basada en el nivel de riesgo')
    
    # Color para vista kanban
    color = fields.Integer('Color', compute='_compute_color')
   

    

    # Relación con planes de evaluación
    evaluation_plan_count = fields.Integer(
    string='Cantidad de Planes',
    compute='_compute_evaluation_plan_count',
    help='Número de planes de evaluación asociados a este riesgo'
    )

    @api.depends('impact', 'probability', 'risk_score')
    def _compute_matriz_visual(self):
        """
        Genera la representación HTML de la matriz de riesgo 5x5
        """
        for record in self:
            if not record.impact or not record.probability:
                record.matriz_visual = '<p>Seleccione impacto y probabilidad para ver la matriz</p>'
                continue
                
            # Valores para la matriz (usando tus campos existentes)
            valores_impacto = ['20', '40', '60', '80', '100']
            valores_probabilidad = ['100', '80', '60', '40', '20']  # Orden inverso
            labels_impacto = ['Insignificante', 'Menor', 'Moderado', 'Mayor', 'Catastrófico']
            labels_probabilidad = ['Frecuente', 'Probable', 'Ocasional', 'Posible', 'Improbable']
            
            # Construir HTML de la matriz
            html = '''
            <div class="risk_matrix_container">
                
                <div style="display: flex; justify-content: center; width: 100%;">
                    <div style="display: grid; grid-template-columns: 80px repeat(5, 65px); grid-template-rows: 50px repeat(5, 65px); gap: 1px; border: 2px solid #ddd; border-radius: 8px; padding: 8px; background: white;">
                        <!-- Celda vacía esquina -->
                        <div style="display: flex; align-items: center; justify-content: center; background: #f8f9fa; font-weight: bold; font-size: 10px; border-radius: 4px;"></div>
            '''
            
            # Headers de impacto
            for i, label in enumerate(labels_impacto):
                html += f'<div style="display: flex; align-items: center; justify-content: center; background: #e9ecef; font-weight: bold; font-size: 11px; text-align: center; padding: 4px; border-radius: 4px; border: 1px solid #dee2e6;">{label}</div>'
            
            # Filas de la matriz
            for i, prob_val in enumerate(valores_probabilidad):
                # Label de probabilidad
                html += f'<div style="display: flex; align-items: center; justify-content: center; background: #e9ecef; font-weight: bold; font-size: 11px; text-align: center; padding: 4px; border-radius: 4px; border: 1px solid #dee2e6;">{labels_probabilidad[i]}</div>'
                
                # Celdas de riesgo
                for imp_val in valores_impacto:
                    riesgo_val = (int(imp_val) / 100) * (int(prob_val) / 100) * 100
                    
                    # Determinar color según el riesgo
                    if riesgo_val <= 15:
                        color = '#4CAF50'  # Verde - Bajo
                        nivel = 'Bajo'
                    elif riesgo_val <= 36:
                        color = '#FFC107'  # Amarillo - Medio
                        nivel = 'Medio'
                    elif riesgo_val <= 59:
                        color = "#FF7300"  # Naranja - Alto
                        nivel = 'Alto'
                    else:
                        color = '#F44336'  # Rojo - Crítico
                        nivel = 'Crítico'
                    
                    # Marcar celda activa
                    border_style = 'border: 1px solid #dee2e6;'
                    if record.impact == imp_val and record.probability == prob_val:
                        border_style = 'border: 3px solid #007bff; box-shadow: 0 0 10px rgba(0, 123, 255, 0.5);'
                    
                    html += f'''
                    <div style="display: flex; align-items: center; justify-content: center; 
                               background: {color}; color: white; font-size: 12px; font-weight: bold; 
                               border-radius: 4px; {border_style} min-height: 55px; text-align: center; 
                               cursor: pointer; transition: all 0.2s ease;"
                         title="Impacto: {imp_val}% - Probabilidad: {prob_val}% - Riesgo: {riesgo_val:.0f}% ({nivel})"
                         onmouseover="this.style.transform='scale(1.05)'; this.style.zIndex='10';"
                         onmouseout="this.style.transform='scale(1)'; this.style.zIndex='1';">
                        {riesgo_val:.0f}%
                    </div>
                    '''          
            
            html += '</div>'
            record.matriz_visual = html
    
    @api.model
    def create(self, vals):
        """
        Genera número de solicitud automático basado en el tipo seleccionado
        """
        if vals.get('request_number', 'Nuevo') == 'Nuevo' and vals.get('risk_type'):
            risk_type = vals['risk_type']
            
            # Buscar el último número para este tipo
            last_record = self.search([
                ('risk_type', '=', risk_type)
            ], order='id desc', limit=1)
            
            if last_record and last_record.request_number:
                try:
                    # Extraer número del último código del mismo tipo
                    prefix = f'{risk_type}-'
                    if last_record.request_number.startswith(prefix):
                        last_number = int(last_record.request_number.replace(prefix, ''))
                        next_number = last_number + 1
                    else:
                        next_number = 1
                except (ValueError, AttributeError):
                    next_number = 1
            else:
                next_number = 1
            
            # Generar nuevo código con formato TIPO-XXXX
            vals['request_number'] = f'{risk_type}-{next_number:04d}'
        
        return super(RiskManagement, self).create(vals)
    
    @api.depends('probability', 'impact')
    def _compute_risk_score(self):
        """
        Calcula la puntuación del riesgo: Probabilidad × Impacto / 100
        """
        for record in self:
            if record.probability and record.impact:
                prob_value = float(record.probability)
                impact_value = float(record.impact)
                record.risk_score = (prob_value * impact_value) / 100
            else:
                record.risk_score = 0.0
    
    @api.depends('risk_score')
    def _compute_risk_level(self):
        """
        Calcula el nivel de riesgo basado en la puntuación
        Bajo: 0-20%, Medio: 21-50%, Alto: 51-75%, Crítico: 76-100%
        """
        for record in self:
            score = record.risk_score
            
            if score <= 15:
                record.risk_level = 'low'
            elif score <= 36:
                record.risk_level = 'medium'
            elif score <= 59:
                record.risk_level = 'high'
            else:  
                record.risk_level = 'critical'

    @api.depends('risk_score')
    def _compute_inherent_risk_level(self):
        """
        Calcula el nivel de riesgo inherente (mismo cálculo que risk_level por ahora)
        """
        for record in self:
            score = record.risk_score
            
            if score <= 15:
                record.inherent_risk_level = 'low'
            elif score <= 36:
                record.inherent_risk_level = 'medium'
            elif score <= 59:
                record.inherent_risk_level = 'high'
            else:  
                record.inherent_risk_level = 'critical'

    @api.depends('risk_level')
    def _compute_priority(self):
        """
        Calcula la prioridad basada en el nivel de riesgo
        """
        for record in self:
            if record.risk_level == 'low':
                record.priority = 'low'
            elif record.risk_level == 'medium':
                record.priority = 'low'
            elif record.risk_level == 'high':
                record.priority = 'medium'
            elif record.risk_level == 'critical':
                record.priority = 'critical'
            else:
                record.priority = 'medium'
    
    def _compute_color(self):
        """
        Asigna colores para la vista Kanban según el nivel de riesgo
        """
        for record in self:
            color_map = {
                'low': 10,      # Verde
                'medium': 3,   # Amarillo
                'high': 2,     # Anaranjado
                'critical': 1  # Rojo
            }
            record.color = color_map.get(record.risk_level, 0)

    def _compute_evaluation_plan_count(self):
                """
                Calcula la cantidad de planes de evaluación asociados a cada riesgo
                """
                for risk in self:
                    risk.evaluation_plan_count = self.env['evaluation.plan'].search_count([
                        ('risk_id', '=', risk.id)
                    ])

    def action_view_evaluation_plans(self):
        """
        Acción para ver los planes de evaluación asociados a este riesgo
        """
        return {
            'type': 'ir.actions.act_window',
            'name': f'Planes de Evaluación - {self.title}',
            'res_model': 'evaluation.plan',
            'view_mode': 'kanban,tree,form',
            'domain': [('risk_id', '=', self.id)],
            'context': {'default_risk_id': self.id},
            'target': 'current',
        }
    



    
    
    # Métodos de acción para cambiar etapas
    def action_evaluate(self):
        """Cambia el riesgo a etapa 'Evaluado'"""
        self.ensure_one()
        if self.stage == 'draft':
            self.stage = 'evaluated'
            self.message_post(body="Riesgo evaluado y clasificado")
        else:
            raise ValidationError("Solo se pueden evaluar riesgos en estado 'Borrador'")
    
    def action_start_treatment(self):
        """Cambia el riesgo a etapa 'En Tratamiento'"""
        self.ensure_one()
        if self.stage == 'evaluated':
            self.stage = 'treatment'
            self.message_post(body="Iniciado el tratamiento del riesgo")
        else:
            raise ValidationError("Solo se pueden tratar riesgos 'Evaluados'")
    
    def action_close(self):
        """Cierra el riesgo"""
        self.ensure_one()
        if self.stage in ['evaluated', 'treatment']:
            self.stage = 'closed'
            self.message_post(body="Riesgo cerrado exitosamente")
        else:
            raise ValidationError("Solo se pueden cerrar riesgos 'Evaluados' o 'En Tratamiento'")
    
    def action_cancel(self):
        """Cancela el riesgo"""
        self.ensure_one()
        if self.stage != 'closed':
            self.stage = 'cancelled'
            self.message_post(body="Riesgo cancelado")
        else:
            raise ValidationError("No se pueden cancelar riesgos cerrados")
    
    def action_reset_to_draft(self):
        """Regresa el riesgo a borrador"""
        self.ensure_one()
        if self.stage != 'closed':
            self.stage = 'draft'
            self.message_post(body="Riesgo regresado a borrador para revisión")
    
    @api.constrains('identification_date')
    def _check_identification_date(self):
        """Valida que la fecha de identificación no sea futura"""
        for record in self:
            if record.identification_date > fields.Date.context_today(self):
                raise ValidationError("La fecha de identificación no puede ser futura")
    
    def name_get(self):
        """Personaliza la representación del nombre del registro"""
        result = []
        for record in self:
            name = f'{record.request_number} - {record.title}'
            result.append((record.id, name))
        return result
    
    def action_print_risk_report(self):
        """
        Acción para generar reporte PDF del riesgo
        """
        return self.env.ref('sgr.action_report_risk_management').report_action(self)
    
    @api.model
    def get_risk_statistics(self):
        """
        Método para obtener estadísticas de riesgos para dashboards
        Retorna un diccionario con métricas clave
        """
        total_risks = self.search_count([])
        high_risks = self.search_count([('risk_level', '=', 'high')])
        active_risks = self.search_count([('stage', 'in', ['draft', 'evaluated', 'treatment'])])
        closed_risks = self.search_count([('stage', '=', 'closed')])
        
        # Estadísticas por categoría
        categories = self.env['risk.category'].search([('active', '=', True)])
        category_stats = []
        for category in categories:
            count = self.search_count([('category_id', '=', category.id)])
            category_stats.append({
                'name': category.name,
                'count': count,
                'percentage': round((count / total_risks * 100) if total_risks > 0 else 0, 1)
            })
        
        return {
            'total_risks': total_risks,
            'high_risks': high_risks,
            'active_risks': active_risks,
            'closed_risks': closed_risks,
            'high_risk_percentage': round((high_risks / total_risks * 100) if total_risks > 0 else 0, 1),
            'closure_rate': round((closed_risks / total_risks * 100) if total_risks > 0 else 0, 1),
            'category_stats': category_stats
        }
    
    def get_risk_matrix_data(self):
        """
        Genera datos para matriz de riesgos (probabilidad vs impacto)
        """
        risks = self.search([('stage', '!=', 'cancelled')])
        matrix_data = []
        
        for risk in risks:
            if risk.probability and risk.impact:
                matrix_data.append({
                    'id': risk.id,
                    'name': risk.title,
                    'number': risk.request_number,
                    'probability': int(risk.probability),
                    'impact': int(risk.impact),
                    'score': risk.risk_score,
                    'level': risk.risk_level,
                    'category': risk.category_id.name,
                    'stage': risk.stage
                })
        
        return matrix_data