# Workflow: CI Build & Deployment

## Descripción General

Este workflow automatiza el proceso completo de integración continua (CI) y despliegue continuo (CD) cuando se integra código a la rama `develop`. Utiliza **Semantic Versioning automático** para generar versiones, construir imágenes Docker, y actualizar los manifiestos de Kubernetes para despliegue con **ArgoCD**.

## Propósito

Automatizar el ciclo completo desde el código hasta el despliegue:
1. **Validación del Build**: Verificar que la imagen Docker se construye correctamente
2. **Semantic Versioning**: Generar versión automática basada en commits convencionales
3. **Build & Push**: Construir y publicar imagen Docker al registro
4. **GitOps**: Actualizar manifiestos de Kubernetes para ArgoCD
5. **Despliegue Automático**: ArgoCD detecta cambios y despliega la nueva versión.

## ¿Cuándo se Ejecuta?

El workflow se activa automáticamente cuando:
- Se hace un **push directo** a la rama `develop`
- Se **fusiona un Pull Request** en la rama `develop`

```yaml
on:
  push:
    branches:
      - develop
```

---

## Componentes del Workflow

### Validation Build - Verificación de Construcción**

**¿Qué hace?**
Ejecuta una construcción de prueba de la imagen Docker sin publicarla:

```bash
docker build app/devsu-demo-devops-python
```

**¿Por qué es importante?**
- Detecta errores en el Dockerfile antes del versionamiento
- Valida que todas las dependencias están disponibles
- Verifica que la aplicación puede empaquetarse correctamente
- Ahorra tiempo evitando publicar imágenes defectuosas

**Si falla esta etapa:**
El workflow se detiene inmediatamente y NO se genera una nueva versión. Esto protege el registro de imágenes de versiones rotas.

---

### **Semantic Release - Versionamiento Semántico Automático**

**¿Qué es Semantic Versioning?**

Es un sistema de versionamiento basado en el formato `MAJOR.MINOR.PATCH`:
- **MAJOR** (X.0.0): Cambios incompatibles con versiones anteriores (breaking changes)
- **MINOR** (0.X.0): Nuevas funcionalidades compatibles hacia atrás
- **PATCH** (0.0.X): Correcciones de bugs y mejoras menores

**¿Cómo funciona en este proyecto?**

El workflow analiza automáticamente los mensajes de commit usando **Conventional Commits** para determinar el tipo de versión:

#### Reglas de Versionamiento

Configuradas en [.releaserc.json](../../.releaserc.json):

| Tipo de Commit | Incrementa | Ejemplo | Versión Resultante |
|----------------|------------|---------|-------------------|
| `feat:` | MINOR | `feat: agregar API de búsqueda` | 1.0.0 → 1.1.0 |
| `fix:` | PATCH | `fix: corregir validación email` | 1.0.0 → 1.0.1 |
| `perf:` | PATCH | `perf: optimizar queries DB` | 1.0.0 → 1.0.1 |
| `refactor:` | PATCH | `refactor: simplificar lógica` | 1.0.0 → 1.0.1 |
| `BREAKING CHANGE:` | MAJOR | `feat!: cambiar estructura API` | 1.0.0 → 2.0.0 |
| `docs:`, `chore:`, `test:` | - | No genera release | Sin cambio |

#### Versionamiento por Rama

El proyecto usa **pre-release tags** para diferentes ambientes:

```json
{
  "branches": [
    "main",                              // Producción: 1.0.0
    { "name": "qa", "prerelease": "rc" },      // QA: 1.0.0-rc.1
    { "name": "develop", "prerelease": "beta" } // DEV: 1.0.0-beta.1
  ]
}
```

**En la rama `develop`:**
- Las versiones llevan el tag `-beta`
- Ejemplo: `1.5.0-beta.1`, `1.5.0-beta.2`, etc.
- Cada commit que genera release incrementa el número beta

**Qué genera Semantic Release:**
1. **Tag de Git**: Etiqueta la versión en el repositorio
2. **GitHub Release**: Crea un release con notas generadas automáticamente
3. **CHANGELOG**: Actualiza el archivo CHANGELOG.md (si está configurado)
4. **Variable `new_release_version`**: Disponible para pasos siguientes del workflow

**Ejemplo de secuencia:**

```bash
# Estado inicial: v1.4.0-beta.5

# Commit 1: fix: corregir timeout en API
→ Genera: v1.4.0-beta.6 (PATCH)

# Commit 2: feat: agregar endpoint de reportes
→ Genera: v1.5.0-beta.1 (MINOR - reinicia pre-release)

# Commit 3: feat!: cambiar autenticación a OAuth2
→ Genera: v2.0.0-beta.1 (MAJOR - breaking change)
```

---

