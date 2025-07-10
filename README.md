# 🛡️ SGR - Sistema de Gestión de Riesgos

**Autor:** Axeel Cerrato  
**Versión:** 17.0.1.0.0  
**Compatibilidad:** Odoo 17  
**Licencia:** LGPL-3

## 📋 Descripción

Sistema integral de gestión de riesgos empresariales desarrollado para Odoo 17, diseñado para identificar, evaluar, monitorear y mitigar riesgos organizacionales de manera sistemática y eficiente.

## ✨ Características Principales

### 🎯 **Gestión Integral de Riesgos**
- **Tipos de Gestión**: ISMS (Seguridad de la Información), COMP (Cumplimiento Normativo), ORM (Riesgos Operacionales)
- **Matriz de Riesgo 5x5**: Evaluación visual de probabilidad vs impacto
- **Numeración automática**: Códigos únicos por tipo (ISMS-0001, COMP-0001, ORM-0001)
- **Análisis de Riesgo Inherente y Residual**

### 📊 **Dashboard Inteligente**
- **Estadísticas en tiempo real**: Total de riesgos, críticos, altos y planes de acción
- **Matriz visual interactiva**: Distribución de riesgos por nivel de criticidad
- **Indicadores KPI**: Métricas clave para toma de decisiones

### 📋 **Planes de Evaluación**
- **Workflow tipo CRM**: Etapas (Por hacer, En progreso, Completada)
- **Sistema de tareas**: Seguimiento detallado con progreso
- **Asignación de responsables**: Control de empleados y fechas
- **Notificaciones automáticas**: Alertas de vencimiento

### 🏷️ **Categorización Avanzada**
- **Categorías personalizables**: Códigos auto-incrementales (CAT-0001)
- **Estados activo/inactivo**: Control de visibilidad
- **Contadores automáticos**: Cantidad de riesgos por categoría

## 🔧 Instalación

### Prerrequisitos
- Odoo 17.0+
- Python 3.8+
- Módulos dependientes: `base`, `mail`, `hr`

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd sgr
   ```

2. **Copiar al directorio de addons de Odoo**
   ```bash
   cp -r sgr /path/to/odoo/addons/
   ```

3. **Actualizar lista de módulos**
   - Ir a Aplicaciones → Actualizar lista de aplicaciones

4. **Instalar el módulo**
   - Buscar "Gestión de Riesgos"
   - Hacer clic en "Instalar"

## 🚀 Configuración Inicial

### 1. **Configurar Grupos de Usuario**
```
Configuración → Usuarios y Compañías → Usuarios
```
- **Usuario de Riesgos**: Permisos básicos (crear/editar propios registros)
- **Gestor de Riesgos**: Permisos completos (administrador del sistema)

### 2. **Crear Categorías de Riesgo**
```
Gestión de Riesgos → Configuración → Categorías de Riesgo
```
Ejemplos sugeridos:
- Financiero
- Operacional  
- Estratégico
- Cumplimiento
- Tecnológico

### 3. **Configurar Departamentos**
```
Empleados → Configuración → Departamentos
```
Asegurar que los departamentos están creados para asignación de riesgos.

## 📖 Guía de Uso

### 🎯 **Registrar un Nuevo Riesgo**

1. **Navegar al módulo**
   ```
   Gestión de Riesgos → Riesgos → Todos los Riesgos
   ```

2. **Crear nuevo registro**
   - Seleccionar **Tipo de Gestión** (ISMS/COMP/ORM)
   - El código se genera automáticamente
   - Completar información básica y evaluación

3. **Evaluación de Riesgo**
   - **Probabilidad**: Improbable (20%) a Frecuente (100%)
   - **Impacto**: Insignificante (20%) a Catastrófico (100%)
   - El sistema calcula automáticamente el nivel de riesgo

### 📋 **Crear Plan de Evaluación**

1. **Desde un riesgo existente**
   - Botón "Planes" en la vista del riesgo
   - Crear nuevo plan de evaluación

2. **Configurar el plan**
   - Asignar responsable
   - Establecer fechas
   - Crear tareas específicas

3. **Seguimiento Kanban**
   - Vista tipo CRM para gestión visual
   - Arrastrar y soltar entre etapas

### 📊 **Usar el Dashboard**

```
Gestión de Riesgos → Dashboard
```

- **Métricas clave**: Visualización de estadísticas
- **Matriz interactiva**: Distribución de riesgos
- **Análisis visual**: Identificación de patrones

## 🏗️ Arquitectura Técnica

### 📁 **Estructura del Módulo**
```
sgr/
├── models/                 # Modelos de datos
│   ├── risk_management.py    # Modelo principal
│   ├── risk_category.py      # Categorías
│   ├── evaluation_plan.py    # Planes de evaluación
│   ├── evaluation_plan_task.py # Tareas
│   └── dashboard.py          # Dashboard
├── views/                  # Interfaces de usuario
├── security/              # Control de acceso
├── data/                  # Datos iniciales
├── reports/               # Reportes PDF
└── static/                # Recursos estáticos
```

### 🔗 **Relaciones entre Modelos**
- **risk.management** → **evaluation.plan** (One2many)
- **evaluation.plan** → **evaluation.plan.task** (One2many)
- **risk.management** → **risk.category** (Many2one)
- **risk.management** → **hr.employee** (Many2one)

### 🔒 **Seguridad Implementada**
- **Grupos de usuario** con permisos diferenciados
- **Reglas de registro** (usuarios ven solo sus registros)
- **Control de acceso** por modelo y operación
- **Validaciones de integridad** en todos los modelos

## 🐳 Docker Support

### Dockerfile
```dockerfile
FROM odoo:17.0
COPY ./sgr /mnt/extra-addons/sgr
USER root
RUN pip install -r /mnt/extra-addons/sgr/requirements.txt
USER odoo
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  web:
    image: odoo:17.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - ./sgr:/mnt/extra-addons/sgr
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Tests unitarios
python -m pytest tests/

# Tests de integración
odoo-bin -d test_db -i sgr --test-enable --stop-after-init
```

### Tests Incluidos
- ✅ Validación de campos requeridos
- ✅ Cálculo automático de puntuaciones de riesgo
- ✅ Reglas de seguridad
- ✅ Workflows de planes de evaluación

## 📈 Mejores Prácticas Implementadas

### 🔧 **Código**
- **Documentación completa** en todos los métodos
- **Validaciones robustas** con `@api.constrains`
- **Manejo de errores** con try/except
- **Logging sistemático** para debugging
- **Campos calculados** con `store=True` para performance

### 🎨 **UI/UX**
- **Vistas Kanban interactivas** tipo CRM
- **Dashboard con métricas en tiempo real**
- **Matriz visual de riesgos** HTML responsiva
- **Filtros y búsquedas avanzadas**
- **Alertas y notificaciones** contextuales

### 🔒 **Seguridad**
- **Principio de menor privilegio**
- **Validación de inputs** en frontend y backend
- **Reglas de acceso granulares**
- **Auditoría de cambios** con chatter

## 🤝 Contribución

1. Fork el proyecto
2. Crear branch para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📞 Soporte

**Desarrollador:** Axeel Cerrato  
**Email:** [tu-email@dominio.com]  
**LinkedIn:** [tu-perfil-linkedin]

## 📄 Licencia

Este proyecto está bajo la Licencia LGPL-2.1. Ver el archivo `LICENSE` para más detalles.

---

**Desarrollado con ❤️ para la gestión eficiente de riesgos empresariales**