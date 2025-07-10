# -*- coding: utf-8 -*-
{
    'name': 'Gestión de Riesgos',
    'version': '17.0.1.0.0',
    'category': 'Risk Management',
    'summary': 'Sistema de gestión de riesgos empresariales',
    'description': """
        Sistema de Gestión de Riesgos Empresariales
        ==========================================
        
        Este módulo proporciona un sistema completo para la gestión de riesgos empresariales que incluye:
        
        Características principales:
        * Identificación y categorización de riesgos
        * Evaluación y análisis de riesgos
        * Matriz de riesgos visual 5x5
        * Planes de evaluación y seguimiento
        * Reportes dinámicos personalizables
        * Dashboard de monitoreo en tiempo real
        * Gestión de medidas de control
        
        Funcionalidades:
        * Registro de riesgos con múltiples criterios
        * Evaluación de probabilidad e impacto
        * Clasificación automática de riesgos
        * Seguimiento de estados y responsables
        * Generación de reportes ejecutivos dinámicos
        * Wizard de reportes con filtros avanzados
        * Integración con sistema de usuarios y permisos
        * Tipos de gestión: ISMS, COMP, ORM
        
        Reportes incluidos:
        * Reporte individual de riesgo
        * Reporte dinámico con filtros personalizables
        * Matriz visual de riesgos
        * Estadísticas y análisis ejecutivo
    """,
    
    'author': 'Axeel Cerrato',
    'depends': ['base', 'mail', 'hr'],
    'images': ['/sgr/static/description/icon.png'],
    
    'assets': {
        'web.assets_backend': [
            'sgr/static/src/css/risk_matrix.css',
        ],
    },
    
    'data': [
        # =============================
        # 1. SEGURIDAD (Primero siempre)
        # =============================
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        
        # =============================
        # 2. DATOS BASE
        # =============================
        'data/risk_sequence.xml',
        'data/demo_data.xml',
        'data/email_templates.xml',
        
        
        # =============================
        # 3. VISTAS DE MODELOS
        # =============================
        'views/risk_category_views.xml',
        'views/risk_management_views.xml',
        'views/evaluation_plan_views.xml',
        'views/dashboard_views.xml',
        
        # =============================
        # 4. VISTAS DE WIZARDS
        # =============================
        'views/risk_report_wizard_views.xml',
        
        # =============================
        # 5. REPORTES PDF
        # =============================
        'reports/risk_report_action.xml',
        'reports/risk_report_template.xml',
        'reports/risk_report_dynamic_action.xml',
        'reports/risk_report_dynamic_template.xml',
        
        # 6. EMAIL CRON (DESPUÉS DE LAS VISTAS)
        'data/email_cron.xml',  # <-- MOVER AQUÍ
        
        # =============================
        # 7. MENÚS (Siempre al final)
        # =============================
        'views/risk_menu.xml',
    ],
    
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'auto_install': False,
    
    # Información adicional
    'website': '',
    'support': '',
    
    # Para desarrollo
    'development_status': 'Production/Stable',
    'maintainers': ['Axeel Cerrato'],
}