from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/LAARNIESTRADA/Documents/Thesis/SDUPS_Test6/SDUPS_Backend/instance/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class PDFFile(db.Model):
    """Database model for storing PDF file information."""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    urgency_score = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<PDFFile {self.filename}, Score: {self.urgency_score}>"

with app.app_context():
    db.create_all()
    print("Database and tables created successfully!")  # ✅ Confirmation
    print(f"Database file exists: {os.path.exists('C:/Users/LAARNIESTRADA/Documents/Thesis/SDUPS_Test6/SDUPS_Backend/instance/database.db')}")  # ✅ Check file

if __name__ == '__main__':
    app.run(debug=True)


    from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy without attaching it to an app yet



