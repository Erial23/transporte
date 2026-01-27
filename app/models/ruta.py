from app import db

class Ruta(db.Model):
    __tablename__ = "rutas"
    id = db.Column(db.Integer, primary_key=True)
    origen_id = db.Column(db.Integer, db.ForeignKey("paradas.id"))
    destino_id = db.Column(db.Integer, db.ForeignKey("paradas.id"))
    distancia = db.Column(db.Float, nullable=False)
    
    origen = db.relationship('Parada', foreign_keys=[origen_id])
    destino = db.relationship('Parada', foreign_keys=[destino_id])