### **Build & Push - Construcción y Publicación de Imagen**

**¿Qué hace?**
Solo si Semantic Release generó una nueva versión:

1. **Autentica** en GitHub Container Registry (GHCR)
2. **Construye** la imagen Docker con el tag de la nueva versión
3. **Publica** la imagen al registro

```bash
# Construcción con tag de versión
docker build -t ghcr.io/aleyamayab/devsu-demo-devops-python:1.5.0-beta.1

# Publicación al registry
docker push ghcr.io/aleyamayab/devsu-demo-devops-python:1.5.0-beta.1
```

**Registro utilizado: GitHub Container Registry (GHCR)**
- **URL**: `ghcr.io`
- **Repositorio**: `ghcr.io/aleyamayab/devsu-demo-devops-python`
- **Autenticación**: Token automático de GitHub Actions (`GITHUB_TOKEN`)
- **Visibilidad**: El paquete hereda la visibilidad del repositorio

**¿Por qué GHCR?**
- Integración nativa con GitHub
- Sin límites de pulls para repos públicos
- Almacenamiento en el mismo proveedor que el código
- Control de acceso granular

**Versionamiento de imágenes:**
- Cada imagen se etiqueta con la **versión exacta** de Semantic Release
- No se usa `latest` para evitar ambigüedades
- Permite rollback preciso a cualquier versión anterior

---

## **GitOps - Actualización de Manifiestos Kubernetes**

**¿Qué es GitOps?**

Es una metodología donde la configuración de infraestructura (Kubernetes manifests) se almacena en Git, y el estado deseado del cluster se define mediante commits. ArgoCD sincroniza automáticamente el cluster con el repositorio.

**¿Cómo funciona en este proyecto?**

#### Estructura de Ramas GitOps

El repositorio tiene una rama dedicada para manifiestos de Kubernetes:
- **Rama GitOps**: `manifiesto-k8s`
- **Estructura**:
  ```
  k8s/
    ├── dev/
    │   ├── deployment.yml
    │   ├── service.yml
    │   └── ingress.yml
    ├── qa/
    └── prod/
  ```

#### Flujo de Actualización

**Paso 1: Checkout de la rama GitOps**
```bash
git checkout manifiesto-k8s
```

**Paso 2: Actualización del manifiesto**

El workflow modifica automáticamente el archivo `k8s/dev/deployment.yml` usando `sed`:

```bash
sed -i "s|image: .*|image: ghcr.io/aleyamayab/devsu-demo-devops-python:1.5.0-beta.1|" \
  k8s/dev/deployment.yml
```

**Antes:**
```yaml
spec:
  containers:
  - name: devsu-app
    image: ghcr.io/aleyamayab/devsu-demo-devops-python:1.4.0-beta.5
```

**Después:**
```yaml
spec:
  containers:
  - name: devsu-app
    image: ghcr.io/aleyamayab/devsu-demo-devops-python:1.5.0-beta.1
```

**Paso 3: Crear Pull Request GitOps**

En lugar de hacer commit directo, el workflow crea un **Pull Request** en la rama `manifiesto-k8s`:

```yaml
titulo: "Deploy 1.5.0-beta.1 to DEV"
rama: gitops/dev-1.5.0-beta.1
base: manifiesto-k8s
labels: gitops, deployment
```

**Contenido del PR:**
```markdown
## GitOps Deployment

**Version:** `1.5.0-beta.1`
**Image:** `ghcr.io/aleyamayab/devsu-demo-devops-python:1.5.0-beta.1`

Changes:
- Updated Kubernetes manifest for DEV
```

**¿Por qué un PR y no commit directo?**
- **Revisión**: Permite revisar cambios antes del despliegue
- **Auditoría**: Historial claro de qué se desplegó y cuándo
- **Rollback**: Fácil de revertir si hay problemas
- **Control**: Posibilidad de aprobar manualmente despliegues críticos

**Paso 4: Auto-merge del PR GitOps**

El workflow automáticamente aprueba y fusiona el PR usando:
- Token con permisos de admin (`ADMIN_GITHUB_TOKEN`)
- Método: squash merge (mantiene historial limpio)

```yaml
merge-method: squash
```

**Nota de seguridad:** Se requiere un token especial `ADMIN_GITHUB_TOKEN` porque el `GITHUB_TOKEN` predeterminado no puede aprobar sus propios PRs (protección de GitHub).

---

### **ArgoCD - Despliegue Automático al Cluster**

**¿Qué es ArgoCD?**

ArgoCD es una herramienta de Continuous Deployment para Kubernetes que:
- Monitorea continuamente el repositorio Git (rama `manifiesto-k8s`)
- Detecta cambios en los manifiestos
- Sincroniza automáticamente el cluster con el estado deseado
- Proporciona visibilidad del estado de los despliegues

