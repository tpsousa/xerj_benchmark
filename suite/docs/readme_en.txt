CodeMentor AI - Configuration

| Variable | Default | Description |
|---|---|---|
| AI_BASE_URL | https://api.groq.com/openai | Provider base URL |
| AI_MODEL | llama-3.3-70b-versatile | Model |
| SPRING_PROFILES_ACTIVE | dev | dev (H2) or prod (PostgreSQL) |
| RATE_LIMIT_RPM | 10 | Requests per minute per IP |
| PORT | 8080 | HTTP port |

Limits: each request accepts at most 8000 characters of code.
Errors: 400 invalid input, 404 not found, 429 rate limit, 502 provider failure.
The application is licensed under MIT.
