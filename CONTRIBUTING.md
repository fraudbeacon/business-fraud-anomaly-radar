# Contributing Guide

 Thank you for contributing to this project.

 This repository is maintained by the **DevOps, Backend, Frontend, Cybersecurity, and Data Analytics** teams. All contributors are expected to follow the standards and workflow described below.

 ## 1\. Development Workflow

 All changes must follow this workflow:

 1. Create a feature or bug-fix branch from `main`.
2. Make your changes.
3. Test your changes locally.
4. Push your branch to the repository.
5. Open a Pull Request (PR) against `main`.
6. Wait for the required code review and automated checks.
7. Address review comments.
8. Merge only after all required checks and approvals have passed.

 Direct pushes to `main` are not permitted.

 ## 2\. Branch Naming

 Use descriptive branch names following these conventions:

 - `feature/<name>` — New functionality
- `bugfix/<name>` — Bug fixes
- `hotfix/<name>` — Urgent production fixes
- `refactor/<name>` — Code restructuring without changing functionality
- `chore/<name>` — Maintenance and tooling
- `docs/<name>` — Documentation changes
- `test/<name>` — Test-related changes

 Examples:

```
feature/user-authentication
feature/dashboard
bugfix/login-validation
hotfix/payment-failure
refactor/authentication-service
chore/update-dependencies
docs/api-documentation
test/user-service
```

 Use lowercase letters and hyphens where possible.

 ## 3\. Pull Requests

 Every change intended for `main` must be submitted through a Pull Request.

 A PR should:

 - Have a clear and descriptive title.
- Explain what was changed and why.
- Be focused on a single feature, bug, or related change.
- Include relevant tests.
- Include screenshots for significant frontend/UI changes where appropriate.
- Identify any database, API, infrastructure, security, or configuration changes.
- Not contain secrets, credentials, private keys, or sensitive information.

 At least **one approved review** is required before merging unless an authorized emergency procedure applies.

 ## 4\. Code Review

 Reviewers should consider:

 - Correctness
- Readability and maintainability
- Test coverage
- Performance
- Security
- API compatibility
- Error handling
- Database impact
- Infrastructure impact
- Data/privacy implications

 Reviewers should provide constructive and respectful feedback.

 Approval should only be given when the reviewer is satisfied that the changes meet the project's standards.

 ## 5\. Frontend — React/TypeScript

 Frontend contributions should:

 - Use TypeScript appropriately.
- Follow the existing React project structure.
- Keep components focused and reusable.
- Avoid unnecessary duplication.
- Handle loading, error, and empty states appropriately.
- Include tests for important functionality.
- Follow the project's ESLint and formatting rules.
- Never expose secrets or private credentials in frontend code.

 Run the appropriate linting, type checking, tests, and build commands before opening a PR.

 ## 6\. Backend — Java/Spring

 Backend contributions should:

 - Follow the established Spring project structure.
- Keep controllers focused on HTTP/API concerns.
- Keep business logic in services.
- Use repositories for persistence operations.
- Use DTOs where appropriate for API requests and responses.
- Validate incoming data.
- Handle errors consistently.
- Include appropriate unit and integration tests.
- Avoid exposing sensitive information through API responses or logs.

 Run the project's Maven tests and verification checks before opening a PR.

 ## 7\. Data Analytics

 Changes involving analytics, data processing, dashboards, pipelines, schemas, or datasets should:

 - Clearly document changes to data structures or transformations.
- Consider data quality and validation.
- Avoid exposing sensitive or personally identifiable information.
- Ensure analytical results remain reproducible where applicable.
- Include appropriate tests or validation for data transformations.
- Coordinate with the relevant Backend, DevOps, or Cybersecurity team when changes affect their systems.

 ## 8\. Security

 Security-sensitive changes require appropriate review.

 Examples include:

 - Authentication and authorization
- User permissions
- Encryption
- Secrets management
- Security configuration
- Dependency vulnerabilities
- Network/security configuration
- Sensitive data handling
- Logging and auditing
- Security-related infrastructure

 Do not commit:

 - Passwords
- API keys
- Access tokens
- Private keys
- Database credentials
- Production secrets
- `.env` files containing real credentials

 Security vulnerabilities should **not** be reported through a public Pull Request. Use the project's designated private security-reporting process.

 ## 9\. DevOps and Infrastructure

 Changes involving infrastructure, CI/CD, deployment, cloud resources, containers, or repository automation should:

 - Be reviewed by the DevOps team.
- Avoid hard-coded credentials.
- Use approved secrets/configuration mechanisms.
- Be tested safely before production deployment.
- Document significant infrastructure changes.
- Avoid unnecessary changes to production resources.

 Examples include:

 - GitHub Actions
- Docker
- Kubernetes
- Cloud infrastructure
- Deployment configuration
- CI/CD pipelines
- Monitoring and observability
- Infrastructure as Code

 ## 10\. Dependencies

 Before adding or updating a dependency:

 - Confirm that it is necessary.
- Prefer maintained and reputable packages.
- Check for known security vulnerabilities.
- Avoid unnecessary dependencies.
- Ensure the dependency is compatible with the project.

 Security-sensitive dependencies may require Cybersecurity review.

 ## 11\. Commit Messages

 Use clear commit messages.

 Recommended format:

```
<type>: <description>
```

 Examples:

```
feat: add user authentication
fix: correct token validation
refactor: simplify user service
test: add authentication tests
docs: update API documentation
chore: update dependencies
```

 Keep commits focused and meaningful.

 ## 12\. Testing

 Before submitting a PR, contributors should ensure that:

 - The application builds successfully.
- Relevant unit tests pass.
- Relevant integration tests pass.
- Linting passes.
- Type checking passes for TypeScript code.
- No obvious security issues have been introduced.

 Automated CI checks must pass before a PR can be merged.

 ## 13\. Database Changes

 Database schema or migration changes must:

 - Be reviewed carefully.
- Include appropriate migration files.
- Avoid destructive changes unless explicitly approved.
- Consider backward compatibility.
- Document significant data migrations.

 Production database changes should follow the project's deployment and change-management process.

 ## 14\. Documentation

 Update documentation when changes affect:

 - Public APIs
- Setup instructions
- Environment variables
- Architecture
- Deployment
- Database structure
- User-facing functionality
- Development workflows

 ## 15\. Respectful Collaboration

 All contributors are expected to communicate professionally and respectfully.

 Code review is about improving the project, not criticizing individuals.

 We value:

 - Clear communication
- Constructive feedback
- Collaboration
- Accountability
- Security
- Quality
- Continuous improvement

 Thank you for helping maintain a secure, reliable, and maintainable project.
