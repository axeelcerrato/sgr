from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RiskCategory(models.Model):
    """
    Modelo para categorías de riesgo
    Permite clasificar los riesgos en diferentes categorías para mejor organización
    """
    _name = 'risk.category'
    _description = 'Categorías de Riesgo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'code, name'
    
    # Campo para el nombre de la categoría
    name = fields.Char(
        string='Nombre de Categoría',
        required=True,
        tracking=True,
        help='Nombre descriptivo de la categoría de riesgo'
    )
    
    # Campo para código auto-incremental
    code = fields.Char(
        string='Código',
        readonly=True,
        copy=False,
        help='Código único auto-generado para la categoría'
    )
    
    # Campo para el estado activo/inactivo
    active = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True,
        help='Si está desmarcado, la categoría estará inactiva y no aparecerá en las listas'
    )
    
    # Campo para mostrar el estado de forma visual
    state = fields.Selection([
        ('active', 'Activo'),
        ('inactive', 'Inactivo')
    ], string='Estado', compute='_compute_state', store=True)
    
    # Relación con riesgos asociados (campo simple sin búsquedas complejas)
    risk_count = fields.Integer(
        string='Cantidad de Riesgos',
        compute='_compute_risk_count',
        help='Número de riesgos asociados a esta categoría'
    )
    
    @api.depends('active')
    def _compute_state(self):
        """
        Calcula el estado basado en el campo active
        """
        for record in self:
            record.state = 'active' if record.active else 'inactive'
    
    @api.model
    def create(self, vals):
        """
        Genera código auto-incremental al crear una nueva categoría
        """
        if not vals.get('code'):
            # Buscar el último código creado
            last_category = self.search([], order='code desc', limit=1)
            if last_category and last_category.code:
                try:
                    # Extraer número del último código
                    last_number = int(last_category.code.replace('CAT-', ''))
                    next_number = last_number + 1
                except ValueError:
                    next_number = 1
            else:
                next_number = 1
            
            # Generar nuevo código con formato CAT-XXXX
            vals['code'] = f'CAT-{next_number:04d}'
        
        return super(RiskCategory, self).create(vals)
    
    def _compute_risk_count(self):
        """
        Calcula la cantidad de riesgos asociados a cada categoría
        """
        for category in self:
            category.risk_count = self.env['risk.management'].search_count([
                ('category_id', '=', category.id)
            ])
    
    def action_view_risks(self):
        """
        Acción para ver los riesgos asociados a esta categoría
        """
        return {
            'type': 'ir.actions.act_window',
            'name': f'Riesgos - {self.name}',
            'res_model': 'risk.management',
            'view_mode': 'tree,form',
            'domain': [('category_id', '=', self.id)],
            'context': {'default_category_id': self.id},
        }
    
    def toggle_active(self):
        """
        Método para alternar el estado activo/inactivo
        """
        for record in self:
            record.active = not record.active
    
    @api.constrains('name')
    def _check_name_unique(self):
        """
        Validación para asegurar que el nombre de la categoría sea único entre categorías activas
        """
        for record in self:
            if record.active:
                existing = self.search([
                    ('name', '=', record.name),
                    ('active', '=', True),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(f'Ya existe una categoría activa con el nombre "{record.name}"')
    
    def name_get(self):
        """
        Personaliza la representación del nombre del registro
        """
        result = []
        for record in self:
            name = f'[{record.code}] {record.name}' if record.code else record.name
            result.append((record.id, name))
        return result