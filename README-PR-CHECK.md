# Workflow: PR Check - Build, Test & Analyze

## Descripción General

Este workflow automatiza el proceso de validación de calidad de código cuando se crea un Pull Request hacia la rama `develop`. Garantiza que el código cumple con los estándares de calidad antes de ser integrado al código base.

## Propósito

Validar automáticamente cada Pull Request mediante:
- **Build**: Construcción y validación de dependencias
- **Unit Tests**: Pruebas unitarias con base de datos real
- **Static Code Analysis**: Análisis estático del código con Flake8
- **Code Coverage**: Medición de cobertura de pruebas

## ¿Cuándo se Ejecuta?

El workflow se activa automáticamente cuando:
- Se crea un Pull Request hacia la rama `develop`
- Se actualiza un Pull Request existente hacia `develop`

```yaml
on:
  pull_request:
    branches: [develop]
```

---

## Componentes del Workflow

### **Build - Instalación de Dependencias**

**¿Qué hace?**
- Configura el entorno Python 3.11
- Instala todas las dependencias del proyecto desde `requirements.txt`
- Instala herramientas adicionales para análisis: `flake8` y `coverage`

**¿Por qué es importante?**
Garantiza que todas las librerías necesarias estén disponibles y que el código pueda ejecutarse correctamente. El sistema de caché acelera las ejecuciones futuras almacenando las dependencias ya descargadas.

**Tecnologías utilizadas:**
- Python 3.11
- pip (gestor de paquetes)
- GitHub Actions Cache (para optimización)

---

### **Static Code Analysis - Análisis Estático con Flake8**

**¿Qué hace?**
Analiza el código Python sin ejecutarlo para detectar:
- **Errores críticos de sintaxis**: Variables no definidas, imports incorrectos, errores de indentación
- **Problemas de calidad**: Complejidad ciclomática alta, líneas muy largas (>120 caracteres)
- **Malas prácticas**: Código no utilizado, imports redundantes

**Reglas configuradas:**
```python
# Verificación crítica (obligatoria)
--select=E9,F63,F7,F82  # Errores de sintaxis y semánticos graves

# Verificación extendida (advertencias)
--max-complexity=10      # Complejidad ciclomática máxima
--max-line-length=120    # Longitud máxima de línea
```

**¿Por qué es importante?**
Detecta problemas potenciales antes de que el código se ejecute, mejora la legibilidad y mantiene un estándar consistente en todo el equipo.

**Exclusiones:**
Se ignoran automáticamente:
- Entornos virtuales (`.venv`, `venv`)
- Archivos compilados (`__pycache__`, `*.pyc`)
- Migraciones de Django (`migrations/`)
- Configuraciones de build (`build/`, `dist/`, `*.egg-info`)

---

### **Unit Tests - Pruebas Unitarias**

**¿Qué hace?**
Ejecuta todas las pruebas unitarias del módulo `api` contra una base de datos PostgreSQL real en Azure:

```bash
coverage run --source='.' manage.py test api
```

**Configuración de Base de Datos:**
- **Motor**: PostgreSQL en Azure
- **Host**: aksdb.postgres.database.azure.com
- **Base de datos de pruebas**: `devsudb_test` (aislada del ambiente productivo)
- **Autenticación**: Credenciales almacenadas en GitHub Secrets

**Pasos previos:**
1. Ejecuta las migraciones de Django para crear las tablas necesarias
2. Prepara el esquema de base de datos en el ambiente de pruebas

**¿Por qué usar una base de datos real?**
- Valida que las queries y modelos funcionen correctamente con PostgreSQL
- Detecta problemas específicos del motor de base de datos
- Asegura compatibilidad con el ambiente productivo
- Prueba las migraciones de forma realista

**¿Por qué es importante?**
Las pruebas unitarias garantizan que:
- Las funcionalidades existentes no se rompan con nuevos cambios (regresiones)
- El código nuevo cumple con los requisitos esperados
- Las integraciones con la base de datos funcionan correctamente

---

###  **Code Coverage - Cobertura de Código**

**¿Qué hace?**
Mide qué porcentaje del código fue ejecutado durante las pruebas utilizando la herramienta `coverage`:

```bash
coverage report -m    # Reporte en consola con líneas no cubiertas
coverage xml          # Reporte XML para análisis posterior
```

