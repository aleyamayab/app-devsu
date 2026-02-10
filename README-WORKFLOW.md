# Documentación de Workflows CI/CD

## Índice de Documentación

### [PR Check - Build, Test & Analyze](README-PR-CHECK.md)
Workflow de validación de calidad que se ejecuta en cada Pull Request hacia `develop`.

**Incluye:**
- Unit Tests (Pruebas Unitarias)
- Static Code Analysis (Análisis Estático con Flake8)
- Code Coverage (Cobertura de Código)
- Database Migration Testing

**Cuándo se ejecuta:** Al crear o actualizar PRs hacia `develop`

**Archivo:** [pr-check.yml](pr-check.yml)

---

### [CI Build & Deployment](README-CI-CD.md)
Workflow de integración y despliegue continuo con versionamiento semántico y GitOps.

**Incluye:**
- Build Validation
- Semantic Versioning (Versionamiento Automático)
- Docker Build & Push a GHCR
- GitOps - Actualización de manifiestos K8s
- Despliegue automático con ArgoCD

**Cuándo se ejecuta:** Al fusionar código en la rama `develop`

**Archivo:** [ci-cd.yml](ci-cd.yml)

---

## Flujo Completo de Desarrollo

```
1. Developer crea feature branch
          ↓
2. Developer hace commits con formato convencional:
   feat:, fix:, etc.
          ↓
3. Developer abre PR → develop
          ↓
4. WORKFLOW PR CHECK se ejecuta automáticamente
   - Build
   - Unit Tests
   - Static Code Analysis
   - Code Coverage
          ↓
5. Code Review + Aprobación
          ↓
6. Merge a develop
         ↓
7.  WORKFLOW CI/CD se ejecuta automáticamente
   - Semantic Release genera versión
   - Build & Push de imagen Docker
   - Actualización de manifiestos K8s (GitOps)
          ↓
8. ArgoCD detecta cambio y despliega
         ↓
9.  Nueva versión corriendo en DEV
```

---

## Convenciones de Commit (Conventional Commits)

Para que el versionamiento semántico funcione correctamente, los commits DEBEN seguir este formato:

### Formato Básico
```
<tipo>(<scope>): <descripción>

[cuerpo opcional]
```

### Tipos y su Impacto en Versiones

| Tipo | Versión | Descripción | Ejemplo |
|------|---------|-------------|---------|
| `feat:` | MINOR | Nueva funcionalidad | `feat: agregar endpoint de reportes` |
| `fix:` | PATCH | Corrección de bugs | `fix: resolver error en login` |
| `perf:` | PATCH | Mejoras de rendimiento | `perf: optimizar query de búsqueda` |
| `refactor:` | PATCH | Refactorización | `refactor: simplificar validación` |
| `feat!:` o `BREAKING CHANGE:` | MAJOR | Cambio incompatible | `feat!: cambiar API de autenticación` |
| `docs:` | - | Documentación (sin release) | `docs: actualizar README` |
| `test:` | - | Pruebas (sin release) | `test: agregar tests unitarios` |
| `chore:` | - | Mantenimiento (sin release) | `chore: actualizar dependencias` |

### Ejemplos Correctos 

```bash
feat(api): agregar endpoint de estadísticas
fix(auth): corregir validación de tokens
perf(db): optimizar consulta de reportes con índice
docs(readme): agregar guía de instalación
test(models): aumentar cobertura del modelo User
chore(deps): actualizar Django a 5.0
```

---

## Versiones por Ambiente

| Rama | Ambiente | Formato de Versión | Ejemplo |
|------|----------|-------------------|---------|
| `develop` | DEV | X.Y.Z-beta.N | `1.5.0-beta.1` |
| `qa` | QA | X.Y.Z-rc.N | `1.5.0-rc.1` |
| `main` | PROD | X.Y.Z | `1.5.0` |

---

##  Stack Tecnológico

