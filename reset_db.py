from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/LAARNIESTRADA/Documents/Thesis/SDUPS_Test6/SDUPS_Backend/instance/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class PDFFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    urgency = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default="Pending")
    comments = db.Column(db.Text, default="")
    uploaded_by = db.Column(db.String(100), nullable=False, default="Unknown")
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    # Drop the existing table
    db.drop_all()
    # Recreate the table with the correct schema
    db.create_all()
    print("Database and tables created successfully!")  # ✅ Confirmation
    print(f"Database file exists: {os.path.exists('C:/Users/LAARNIESTRADA/Documents/Thesis/SDUPS_Test6/SDUPS_Backend/instance/database.db')}")  # ✅ Check file

if __name__ == '__main__':
    app.run(debug=True)