**Métricas generadas:**
- **Cobertura por archivo**: Porcentaje de líneas ejecutadas en cada archivo
- **Líneas faltantes**: Identifica qué líneas de código NO fueron probadas
- **Reporte XML**: Formato estándar para herramientas de análisis

**Exclusiones inteligentes:**
```python
--omit="*/migrations/*,*/tests.py"
```
Se excluyen de la medición:
- Migraciones de Django (código generado automáticamente)
- Archivos de pruebas (no tiene sentido probar las pruebas)

**¿Por qué es importante?**
- **Identifica código sin probar**: Áreas del código que podrían contener bugs no detectados
- **Mejora la calidad**: Incentiva a escribir más pruebas
- **Visibilidad**: Permite tomar decisiones informadas sobre dónde enfocar esfuerzos de testing
- **Tendencia**: Monitorea si la cobertura mejora o empeora con el tiempo

**Almacenamiento:**
El reporte XML se guarda como artifact en GitHub Actions durante 30 días, permitiendo:
- Descargar y analizar el reporte detallado
- Integración con herramientas de análisis de cobertura
- Auditorías y revisiones posteriores

---

## Reportes y Feedback

### Comentario Automático en el PR

El workflow genera automáticamente un comentario en el Pull Request con un resumen de resultados:

```markdown
## CI/CD Pipeline Results

| Step            | Status        |
|-----------------|---------------|
| Build           | ✅ Passed     |
| Code Analysis   | ✅ Passed     |
| Migrations      | ✅ Passed     |
| Tests           | ✅ Passed     |
| Coverage        | Generated     |

**Coverage report:** Check artifacts for detailed coverage.xml
```

**Este comentario se actualiza automáticamente** cada vez que se hace un nuevo push al PR, evitando spam de comentarios duplicados.

### GitHub Summary

Se genera un resumen visual en la interfaz de GitHub Actions con:
- Estado detallado de cada paso
- Indicadores claros de éxito/fallo
- Mensaje final de validación

---

## Criterios de Aprobación

El PR puede ser aprobado si:
- Build exitoso (todas las dependencias instaladas)
- Code Analysis sin errores críticos (warnings permitidos)
- Migraciones aplicadas exitosamente
- Todas las pruebas unitarias pasan
- Reporte de cobertura generado

---

## Seguridad

### Secretos Utilizados

Almacenados en **GitHub Secrets** (Settings → Secrets and variables → Actions):

| Secret         | Descripción                               |
|----------------|-------------------------------------------|
| `DB_USER`      | Usuario de PostgreSQL en Azure            |
| `DB_PASSWORD`  | Contraseña de PostgreSQL en Azure         |

**Protección:**
- Los secretos nunca se exponen en los logs
- Solo accesibles durante la ejecución del workflow
- Encriptados en reposo por GitHub

---

## Tecnologías y Herramientas

| Herramienta | Versión | Propósito |
|-------------|---------|-----------|
| Python | 3.11 | Lenguaje de programación |
| Django | Latest | Framework web |
| Flake8 | Latest | Análisis estático de código |
| Coverage.py | Latest | Medición de cobertura |
| PostgreSQL | Azure | Base de datos de pruebas |
| GitHub Actions | v4/v5 | Orquestación del pipeline |

---

## Beneficios

1. **Calidad Automatizada**: Validación consistente sin intervención manual
2. **Detección Temprana**: Problemas identificados antes del merge
3. **Feedback Rápido**: Resultados en minutos después del push
4. **Estándares Consistentes**: Mismo nivel de calidad para todos los PRs
5. **Documentación**: Historial completo de validaciones
6. **Productividad**: Desarrolladores pueden enfocarse en codificar, no en validar manualmente

---

## Flujo Completo

```
1. Developer crea PR → develop
          ↓
2. Workflow se activa automáticamente
          ↓
3. Checkout del código
          ↓
4. Configuración de Python 3.11
          ↓
5. Instalación de dependencias (con caché)
          ↓
6. Análisis estático con Flake8
          ↓
7. Migraciones en base de datos de pruebas
          ↓
8. Ejecución de tests unitarios con coverage
          ↓
9. Generación de reporte XML
          ↓
10. Comentario automático en el PR
          ↓
11.  PR listo para revisión
```

---