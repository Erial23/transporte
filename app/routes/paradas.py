from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models.parada import Parada
from app import db

paradas_bp = Blueprint("paradas", __name__)

@paradas_bp.route("/paradas")
@login_required
def ver_paradas():
    todas_las_paradas = Parada.query.all()
    return render_template("paradas.html", paradas=todas_las_paradas)

@paradas_bp.route("/paradas/crear", methods=['POST'])
@login_required
def crear():
    nombre = request.form.get('nombre')
    lat = request.form.get('latitud')
    lng = request.form.get('longitud')
    if nombre and lat and lng:
        nueva = Parada(nombre=nombre, latitud=float(lat), longitud=float(lng))
        db.session.add(nueva)
        db.session.commit()
        flash("Parada guardada con éxito.")
    return redirect(url_for('paradas.ver_paradas'))

@paradas_bp.route("/paradas/eliminar/<int:id>")
@login_required
def eliminar_parada(id):
    from app.models.ruta import Ruta
    Ruta.query.filter((Ruta.origen_id == id) | (Ruta.destino_id == id)).delete()
    parada = Parada.query.get_or_404(id)
    db.session.delete(parada)
    db.session.commit()
    return redirect(url_for('paradas.ver_paradas'))