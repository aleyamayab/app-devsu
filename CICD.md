# CI/CD Pipeline

## Arquitectura

```
fix/* (Feature Branch)
  ↓ PR a develop
develop (Integration)
  ↓ CI: Build versión automática
  ↓ Imagen: v1.2.0, develop-abc123
main (Release Ready)
  ↓ Tag: v1.2.0
  ↓ CD: Deploy manual a ambientes
  ├─ dev (v1.2.0-dev)
  ├─ qa (v1.2.0-qa)
  └─ production (v1.2.0)
```

## Workflows

### 1️⃣ PR Check (pr-check.yml)
- **Trigger:** PR a `develop`
- **Acciones:**
  - Lint con flake8
  - Tests con coverage
  - Comenta en PR

### 2️⃣ CI Build (ci-cd.yml)
- **Trigger:** Push a `develop`
- **Acciones:**
  - Lint y tests (si pasan pr-check)
  - Genera versión automática (semantic-release)
  - Build imagen Docker
  - Push a GHCR
  - Crea release en GitHub
  - Genera CHANGELOG.md

### 3️⃣ CD Deploy (deploy.yml)
- **Trigger:** Manual (`workflow_dispatch`)
- **Inputs:** Elegir ambiente (dev/qa/production)
- **Acciones:**
  - Lee última versión con tag
  - Actualiza manifest de K8s
  - Deploya a ambiente seleccionado
  - Verifica rollout

## Flujo de trabajo

### 1. Desarrollo
```bash
# Crear rama
git checkout -b fix/agregar-cache

# Hacer cambios
git commit -m "feat: agregar cache Redis"

# Push
git push origin fix/agregar-cache
```

### 2. PR a develop
- Crea PR en GitHub: `fix/agregar-cache` → `develop`
- GitHub ejecuta `pr-check.yml`
- Si pasa: revisa y aprueba

### 3. Merge a develop
```bash
# En GitHub: Approve y Merge PR
```
- GitHub ejecuta `ci-cd.yml`
- Versión automática: v1.1.0
- Imagen: `v1.1.0`, `1.1`, `develop-abc123`

### 4. Release a main
```bash
# En local
git checkout main
git pull
git merge develop
git tag v1.1.0 -m "Release v1.1.0"
git push origin main --tags
```

### 5. Deploy manual
En GitHub Actions:
1. Ir a **Actions** → **CD Deploy**
2. **Run workflow**
3. Elegir ambiente: `dev`
4. Confirmar

## Versionamiento automático

### Formato de commits
```bash
# Patch: v1.0.0 → v1.0.1
git commit -m "fix: corregir validación"

# Minor: v1.0.0 → v1.1.0
git commit -m "feat: agregar caché"

# Major: v1.0.0 → v2.0.0
git commit -m "feat!: nuevo schema API"
# o
git commit -m "feat: nuevo schema\n\nBREAKING CHANGE: cambió la estructura"
```

### Sin versión
```bash
git commit -m "docs: actualizar README"
git commit -m "chore: dependencias"
git commit -m "style: formato"
```

## Imágenes generadas

### En develop (CI)
```
ghcr.io/aleyamayab/devsu-demo-devops-python:v1.1.0
ghcr.io/aleyamayab/devsu-demo-devops-python:1.1
ghcr.io/aleyamayab/devsu-demo-devops-python:develop-abc123
ghcr.io/aleyamayab/devsu-demo-devops-python:latest
```

### En CD Deploy
```
# dev
image: v1.1.0-dev
namespace: dev
replicas: 2

# qa
image: v1.1.0-qa
namespace: qa
replicas: 3

# production
image: v1.1.0
namespace: production
replicas: 4
```

## Configuración requerida

### GitHub Environments
En **Settings** → **Environments**, crear:

1. **dev**
   - No requiere aprobación
   - Deployment branches: any branch

2. **qa**
   - Requiere 1 revisor
   - Deployment branches: main

3. **production**
   - Requiere 2 revisores
   - Deployment branches: only main

### Secrets de GitHub
En **Settings** → **Secrets and variables** → **Actions**:

- `GITHUB_TOKEN` (automático)
- Si usas Kubernetes remoto:
  - `KUBECONFIG` (base64 del config)

## Troubleshooting

### CI no genera versión
- ✅ Commits siguen conventional commits?
- ✅ Merge a `develop` completado?
- ✅ Permisos de push con tags?

### CD no despliega
- ✅ Tag existe en main?
- ✅ Kubernetes accesible?
- ✅ Namespace existe?
- ✅ Secret KUBECONFIG configurado?

### Imagen no está en GHCR
- ✅ GitHub Token tiene permisos?
- ✅ Verificar logs de CI

## Comandos útiles

```bash
# Ver últimas versiones
git tag | sort -V | tail -5

# Ver commits desde última versión
git log v1.0.0..HEAD --oneline

# Ver workflow status
gh run list -w ci-cd.yml -L 5

# Ver logs de workflow
gh run view <RUN_ID> --log
```

## Características

- ✅ Versionamiento automático (semantic-release)
- ✅ CHANGELOG generado automáticamente
- ✅ Una sola imagen que se promueve entre ambientes
- ✅ Configuración per-ambiente (dev/qa/prd)
- ✅ Deploy manual controlado
- ✅ Lineage de cambios completo
- ✅ Trazabilidad total

## Referencias

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Semantic Release](https://github.com/semantic-release/semantic-release)
