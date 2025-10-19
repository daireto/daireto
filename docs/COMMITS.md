# Conventional Commits

https://www.conventionalcommits.org/es/v1.0.0/

Most common and recommended types of commits based on the [Angular convention](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines):

- `feat`: This type is used for new features introduced in the codebase. For example: "feat: Implement user authentication".
- `fix`: Used for bug fixes. For example: "fix: Resolve issue with incorrect date display".
- `build`: Refers to changes that affect the build system or external dependencies (e.g., npm, yarn, webpack, gulp, etc.). For example: "build: Update webpack configuration for production builds".
- `ci`: Used for changes related to Continuous Integration (CI) and Continuous Delivery (CD). For example: "ci: Configure GitLab CI pipeline for automated testing".
- `docs`: Applies to documentation changes. For example: "docs: Add API documentation for user endpoints".
- `perf`: Used for changes that improve code performance. For example: "perf: Optimize database query for faster response times".
- `refactor`: Refers to a code restructuring that neither fixes a bug nor adds new functionality. For example, renaming variables, functions, etc. Its goal is to improve readability and maintainability. For example: "refactor: Extract user profile component".
- `revert`: Used to revert a previous commit. For example: "revert: Revert "feat: Implement user authentication" due to critical bugs".
- `style`: Applies to changes that do not affect the meaning of the code (formatting corrections, whitespace, linting, etc.). For example: "style: Apply code formatting according to PEP 8".
- `test`: Used to add or modify unit or integration tests. For example: "test: Add unit tests for user service".
- `chore`: Used for other tasks that don't fit into the previous categories. This may include dependency updates, changes to configuration files (like .gitignore), maintenance tasks, etc. For example: "chore: Update dependencies to latest versions".

The commit message format should be as follows:

```text
<type>: <description>

<longer description, if necessary, explaining the changes in more detail>

<reference to the issue, task or pull request, if applicable>
```
