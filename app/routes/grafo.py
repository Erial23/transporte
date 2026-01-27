from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models.parada import Parada
from app.models.ruta_personalizada import RutaPersonalizada
from app.utils.grafo import calcular_ruta_optima, obtener_datos_visualizacion, obtener_geometria_calle
from app import db
import json
from datetime import datetime

grafo_bp = Blueprint('grafo', __name__)

@grafo_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    paradas = Parada.query.all()
    rutas_guardadas_list = RutaPersonalizada.query.order_by(RutaPersonalizada.fecha_creacion.desc()).all()
    
    resultado = None
    instrucciones = []
    total_distancia = 0
    puntos_json = None
    ruta_seleccionada = None

    ruta_id = request.args.get('ruta_id')
    if ruta_id:
        ruta_db = RutaPersonalizada.query.get(ruta_id)
        if ruta_db:
            ruta_seleccionada = ruta_db
            puntos = json.loads(ruta_db.puntos_json)
            puntos_json = ruta_db.puntos_json
            
            class P:
                def __init__(self, lat, lng):
                    self.latitud, self.longitud = lat, lng

            for i in range(len(puntos) - 1):
                p_orig = P(puntos[i]['lat'], puntos[i]['lng'])
                p_dest = P(puntos[i+1]['lat'], puntos[i+1]['lng'])
                _, dist = obtener_geometria_calle(p_orig, p_dest)
                
                instrucciones.append({
                    'paso': i + 1,
                    'desde': puntos[i]['nombre'],
                    'hacia': puntos[i+1]['nombre'],
                    'distancia': round(dist, 2) if dist else 0
                })
                total_distancia += dist if dist else 0

    if request.method == 'POST':
        orig = request.form.get('origen')
        dest = request.form.get('destino')
        if orig and dest:
            resultado = calcular_ruta_optima(int(orig), int(dest))
            
    return render_template('grafo.html', 
                           paradas=paradas, 
                           rutas_guardadas=rutas_guardadas_list,
                           instrucciones=instrucciones,
                           total=round(total_distancia, 2),
                           puntos_json=puntos_json,
                           ruta_seleccionada=ruta_seleccionada,
                           res=resultado)

@grafo_bp.route('/ruta-multiple')
@login_required
def ruta_multiple():
    return render_template('ruta_multiple.html', paradas=Parada.query.all())

@grafo_bp.route('/rutas-guardadas')
@login_required
def rutas_guardadas():
    rutas = RutaPersonalizada.query.order_by(RutaPersonalizada.fecha_creacion.desc()).all()
    return render_template('rutas_guardadas.html', rutas=rutas)

# FUNCIÓN ACTUALIZADA: AHORA SOPORTA ACTUALIZACIÓN (EDITAR)
@grafo_bp.route('/guardar-ruta-personalizada', methods=['POST'])
@login_required
def guardar_ruta_personalizada():
    data = request.form.get('puntos_data')
    nombre = request.form.get('nombre_ruta') or f"Ruta {datetime.now().strftime('%d/%m %H:%M')}"
    ruta_id = request.form.get('ruta_id') # Capturamos el ID enviado desde el formulario de edición

    if data:
        if ruta_id:
            # Si hay un ID, buscamos la ruta para actualizarla
            ruta_existente = RutaPersonalizada.query.get(ruta_id)
            if ruta_existente:
                ruta_existente.nombre_ruta = nombre
                ruta_existente.puntos_json = data
                ruta_existente.fecha_creacion = datetime.now()
                flash("Ruta actualizada exitosamente.")
            else:
                flash("Error: No se pudo encontrar la ruta para actualizar.")
        else:
            # Si no hay ID, es una ruta nueva
            nueva = RutaPersonalizada(nombre_ruta=nombre, puntos_json=data)
            db.session.add(nueva)
            flash("Ruta guardada exitosamente.")
        
        db.session.commit()
    return redirect(url_for('grafo.rutas_guardadas'))

@grafo_bp.route('/eliminar-ruta/<int:id>', methods=['POST'])
@login_required
def eliminar_ruta(id):
    ruta = RutaPersonalizada.query.get_or_404(id)
    db.session.delete(ruta)
    db.session.commit()
    flash("Ruta eliminada correctamente.")
    return redirect(url_for('grafo.rutas_guardadas'))

@grafo_bp.route('/empezar-ruta')
@login_required
def empezar_ruta():
    ruta_id = request.args.get('ruta_id')
    rutas = RutaPersonalizada.query.order_by(RutaPersonalizada.fecha_creacion.desc()).all()
    
    puntos_json = None
    ruta_seleccionada = None
    
    if ruta_id:
        ruta_seleccionada = RutaPersonalizada.query.get(ruta_id)
        if ruta_seleccionada:
            puntos_json = ruta_seleccionada.puntos_json
            
    return render_template('empezar_ruta.html', 
                           rutas=rutas, 
                           puntos_json=puntos_json, 
                           ruta_seleccionada=ruta_seleccionada)

@grafo_bp.route('/procesar-ruta-libre', methods=['POST'])
@login_required
def procesar_ruta_libre():
    data_json = request.form.get('puntos_data')
    if not data_json: return redirect(url_for('grafo.ruta_multiple'))
    puntos = json.loads(data_json)
    nodes, edges = [], []
    class PTemp:
        def __init__(self, n, la, lo): self.nombre, self.latitud, self.longitud = n, la, lo
    objs = [PTemp(p['nombre'], p['lat'], p['lng']) for p in puntos]
    for i in range(len(objs)):
        nodes.append({"data": {"id": f"p{i}", "label": objs[i].nombre}})
        if i < len(objs) - 1:
            _, dist = obtener_geometria_calle(objs[i], objs[i+1])
            edges.append({"data": {"source": f"p{i}", "target": f"p{i+1}", "weight": round(dist, 2) if dist else 0}})
    return render_template('visualizar_grafo.html', datos={"nodes": nodes, "edges": edges})

@grafo_bp.route('/visualizar')
@login_required
def visualizar_grafo():
    datos_red = obtener_datos_visualizacion()
    rutas_guardadas = RutaPersonalizada.query.all()
    colores = ['#0dcaf0', '#6610f2', '#fd7e14', '#20c997', '#d63384']
    
    for idx, ruta in enumerate(rutas_guardadas):
        puntos = json.loads(ruta.puntos_json)
        color_actual = colores[idx % len(colores)]
        
        for i, p in enumerate(puntos):
            node_id = f"ruta_{ruta.id}_p{i}"
            datos_red['nodes'].append({
                "data": {
                    "id": node_id, 
                    "label": f"{ruta.nombre_ruta}: {p['nombre']}",
                    "tipo": "guardada",
                    "color_nodo": color_actual
                }
            })
            if i > 0:
                prev_id = f"ruta_{ruta.id}_p{i-1}"
                datos_red['edges'].append({
                    "data": {
                        "source": prev_id, 
                        "target": node_id, 
                        "label": "trayecto",
                        "color_linea": color_actual
                    }
                })
    return render_template('visualizar_grafo.html', datos=datos_red)

@grafo_bp.route('/editar-ruta/<int:id>')
@login_required
def editar_ruta(id):
    ruta = RutaPersonalizada.query.get_or_404(id)
    return render_template('ruta_multiple.html', 
                           paradas=Parada.query.all(),
                           puntos_edit=json.loads(ruta.puntos_json),
                           nombre_edit=ruta.nombre_ruta,
                           ruta_id_edit=ruta.id)