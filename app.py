import os
import uuid
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

try:
    import boto3
except Exception:
    boto3 = None

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///cloudvault.db").replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "txt", "doc", "docx"}
S3_BUCKET = os.getenv("S3_BUCKET")
S3_REGION = os.getenv("S3_REGION", "ap-south-1")

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_name = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(255), nullable=False)
    storage_type = db.Column(db.String(20), default="local")
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def s3_client():
    if not (boto3 and S3_BUCKET):
        return None
    return boto3.client("s3", region_name=S3_REGION)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Enter name, email and a password of at least 6 characters.", "danger")
            return redirect(url_for("register"))
        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "warning")
            return redirect(url_for("login"))
        user = User(name=name, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.uploaded_at.desc()).all()
    return render_template("dashboard.html", documents=documents)

@app.route("/upload", methods=["POST"])
@login_required
def upload():
    file = request.files.get("file")
    if not file or not file.filename:
        flash("Select a file to upload.", "warning")
        return redirect(url_for("dashboard"))
    if not allowed_file(file.filename):
        flash("Unsupported file type.", "danger")
        return redirect(url_for("dashboard"))

    original = secure_filename(file.filename)
    ext = original.rsplit(".", 1)[1].lower()
    stored = f"{current_user.id}-{uuid.uuid4().hex}.{ext}"

    client = s3_client()
    storage_type = "local"
    if client:
        client.upload_fileobj(file, S3_BUCKET, stored, ExtraArgs={"ContentType": file.mimetype or "application/octet-stream"})
        storage_type = "s3"
    else:
        file.save(os.path.join(UPLOAD_DIR, stored))

    doc = Document(original_name=original, stored_name=stored, storage_type=storage_type, user_id=current_user.id)
    db.session.add(doc)
    db.session.commit()
    flash("File uploaded successfully.", "success")
    return redirect(url_for("dashboard"))

@app.route("/download/<int:doc_id>")
@login_required
def download(doc_id):
    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()
    if doc.storage_type == "s3":
        client = s3_client()
        if not client:
            flash("Cloud storage is not configured.", "danger")
            return redirect(url_for("dashboard"))
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": doc.stored_name, "ResponseContentDisposition": f'attachment; filename="{doc.original_name}"'},
            ExpiresIn=300,
        )
        return redirect(url)
    return send_from_directory(UPLOAD_DIR, doc.stored_name, as_attachment=True, download_name=doc.original_name)

@app.route("/delete/<int:doc_id>", methods=["POST"])
@login_required
def delete(doc_id):
    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()
    if doc.storage_type == "s3":
        client = s3_client()
        if client:
            client.delete_object(Bucket=S3_BUCKET, Key=doc.stored_name)
    else:
        path = os.path.join(UPLOAD_DIR, doc.stored_name)
        if os.path.exists(path):
            os.remove(path)
    db.session.delete(doc)
    db.session.commit()
    flash("File deleted.", "success")
    return redirect(url_for("dashboard"))

@app.route("/health")
def health():
    return {"status": "ok", "service": "CloudVault"}, 200

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
