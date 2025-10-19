# Commits Convencionales

https://www.conventionalcommits.org/es/v1.0.0/

Tipos de commits más comunes y recomendados basados en [la convención de Angular](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines):
- `feat`: Este tipo se utiliza para nuevas funcionalidades que introduces en el código. Por ejemplo: "feat: Implement user authentication".
- `fix`: Se usa para correcciones de errores. Por ejemplo: "fix: Resolve issue with incorrect date display".
- `build`: Se refiere a cambios que afectan el sistema de construcción o las dependencias externas (ej: npm, yarn, webpack, gulp, etc.). Por ejemplo: "build: Update webpack configuration for production builds".
- `ci`: Se utiliza para cambios relacionados con la integración continua (CI) y la entrega continua (CD). Por ejemplo: "ci: Configure GitLab CI pipeline for automated testing".
- `docs`: Se aplica a cambios en la documentación. Por ejemplo: "docs: Add API documentation for user endpoints".
- `perf`: Se utiliza para cambios que mejoran el rendimiento del código. Por ejemplo: "perf: Optimize database query for faster response times".
- `refactor`: Se refiere a una reestructuración del código que no corrige un error ni añade una nueva funcionalidad. Por ejemplo, al renombrar variables, funciones, etc. Su objetivo es mejorar la legibilidad y la mantenibilidad. Por ejemplo: "refactor: Extract user profile component".
- `revert`: Se usa para revertir un commit anterior. Por ejemplo: "revert: Revert "feat: Implement user authentication" due to critical bugs".
- `style`: Se aplica a cambios que no afectan el significado del código (correcciones de formato, espacios en blanco, linting, etc.). Por ejemplo: "style: Apply code formatting according to PEP 8".
- `test`: Se utiliza para añadir o modificar pruebas unitarias o de integración. Por ejemplo: "test: Add unit tests for user service".
- `chore`: Se usa para otras tareas que no entran en las categorías anteriores. Esto puede incluir la actualización de dependencias, cambios en archivos de configuración (como .gitignore), tareas de mantenimiento, etc. Por ejemplo: "chore: Update dependencies to latest versions".

El formato del mensaje del commit debería ser como el siguiente:

```text
<tipo>: <descripción>

<descripción más larga, de ser necesario, explicando detalladamente los cambios>

<referencia al issue, tarea o pull request, si aplica>
```