| Componente | Herramienta | Propósito |
|------------|-------------|-----------|
| **CI/CD** | GitHub Actions | Orquestación de pipelines |
| **Versionamiento** | Semantic Release | Generación automática de versiones |
| **Testing** | pytest + coverage | Pruebas unitarias y cobertura |
| **Code Quality** | Flake8 | Análisis estático de código Python |
| **Containerización** | Docker | Empaquetado de aplicación |
| **Registry** | GHCR | Almacenamiento de imágenes Docker |
| **GitOps** | Git (rama manifiesto-k8s) | Control de versiones de infra |
| **CD** | ArgoCD | Despliegue continuo a Kubernetes |
| **Orquestación** | Kubernetes | Ejecución de containers |

---

#📊 Arquitectura de CI/CD

```
┌─────────────────────────────────────────────────────────────┐
│                       REPOSITORY                            │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   develop    │    │      qa      │    │     main     │ │
│  │   (DEV)      │    │     (QA)     │    │    (PROD)    │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                    │                   │         │
│         ├──────────┐         ├────────┐          │         │
│    PR Check    CI/CD    PR Check   CI/CD    PR Check  CI/CD│
│                                                             │
└─────────────────────────────────────────────────────────────┘
                                │
                                ↓
┌─────────────────────────────────────────────────────────────┐
│              GITHUB CONTAINER REGISTRY (GHCR)               │
│                                                             │
│  ghcr.io/aleyamayab/devsu-demo-devops-python             │
│     ├── 1.5.0-beta.1                                        │
│     ├── 1.5.0-beta.2                                        │
│     └── 1.5.0                                               │
└─────────────────────────────────────────────────────────────┘
                                │
                                ↓
┌─────────────────────────────────────────────────────────────┐
│                    GITOPS REPOSITORY                        │
│               (Rama: manifiesto-k8s)                        │
│                                                             │
│  k8s/                                                       │
│   ├── dev/deployment.yml      (1.5.0-beta.1)                │
│   ├── qa/deployment.yml       (1.5.0-rc.1)                  │
│   └── prod/deployment.yml     (1.4.0)                       │
└─────────────────────────────────────────────────────────────┘
                                │
                                ↓
┌─────────────────────────────────────────────────────────────┐
│                         ARGOCD                              │
│                  (Continuous Deployment)                    │
│                                                             │
│  Monitorea: manifiesto-k8s branch                           │
│  Sincroniza: Kubernetes clusters                            │
└─────────────────────────────────────────────────────────────┘
                                │
                                ↓
┌─────────────────────────────────────────────────────────────┐
│                   KUBERNETES CLUSTERS                       │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │   DEV    │    │    QA    │    │   PROD   │             │
│  │ Namespace│    │ Namespace│    │ Namespace│             │
│  └──────────┘    └──────────┘    └──────────┘             │
└─────────────────────────────────────────────────────────────┘
```

---

##  Seguridad y Secretos

### GitHub Secrets Requeridos

| Secret | Usado en | Descripción |
|--------|----------|-------------|
| `DB_USER` | PR Check | Usuario PostgreSQL Azure |
| `DB_PASSWORD` | PR Check | Contraseña PostgreSQL Azure |
| `GITHUB_TOKEN` | Ambos | Token automático de GitHub (preconfigurado) |
| `ADMIN_GITHUB_TOKEN` | CI/CD | Token con permisos admin para auto-merge |

### Configuración de Secretos

1. Ve a **Settings → Secrets and variables → Actions**
2. Click en **New repository secret**
3. Agrega cada secreto requerido

---

## Documentación Detallada

Para información completa sobre cada workflow:

- **[README-PR-CHECK.md](README-PR-CHECK.md)** - Documentación completa del workflow de validación de PRs
- **[README-CI-CD.md](README-CI-CD.md)** - Documentación completa del workflow de CI/CD y GitOps

---
