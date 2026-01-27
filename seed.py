from app import create_app, db
from app.models.parada import Parada
from app.models.ruta import Ruta

app = create_app()
with app.app_context():
    db.session.query(Ruta).delete()
    db.session.query(Parada).delete()

    # Coordenadas Reales GPS de Ambato
    p1 = Parada(nombre="Terminal Ingahurco", latitud=-1.2389, longitud=-78.6167)
    p2 = Parada(nombre="Parque Cevallos", latitud=-1.2423, longitud=-78.6253)
    p3 = Parada(nombre="Mall de los Andes", latitud=-1.2685, longitud=-78.6251)
    p4 = Parada(nombre="UTA Huachi", latitud=-1.2782, longitud=-78.6335)
    
    db.session.add_all([p1, p2, p3, p4])
    db.session.commit()

    # Distancias reales calculadas entre puntos
    db.session.add(Ruta(origen_id=p1.id, destino_id=p2.id, distancia=1.2)) # 1.2 km
    db.session.add(Ruta(origen_id=p2.id, destino_id=p3.id, distancia=3.1)) # 3.1 km
    db.session.add(Ruta(origen_id=p3.id, destino_id=p4.id, distancia=1.5)) # 1.5 km
    
    db.session.commit()
    print("✅ Datos reales de Ambato cargados.")