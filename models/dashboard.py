from odoo import models, fields, api


class RiskDashboard(models.Model):
    """
    Modelo para el Dashboard de Riesgos
    """
    _name = 'risk.dashboard'
    _description = 'Dashboard de Gestión de Riesgos'
    _rec_name = 'name'
    
    name = fields.Char(string='Nombre', default='Dashboard de Riesgos', readonly=True)
    
    # Campos para estadísticas
    total_risks = fields.Integer(
        string='Total de Riesgos',
        compute='_compute_dashboard_data'
    )

    critical_risks = fields.Integer(
        string='Riesgos Críticos',
        compute='_compute_dashboard_data'
    )
    
    high_risks = fields.Integer(
        string='Riesgos Altos',
        compute='_compute_dashboard_data'
    )

    total_plans = fields.Integer(
        string='Total de Planes',
        compute='_compute_dashboard_data'
    )

    dashboard_matrix = fields.Html(
        string='Matriz Dashboard',
        compute='_compute_dashboard_matrix'
    )

    @api.depends()
    def _compute_dashboard_data(self):
        """
        Calcula los datos para el dashboard
        """
        for record in self:
            record.total_risks = self.env['risk.management'].search_count([])
            record.critical_risks = self.env['risk.management'].search_count([('risk_level', '=', 'critical')])
            record.high_risks = self.env['risk.management'].search_count([('risk_level', '=', 'high')])
            record.total_plans = self.env['evaluation.plan'].search_count([])

    @api.depends()
    def _compute_dashboard_matrix(self):
        """
        Genera la matriz de riesgo para el dashboard con contadores
        """
        for record in self:
            # Obtener todos los riesgos
            risks = self.env['risk.management'].search([])
            total_plans = record.total_plans
            
            # Crear contadores por posición en la matriz
            matrix_counts = {}
            for risk in risks:
                if risk.impact and risk.probability:
                    key = f"{risk.impact}_{risk.probability}"
                    if key not in matrix_counts:
                        matrix_counts[key] = 0
                    matrix_counts[key] += 1
            
            # Valores para la matriz
            valores_impacto = ['20', '40', '60', '80', '100']
            valores_probabilidad = ['100', '80', '60', '40', '20']  # Orden inverso
            labels_impacto = ['Insignificante', 'Menor', 'Moderado', 'Mayor', 'Catastrófico']
            labels_probabilidad = ['Frecuente', 'Probable', 'Ocasional', 'Posible', 'Improbable']
            
            html = f'''
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 30px;">
                <!-- Estadísticas a la derecha -->
                <div style="min-width: 200px;">
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6;">
                        <h4 style="margin: 0 0 15px 0; color: #495057; font-size: 18px;">
                            Gestión de riesgos operativos
                        </h4>
                        <div style="margin-bottom: 10px;">
                            <span style="font-size: 24px; font-weight: bold; color: #007bff;">
                                {len(risks)}
                            </span>
                            <span style="color: #6c757d; margin-left: 5px;">Riesgos</span>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <span style="font-size: 24px; font-weight: bold; color: #28a745;">
                                {total_plans}
                            </span>
                            <span style="color: #6c757d; margin-left: 5px;">Planes de acción</span>
                        </div>
                    </div>
                </div>
                
                <!-- Matriz a la izquierda -->
                <div style="flex: 1;">
                    <div style="display: grid; grid-template-columns: 100px repeat(5, 80px); grid-template-rows: 40px repeat(5, 80px); gap: 2px; padding: 10px; background: white; border-radius: 8px;">
                        <!-- Celda vacía esquina -->
                        <div style="display: flex; align-items: center; justify-content: center;"></div>
            '''
            
            # Headers de impacto
            for i, label in enumerate(labels_impacto):
                html += f'''
                <div style="display: flex; align-items: center; justify-content: center; background: #e9ecef; 
                           font-weight: bold; font-size: 12px; text-align: center; padding: 5px; 
                           border-radius: 4px; border: 1px solid #dee2e6;">
                    {label}
                </div>
                '''
            
            # Filas de la matriz
            for i, prob_val in enumerate(valores_probabilidad):
                # Label de probabilidad
                html += f'''
                <div style="display: flex; align-items: center; justify-content: center; background: #e9ecef; 
                           font-weight: bold; font-size: 12px; text-align: center; padding: 5px; 
                           border-radius: 4px; border: 1px solid #dee2e6;">
                    {labels_probabilidad[i]}
                </div>
                '''
                
                # Celdas de riesgo
                for imp_val in valores_impacto:
                    riesgo_val = (int(imp_val) / 100) * (int(prob_val) / 100) * 100
                    
                    # Contar riesgos en esta celda
                    count = matrix_counts.get(f"{imp_val}_{prob_val}", 0)
                    
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
                    
                    # Mostrar número si hay riesgos en esta celda
                    display_text = str(count) if count > 0 else ''
                    
                    html += f'''
                    <div style="display: flex; align-items: center; justify-content: center; 
                               background: {color}; color: white; font-size: 18px; font-weight: bold; 
                               border-radius: 6px; border: 2px solid #fff; min-height: 70px; 
                               box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                         title="Impacto: {imp_val}% - Probabilidad: {prob_val}% - Nivel: {nivel} - Riesgos: {count}">
                        {display_text}
                    </div>
                    '''
            
            html += '''
                    </div>
                </div>
            </div>
            '''
            
            record.dashboard_matrix = html

  