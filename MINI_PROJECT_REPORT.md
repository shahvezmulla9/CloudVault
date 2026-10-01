# MINI PROJECT: CLOUDVAULT – STUDENT DOCUMENT MANAGER

## 1. Aim
To design and deploy a web application on a public cloud platform and demonstrate IaaS, PaaS, DBaaS, Storage as a Service, and cloud security services.

## 2. Project Topic
**CloudVault – Student Document Manager** is a secure web application where students create an account and upload, download, and delete study files such as PDFs, notes, images, and documents.

## 3. Theory
Cloud computing provides computing resources over the Internet on demand. Instead of buying and maintaining all hardware and software locally, users can rent infrastructure, application platforms, databases, storage, and security services from a cloud provider.

**IaaS (Infrastructure as a Service):** IaaS provides virtual machines, networking, and computing infrastructure. In this project, Amazon EC2 can be used as a VM for a reverse proxy, monitoring node, or direct Docker-based deployment. The user controls the operating system and installed software while AWS manages the physical data center and hardware.

**PaaS (Platform as a Service):** PaaS allows developers to deploy applications without managing the complete server operating system. AWS Elastic Beanstalk can run the Flask web application, manage application deployment, health checks, scaling configuration, and the runtime environment.

**DBaaS (Database as a Service):** DBaaS provides a managed database. Amazon RDS for PostgreSQL can store user information and uploaded-file metadata. AWS handles common database administration tasks such as backups, patching, and infrastructure management.

**Storage as a Service:** Cloud object storage stores application files reliably. Amazon S3 is used to store uploaded documents. Files remain outside the application server, making storage easier to scale and manage.

**Security as a Service / Cloud Security:** AWS IAM is used to control permissions. Security Groups restrict network connections. User passwords are stored as secure hashes instead of plain text. HTTPS can be enabled using AWS Certificate Manager and an Application Load Balancer. AWS WAF may also be added to filter malicious web requests.

## 4. Software and Cloud Requirements
Python 3, Flask, Flask-SQLAlchemy, Flask-Login, PostgreSQL, Amazon Web Services, Amazon S3, Amazon RDS, AWS IAM, and a modern web browser.

## 5. System Architecture
User Browser → HTTPS / Load Balancer → Flask Web Application (Elastic Beanstalk / PaaS) → Amazon RDS PostgreSQL (DBaaS)

Flask Web Application → Amazon S3 (Storage as a Service)

Administrator / Monitoring → Amazon EC2 VM (IaaS)

Security across services → IAM + Security Groups + HTTPS + optional WAF

## 6. Procedure
1. Form a group of 3–4 students.
2. Select CloudVault as the cloud-computing mini-project.
3. Choose Amazon Web Services as the public cloud platform.
4. Develop the Flask web application with registration, login, file upload, download, and delete functions.
5. Create a PostgreSQL database using Amazon RDS.
6. Create a private Amazon S3 bucket for user files.
7. Configure IAM permissions so the application can access only the required S3 resources.
8. Deploy the Flask application using AWS Elastic Beanstalk.
9. Configure an EC2 VM as an IaaS demonstration for reverse proxy, monitoring, or direct container hosting.
10. Configure Security Groups and HTTPS.
11. Test registration, login, upload, download, deletion, authorization, and the health endpoint.
12. Record screenshots and test results in the final report.

## 7. Modules
**User Authentication Module:** Registers users, hashes passwords, verifies login credentials, and creates authenticated sessions.

**Document Management Module:** Allows authenticated users to upload, list, download, and delete only their own documents.

**Database Module:** Stores user details and file metadata in SQL tables.

**Cloud Storage Module:** Uploads documents to S3. Download operations can use temporary pre-signed URLs.

**Security Module:** Uses password hashing, access control, IAM permissions, private object storage, restricted database connectivity, and HTTPS.

## 8. Test Results
- User registration: Pass when valid details create a new account.
- User login: Pass when correct credentials open the dashboard.
- Invalid login: Pass when incorrect password is rejected.
- File upload: Pass when supported files are stored successfully.
- File listing: Pass when the current user's files appear on the dashboard.
- File download: Pass when the owner can download a file.
- File deletion: Pass when the owner can remove a file.
- Security: Pass when one user cannot access another user's file record through the normal application flow.
- Health check: Pass when `/health` returns an OK status.

## 9. Advantages
The project is scalable, uses managed cloud services, separates application data from file storage, improves reliability compared with a single local computer, and demonstrates practical cloud service models in one application.

## 10. Conclusion
CloudVault demonstrates how a real web application can use multiple cloud-computing service models together. IaaS provides VM-level infrastructure, PaaS hosts the web application, DBaaS manages structured application data, cloud storage keeps user documents, and security services control access and protect communication. The project shows how cloud services reduce infrastructure-management work while providing scalable and secure resources.
