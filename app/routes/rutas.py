from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models.ruta import Ruta
from app.models.parada import Parada
from app.utils.grafo import obtener_geometria_calle
from app import db

# Definición del Blueprint
rutas_bp = Blueprint("rutas", __name__)

@rutas_bp.route("/rutas", methods=['GET', 'POST'])
@login_required
def ver_rutas():
    if request.method == 'POST':
        # Captura los IDs enviados desde el clic en el mapa
        origen_id = request.form.get('origen_id')
        destino_id = request.form.get('destino_id')
        
        if not origen_id or not destino_id:
            flash("Error: Debes seleccionar dos paradas en el mapa.")
            return redirect(url_for('rutas.ver_rutas'))

        if origen_id == destino_id:
            flash("El origen y el destino no pueden ser la misma parada.")
            return redirect(url_for('rutas.ver_rutas'))

        p1 = Parada.query.get(origen_id)
        p2 = Parada.query.get(destino_id)
        
        # Obtenemos la distancia real siguiendo las calles (OSRM)
        _, distancia_vial = obtener_geometria_calle(p1, p2)
        
        if distancia_vial:
            # Creamos la nueva conexión en la base de datos
            nueva_ruta = Ruta(
                origen_id=origen_id, 
                destino_id=destino_id, 
                distancia=distancia_vial
            )
            db.session.add(nueva_ruta)
            db.session.commit()
            flash(f"Conexión guardada: {distancia_vial} km entre {p1.nombre} y {p2.nombre}")
        else:
            flash("No se pudo calcular la ruta vial entre esos puntos.")
            
        return redirect(url_for('rutas.ver_rutas'))

    # Carga inicial de la página
    return render_template("rutas.html", 
                           paradas=Parada.query.all(), 
                           rutas=Ruta.query.all())

@rutas_bp.route("/rutas/eliminar/<int:id>")
@login_required
def eliminar_ruta(id):
    """Elimina una conexión específica del grafo."""
    ruta = Ruta.query.get_or_404(id)
    db.session.delete(ruta)
    db.session.commit()
    flash("Ruta eliminada. El sistema de rastreo se ha actualizado.")
    return redirect(url_for('rutas.ver_rutas'))

@rutas_bp.route("/paradas/eliminar/<int:id>")
@login_required
def eliminar_parada(id):
    """Elimina una parada y todas las rutas asociadas (Eliminación en cascada)."""
    try:
        # 1. Borrar todas las rutas donde la parada sea origen o destino
        Ruta.query.filter((Ruta.origen_id == id) | (Ruta.destino_id == id)).delete()
        
        # 2. Borrar la parada
        parada = Parada.query.get_or_404(id)
        db.session.delete(parada)
        
        db.session.commit()
        flash(f"Parada '{parada.nombre}' y sus rutas conectadas han sido eliminadas.")
    except Exception as e:
        db.session.rollback()
        flash("Error al eliminar la parada.")
        
    return redirect(url_for('paradas.ver_paradas'))

@rutas_bp.route("/sistema/limpiar-todo")
@login_required
def limpiar_todo():
    """Borra absolutamente todos los datos para empezar de cero."""
    try:
        db.session.query(Ruta).delete()
        db.session.query(Parada).delete()
        db.session.commit()
        flash("Sistema reiniciado. Todas las paradas y rutas han sido borradas.")
    except Exception as e:
        db.session.rollback()
        flash("Error al vaciar la base de datos.")
        
    return redirect(url_for('paradas.ver_paradas'))