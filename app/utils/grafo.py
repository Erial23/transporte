import networkx as nx
import requests
from app.models.ruta import Ruta
from app.models.parada import Parada

def obtener_geometria_calle(p1, p2):
    """Consulta OSRM para obtener la distancia real por calles."""
    url = f"http://router.project-osrm.org/route/v1/driving/{p1.longitud},{p1.latitud};{p2.longitud},{p2.latitud}?overview=full&geometries=geojson"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        if data['code'] == 'Ok':
            return data['routes'][0]['geometry']['coordinates'], data['routes'][0]['distance'] / 1000
    except:
        return None, None

def calcular_ruta_optima(id_inicio, id_fin):
    G = nx.Graph()
    rutas_db = Ruta.query.all()
    for r in rutas_db:
        G.add_edge(r.origen_id, r.destino_id, weight=r.distancia)
    try:
        nodos_id = nx.shortest_path(G, source=id_inicio, target=id_fin, weight='weight')
        camino_objs = [Parada.query.get(id) for id in nodos_id]
        geometria = []
        dist_total = 0
        for i in range(len(camino_objs) - 1):
            coords, d = obtener_geometria_calle(camino_objs[i], camino_objs[i+1])
            if coords:
                geometria.extend([[c[1], c[0]] for c in coords])
                dist_total += d
        return {"camino": camino_objs, "geometria": geometria, "distancia": round(dist_total, 2), "tiempo": round((dist_total / 20) * 60)}
    except:
        return None

def obtener_datos_visualizacion():
    paradas = Parada.query.all()
    rutas = Ruta.query.all()
    nodes = [{"data": {"id": str(p.id), "label": p.nombre}} for p in paradas]
    edges = [{"data": {"source": str(r.origen_id), "target": str(r.destino_id), "weight": round(r.distancia, 2)}} for r in rutas]
    return {"nodes": nodes, "edges": edges}