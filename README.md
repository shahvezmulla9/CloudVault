# CloudVault – Cloud Computing Mini Project

CloudVault is a student document manager built with Flask. Users can register, log in, upload files, download files, and delete their own files.

## Cloud service mapping (AWS)

- **IaaS:** Amazon EC2 can run an Nginx reverse proxy / monitoring node or host the same Docker container directly.
- **PaaS:** AWS Elastic Beanstalk can host the Flask application without managing the underlying OS.
- **DBaaS:** Amazon RDS for PostgreSQL stores users and document metadata.
- **Storage as a Service:** Amazon S3 stores uploaded documents.
- **Security as a Service / Cloud Security:** AWS IAM controls permissions; Security Groups restrict network access; HTTPS can be provided with ACM; AWS WAF may be added in front of the application.

## Local run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

Without cloud environment variables, CloudVault automatically uses SQLite and a local `uploads/` folder.

## Production environment variables

Copy `.env.example` values into the cloud platform's environment-variable settings. Never commit real passwords or access keys.

## AWS deployment outline

1. Create an S3 bucket with public access blocked.
2. Create RDS PostgreSQL and a database named `cloudvault`.
3. Create an IAM role/user with minimum S3 permissions required by this app.
4. Deploy this code to Elastic Beanstalk using Python or Docker.
5. Set `SECRET_KEY`, `DATABASE_URL`, `S3_BUCKET`, and `S3_REGION` as environment variables.
6. Restrict RDS to accept traffic only from the application security group.
7. Add HTTPS using an Application Load Balancer + ACM certificate.
8. Optional IaaS demonstration: launch a small EC2 instance to run Nginx/status monitoring and explain VM-level control.

## Test cases

1. Register a new user — expected: account created.
2. Login with correct password — expected: dashboard opens.
3. Login with wrong password — expected: rejected.
4. Upload PDF/image — expected: file stored and metadata saved.
5. Download own file — expected: file downloads.
6. Delete own file — expected: object and database record are deleted.
7. Open `/health` — expected: `{ "status": "ok" }`.
