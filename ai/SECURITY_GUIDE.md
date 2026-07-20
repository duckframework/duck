# Security Guide

## Core Principles

Write secure code by default. Security should be considered during design, implementation, and review.

Never assume external data is trusted. Validate, sanitize, and restrict data at system boundaries.

Prefer secure defaults over convenience. Avoid introducing security risks that require future fixes.

---

# Strict Rules

- Never expose secrets, credentials, tokens, API keys, private URLs, or sensitive configuration values in source code.
- Never commit `.env` files, private keys, certificates, or production credentials.
- Always use environment variables or secure configuration systems for sensitive values.
- Do not disable security protections unless there is a clear, documented reason and the change is limited to the appropriate environment.
- Treat all external input as untrusted until it has been validated by the appropriate layer.
- Never log passwords, tokens, session data, or sensitive personal information.
- Never store passwords in plain text. Always use secure password hashing.
- Never bypass existing security middleware, permission checks, or validation layers.
- Before adding dependencies, consider security impact, maintenance status, and whether the dependency provides enough value.
- Follow the principle of least privilege. Give users, services, and processes only the access they require.

---

# Input Validation

All external input must be treated as untrusted.

Validate:

- User forms.
- Query parameters.
- API payloads.
- Uploaded files.
- URLs.
- Headers.
- Cookies.

Rules:

- Validate data type, length, format, and allowed values.
- Reject unexpected input instead of attempting to silently fix unsafe input.
- Use framework-provided validation utilities where available.
- Keep validation close to the boundary where data enters the system.

Example:

'''python
# Bad

username = request.GET["username"]
query = User.objects.filter(name=username)


# Good

username = validate_username(request.GET.get("username"))
query = User.objects.filter(name=username)
'''

---

# Authentication

Authentication determines who a user is.

Rules:

- Always verify user identity before accessing protected resources.
- Use secure session handling.
- Use expiration for temporary credentials and tokens.
- Do not store sensitive information in client-controlled data.
- Use established authentication systems instead of creating custom ones unless necessary.
- Require strong authentication practices for privileged accounts.

Example:

'''python
# Bad

if user_id == request.user.id:
    show_private_data()


# Good

if request.user.has_permission("view_private_data"):
    show_private_data()
'''

---

# Authorization

Authorization determines what a user is allowed to do.

Rules:

- Always enforce permissions on the server.
- Never rely only on hidden UI elements to restrict access.
- Never trust client-side permission checks.
- Verify ownership before modifying user-owned resources.
- Apply the principle of least privilege.

Example:

'''python
# Bad

delete_record(record_id)


# Good

if user.can_delete(record):
    delete_record(record_id)
'''

---

# Secrets and Configuration

Sensitive values must never be hardcoded.

Bad:

'''python
DATABASE_PASSWORD = "password123"
SECRET_KEY = "abc123"
'''

Good:

'''python
DATABASE_PASSWORD = os.environ["DATABASE_PASSWORD"]
SECRET_KEY = os.environ["SECRET_KEY"]
'''

Sensitive values include:

- Passwords.
- API keys.
- Tokens.
- Encryption keys.
- Database credentials.
- Cloud credentials.
- Private certificates.

---

# Database Security

Rules:

- Use parameterized queries or ORM query APIs.
- Never build SQL queries using string concatenation.
- Validate objects before modifying or deleting them.
- Prevent unauthorized object access.
- Use appropriate database permissions.
- Avoid exposing unnecessary database information.

Bad:

'''python
query = f"SELECT * FROM users WHERE id={user_id}"
'''

Good:

'''python
User.objects.filter(id=user_id)
'''

---

# File Upload Security

Treat uploaded files as unsafe.

Rules:

- Validate file types.
- Limit file sizes.
- Generate safe filenames.
- Store uploads in appropriate locations.
- Never execute uploaded files.
- Do not trust file extensions alone.
- Prevent path traversal attacks.

---

# Web Security

Protect against common web vulnerabilities.

## Cross-Site Scripting (XSS)

Rules:

- Escape user-generated content.
- Avoid rendering untrusted HTML.
- Sanitize content when HTML input is required.
- Do not inject user data into scripts.

## Cross-Site Request Forgery (CSRF)

Rules:

- Use CSRF protection for state-changing requests.
- Do not disable CSRF protection without a strong reason.
- Follow framework recommendations.

## SQL Injection

Rules:

- Never concatenate user input into SQL queries.
- Use ORM APIs or parameterized queries.

## Open Redirects

Rules:

- Validate redirect destinations.
- Do not redirect users to arbitrary external URLs.

---

# Logging and Error Handling

Errors should help developers without exposing sensitive information.

Rules:

- Never expose stack traces or internal details to users in production.
- Never log secrets or sensitive data.
- Use structured logging where possible.
- Include enough context to debug safely.
- Avoid leaking system information through error messages.

Bad:

'''python
logger.info(f"User password: {password}")
'''

Good:

'''python
logger.info(
    "User authentication failed",
    extra={"user_id": user.id},
)
'''

---

# Dependencies

Before adding dependencies:

- Check whether the package is actively maintained.
- Consider security history and known vulnerabilities.
- Avoid unnecessary dependencies.
- Keep dependencies updated.
- Remove unused dependencies.

---

# API Security

Rules:

- Validate all API inputs.
- Authenticate protected endpoints.
- Apply rate limiting where appropriate.
- Avoid exposing unnecessary internal data.
- Use correct HTTP status codes.
- Do not reveal sensitive information in error responses.
- Keep API responses limited to required data.

---

# Frontend Security

Rules:

- Never store secrets in frontend code.
- Assume frontend code is visible to users.
- Never trust client-side validation.
- Avoid exposing privileged operations.
- Sanitize dynamic content.
- Keep sensitive operations on the server.

---

# Balance

Security should improve safety without creating unnecessary complexity.

Rules:

- Apply security measures appropriate to the risk level.
- Do not add restrictions, abstractions, or security layers without a clear benefit.
- Prefer proven framework security features over custom security implementations.
- Avoid over-engineering security for simple, low-risk functionality.

---

# Security Review Checklist

Before completing security-sensitive changes:

- Are all inputs validated?
- Are permissions checked?
- Are secrets protected?
- Are errors safe?
- Are logs safe?
- Are dependencies justified?
- Could an attacker abuse this functionality?
- Does this follow existing security patterns?
- Is the security approach appropriate for the risk level?

---

# Security Mindset

When implementing a feature, ask:

- What input can an attacker control?
- What data should this user be allowed to access?
- What happens if this endpoint is called repeatedly?
- What happens if unexpected data is provided?
- What information could leak through errors, logs, or responses?

Security is part of every implementation decision, not a final step.
