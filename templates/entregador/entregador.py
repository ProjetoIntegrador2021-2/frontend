from flask import Blueprint, request, render_template, redirect
from flask_login import current_user
from backend.models import Entregador, Cliente
from backend.ext.database import db



bp = Blueprint('entregador', __name__, url_prefix='/entregador', template_folder='templates')

@bp.route('/parceria')
def parceria():
    return render_template('entregador/cadastro_parceiros.html')

@bp.route('/cadastro_entregador', methods=["GET", "POST"])
def cadastro_entregador():
    regioes = {
    '--------': '--------',
    'Aracati':'ARACATI',
    'Fortim':'FORTIM',
    'Icapuí': 'ICAPUÍ',
    }
    if request.method == "POST":
        email=request.form["email"]

        cliente= Cliente.query.filter_by(email=email).first()
        if not cliente:
            return "Você não é cadastrado como cliente"
        else:
            novo = Entregador()
            novo.regiao = request.form.get('regiao')
            novo.contato = request.form["contato"]
            novo.cpf = request.form["cpf"]
            novo.cnh = request.form["cnh"]
            novo.veiculo = request.form["veiculo"]
            novo.cliente_id = cliente.id

            db.session.add(novo)
            db.session.commit()

            return redirect("/cliente/pagina_cliente")
    else:
        return render_template("entregador/cadastro_entregador.html", regioes=regioes)


@bp.route("/pagina_entregador/<int:id>")
def pagina_entregador(id):
    cliente= current_user
    entregador = Cliente.query.get_or_404(id)
    return render_template("entregador/pagina_entregador.html", entregador=entregador, cliente=cliente)

@bp.route("/perfil_entregador")
def perfil_entregador():
    cliente = current_user
    entregador = Entregador.query.filter_by(cliente_id = cliente.id).first()
    return render_template("entregador/perfil_entregador.html", entregador=entregador)

@bp.route("/perfil_entregador/editar_perfil/<int:id>", methods = ["GET", "POST"])
def editar_perfil(id):
    regioes = {
    '--------': '--------',
    'Aracati':'ARACATI',
    'Fortim':'FORTIM',
    'Icapuí': 'ICAPUÍ',
    }
    edit = Entregador.query.get_or_404(id)
    if request.method == "POST":
        edit.regiao = request.form.get("regiao")
        edit.contato = request.form["contato"]
        edit.cpf = request.form["cpf"]
        edit.cnh = request.form["cnh"]
        edit.veiculo = request.form["veiculo"]
        try:
            db.session.add(edit)
            db.session.commit()
            return redirect("/entregador/perfil_entregador")
        except:
            return "Não deu certo fazer o update"
    else:
        return render_template("entregador/editar_perfil.html", entregador=edit, regioes=regioes)

def init_app(app):
    app.register_blueprint(bp)