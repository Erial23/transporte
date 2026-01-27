from app import db
from datetime import datetime

class RutaPersonalizada(db.Model):
    __tablename__ = 'rutas_personalizadas'
    id = db.Column(db.Integer, primary_key=True)
    nombre_ruta = db.Column(db.String(100), nullable=False)
    puntos_json = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)