**Configuración de ArgoCD**

ArgoCD está configurado para:
```yaml
Repositorio: Este repo Git
Rama: manifiesto-k8s
Path: k8s/dev/
Namespace: devsu-dev
Sync Policy: Automatic
```

**Flujo de Despliegue con ArgoCD**

```
1. PR GitOps se fusiona en manifiesto-k8s
             ↓
2. ArgoCD detecta el cambio (polling cada 3 min)
             ↓
3. ArgoCD compara estado deseado vs estado actual
             ↓
4. ArgoCD aplica los cambios al cluster:
   - kubectl set image deployment/devsu-app ...
   - Rolling update (sin downtime)
             ↓
5. Pods antiguos se reemplazan gradualmente
             ↓
6. Health checks verifican que nuevos pods estén OK
             ↓
7. Despliegue completo
```

**Estrategia de Rolling Update:**

Kubernetes actualiza los pods gradualmente:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # Máximo 1 pod extra durante update
    maxUnavailable: 0  # Siempre mantener servicio disponible
```

**Ventajas:**
- **Zero Downtime**: Siempre hay pods sirviendo tráfico
- **Automático**: No requiere intervención manual
- **Rollback rápido**: Si falla, ArgoCD puede revertir
- **Visibilidad**: Dashboard de ArgoCD muestra estado en tiempo real

**Monitoreo del Despliegue:**

Puedes verificar el estado en:
- **ArgoCD UI**: `https://<argocd-url>/applications/devsu-dev`
- **CLI**: `argocd app get devsu-dev`
- **kubectl**: `kubectl get pods -n devsu-dev -w`

---

## Flujo Completo End-to-End

```
┌─────────────────────────────────────────────────────────────┐
│  DESARROLLADOR                                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ 1. feat: agregar nueva API
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  GIT PUSH → develop                                         │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  WORKFLOW CI/CD                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. Validation Build                               │   │
│  │    - docker build (prueba)                           │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │    2. Semantic Release                             │   │
│  │    - Analiza commits                                 │   │
│  │    - Genera versión: 1.5.0-beta.1                    │   │
│  │    - Crea GitHub Release                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   3. Build & Push                                   │   │
│  │    - docker build con tag 1.5.0-beta.1               │   │
│  │    - docker push a GHCR                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  4. GitOps Update                                  │   │
│  │    - Checkout manifiesto-k8s                         │   │
│  │    - Actualiza k8s/dev/deployment.yml                │   │
│  │    - Crea PR GitOps                                  │   │
│  │    - Auto-merge PR                                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  ARGOCD                                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Detecta cambio en manifiesto-k8s                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Sincroniza cluster                                │   │
│  │    - kubectl apply                                   │   │
│  │    - Rolling update de pods                          │   │
│  │    - Health checks                                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│   KUBERNETES CLUSTER - AMBIENTE DEV                       │
│  - Nuevos pods con versión 1.5.0-beta.1 ejecutándose       │
│  - Servicio disponible sin downtime                        │
└─────────────────────────────────────────────────────────────┘
```

---

##  Convenciones de Commit (IMPORTANTE)

Para que Semantic Release funcione correctamente, **DEBES** seguir el formato de Conventional Commits:

###  Formato Correcto

```bash
<tipo>(<scope>): <descripción corta>

[cuerpo opcional]

[footer opcional]
```

### Tipos Principales

| Tipo | Uso | Versión | Ejemplo |
|------|-----|---------|---------|
| `feat:` | Nueva funcionalidad | MINOR | `feat: agregar endpoint de exportación PDF` |
| `fix:` | Corrección de bug | PATCH | `fix: resolver error 500 en búsqueda` |
| `perf:` | Mejora de rendimiento | PATCH | `perf: optimizar query de dashboard` |
| `refactor:` | Refactorización | PATCH | `refactor: extraer lógica de validación` |
| `docs:` | Documentación | - | `docs: actualizar README de API` |
| `test:` | Pruebas | - | `test: agregar tests para modelo User` |
| `chore:` | Mantenimiento | - | `chore: actualizar dependencias` |
| `style:` | Formato de código | - | `style: aplicar black formatter` |

### Breaking Changes

Para indicar cambios incompatibles (MAJOR version):

```bash
feat!: cambiar autenticación de JWT a OAuth2

BREAKING CHANGE: Los tokens JWT anteriores ya no son válidos.
Los clientes deben actualizar a OAuth2.
```

O usando el footer:

```bash
feat: migrar API a v2

BREAKING CHANGE: El endpoint /api/users cambió a /api/v2/users
```

###  Ejemplos Incorrectos (NO hacer)

