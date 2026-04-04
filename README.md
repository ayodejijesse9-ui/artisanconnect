# ArtisanConnect Nigeria
## Security

This project uses three pre-deploy security tools:

- **Semgrep** — scans FastAPI Python code for vulnerabilities before every push
- **Snyk** — scans requirements.txt for vulnerable dependencies
- **GitHub Advanced Security** — secret scanning and Dependabot alerts on every commit

Run before every push:
```bash
semgrep scan .
snyk test
git push
```