```bash
# Muy vagos
"actualizaciones"
"cambios"
"fix"

# Sin tipo
"agregar nueva funcionalidad"
"corregir bug en login"

# Formato incorrecto
"Feat agregar API"  # Sin ':'
"FIX: Bug"          # Mayúsculas incorrectas
```

###  Ejemplos Correctos

```bash
feat(api): agregar endpoint de estadísticas de ventas
fix(auth): corregir validación de tokens expirados
perf(db): optimizar query de reportes con índices
refactor(utils): simplificar función de formateo de fechas
docs(readme): agregar instrucciones de instalación local
test(models): agregar cobertura para Product model
chore(deps): actualizar Django de 4.2 a 5.0
```

---

##  Secretos y Permisos

### Secretos Requeridos

Configurados en **Settings → Secrets and variables → Actions**:

| Secret | Descripción | Uso |
|--------|-------------|-----|
| `GITHUB_TOKEN` | Token automático de GitHub | Build, push, release |
| `ADMIN_GITHUB_TOKEN` | Token con permisos de admin | Auto-merge de PRs GitOps |

### Permisos del Workflow

```yaml
permissions:
  contents: write       # Crear tags y releases
  packages: write       # Push a GHCR
  pull-requests: write  # Crear y actualizar PRs
```

### Configuración de `ADMIN_GITHUB_TOKEN`

Para crear el token:
1. Ve a **Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Crea un nuevo token con permisos:
   - `contents`: write
   - `pull-requests`: write
   -  `metadata`: read (obligatorio)
3. Guárdalo en los Secrets del repositorio

---

## 🛠️ Tecnologías y Herramientas

| Herramienta | Versión | Propósito |
|-------------|---------|-----------|
| Docker | Latest | Containerización |
| Semantic Release | v4 | Versionamiento automático |
| GitHub Actions | v4-v6 | Orquestación CI/CD |
| GitHub Container Registry | - | Registro de imágenes |
| ArgoCD | Latest | Continuous Deployment |
| Kubernetes | 1.27+ | Orquestación de containers |

---

## 📊 Monitoreo y Observabilidad

### ¿Cómo verificar que todo funcionó?

1. **GitHub Actions**:
   - Ve a la pestaña "Actions" del repositorio
   - Verifica que el workflow completó 

2. **GitHub Releases**:
   - Ve a la pestaña "Releases"
   - Verifica que se creó la nueva versión beta

3. **GitHub Packages**:
   - Ve a la sección "Packages" del repositorio
   - Verifica que la imagen con el nuevo tag está publicada

4. **Pull Request GitOps**:
   - Revisa los PRs en la rama `manifiesto-k8s`
   - Verifica que se fusionó automáticamente

5. **ArgoCD**:
   - Abre el dashboard de ArgoCD
   - Verifica que la aplicación `devsu-dev` está sincronizada
   - Estado: `Healthy` y `Synced`

6. **Kubernetes**:
   ```bash
   # Ver pods con la nueva versión
   kubectl get pods -n devsu-dev -l app=devsu-app
   
   # Ver imagen desplegada
   kubectl describe deployment devsu-app -n devsu-dev | grep Image
   ```

---

## Troubleshooting

### Error: "Semantic Release: No release published"

**Causa**: Los commits desde la última versión no justifican un nuevo release

**Solución**:
- Verifica que tus commits usan el formato correcto (`feat:`, `fix:`, etc.)
- Si solo hay commits `docs:` o `chore:`, no se genera release
- Revisa el log del workflow para ver qué commits fueron analizados

### Error: "Docker push denied"

**Causa**: Problemas de autenticación con GHCR

**Solución**:
- Verifica que los permisos del workflow incluyen `packages: write`
- Asegúrate de que el paquete en GHCR permite escritura del repositorio
- Revisa que `GITHUB_TOKEN` tiene los permisos necesarios

### Error: "Auto-merge failed"

**Causa**: El token no tiene permisos suficientes

**Solución**:
- Verifica que `ADMIN_GITHUB_TOKEN` está configurado en los Secrets
- Asegúrate de que el token tiene permisos de `contents` y `pull-requests`
- Revisa que el token no haya expirado

### Warning: "ArgoCD out of sync"

**Causa**: ArgoCD detectó diferencias entre Git y el cluster

**Posibles causas**:
- Cambio manual en el cluster (no GitOps)
- ArgoCD aún no sincronizó (espera 3 minutos)
- Configuración de sync deshabilitada

**Solución**:
```bash
# Forzar sincronización manual
argocd app sync devsu-dev

# O desde la UI de ArgoCD, click en "Sync"
```

---


## Referencias

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitOps Principles](https://opengitops.dev/)

---

**Última actualización**: 2026-02-10  
**Versión del workflow**: 1.0.0  
**Mantenido por**: DevOps Team
