import os
from flask import Blueprint, request, redirect, render_template, flash, send_from_directory, url_for
from backend.models import Restaurante, Cliente, Cardapio, Pedidofeito
from flask_login import current_user, login_required
from backend.ext.database import db
from backend.app import create_app
from werkzeug.utils import secure_filename


bp = Blueprint('restaurante', __name__, url_prefix='/restaurante', template_folder='templates')

ALLOWED_EXTENSIONS = {'png', 'jpeg', 'jpg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/cadastro_restaurante", methods=["GET", "POST"])
def cadastro_restaurante():
    cidades = {
        "-------": "--------",
        "Aracati": "Aracati",
        "Fortim": "Fortim",
        "Icapuí": "Icapuí",
        }
    categorias = {
        "-------": "--------",
        "Japonesa": "Japonesa",
        "Bebidas": "Bebidas",
        "Lanches": "Lanches",
        "Carnes": "Carnes",
        "Doces": "Doces",
        "Pizzas": "Pizzas",
        }
    if request.method == "POST":
        email= request.form["email"]

        cliente= Cliente.query.filter_by(email=email).first()

        if not cliente:
           return redirect("/cliente/login_cliente/cadastro_cliente")
        else:
            novo = Restaurante()
            novo.nome_restaurante = request.form["nome_restaurante"]
            novo.endereco = request.form["endereco"]
            novo.cidade = request.form.get("cidade")
            novo.categoria = request.form.get("categoria")
            novo.cnpj = request.form["cnpj"]
            novo.funcionamento_inicio = request.form["funcionamento_inicio"]
            novo.funcionamento_termino = request.form["funcionamento_termino"]
            novo.cliente_id = cliente.id

            db.session.add(novo)
            db.session.commit()

        return redirect(url_for('cliente.pagina_cliente', id=cliente.id))
    else:
        return render_template("restaurante/cadastro_restaurante.html", cidades=cidades, categorias=categorias)


@bp.route("/pagina_restaurante/<int:id>")
def pagina_restaurante(id):
    restaurante = Restaurante.query.get_or_404(id)
    #restaurantes = Restaurante.query.filter_by(cliente_id = current_user.id).first()
    cardapio=Cardapio.query.all()
    cardapios = Cardapio.query.filter_by(restaurante_id = restaurante.id).all()
    return render_template("restaurante/pagina_restaurante.html", restaurante=restaurante, cardapio=cardapio, cardapios=cardapios)

@bp.route("/excluir_restaurante/<int:id>", methods=["POST"])
def excluir_restaurante(id):
    excluir = Restaurante.query.get_or_404(id)
    db.session.delete(excluir)
    db.session.commit()
    return "Apagou restaurante"

@bp.route('/excluircardapio/<int:id>', methods = ["POST"])
def excluircardapio(id):
    excluir = Cardapio.query.get_or_404(id)
    db.session.delete(excluir)
    db.session.commit()


    return "Apagou cardapio"

@bp.route("/perfil_restaurante/")
def perfil_restaurante():
    cliente = current_user
    restaurante = Restaurante.query.filter_by(cliente_id = cliente.id).first()
    return render_template("restaurante/perfil_restaurante.html", restaurante=restaurante)

@bp.route("/perfil_restaurante/editar_perfil/<int:id>", methods=["GET", "POST"])
def editar_perfil(id):
    cidades = {
        "-------": "--------",
        "Aracati": "ARACATI",
        "Fortim": "FORTIM",
        "Icapuí": "ICAPUÍ",
        }

    categorias = {
        "-------":"-------",
        "Pizzas": "PIZZA",
        "Doces":"DOCES",
        "Lanches":"HAMBURGUER",
        }
    edit = Restaurante.query.get_or_404(id)
    if request.method == "POST":
        edit.nome_restaurante = request.form["nome_restaurante"]
        edit.endereco = request.form["endereco"]
        edit.cidade = request.form.get("cidade")
        edit.categoria = request.form.get("categoria")
        edit.funcionamento_inicio = request.form["funcionamento_inicio"]
        edit.funcionamento_termino = request.form["funcionamento_termino"]
        try:
            db.session.add(edit)
            db.session.commit()
            return redirect ("/restaurante/perfil_restaurante")
        except:
            return "Não deu certo o update"
    else:
        return render_template("restaurante/editar_perfil.html", restaurante=edit, cidades=cidades, categorias=categorias)

@bp.route("/pagina_restaurante/adicionar_cardapio", methods=["GET","POST"])
@login_required
def adicionar_cardapio():
    cliente = current_user
    restaurante = Restaurante.query.filter_by(cliente_id = cliente.id).first()
    if request.method == "POST":
        if 'imagem_prato' not in request.files:
            flash('No file part')
            return redirect(request.url)
        novo=Cardapio()
        imagem_prato = request.files["imagem_prato"]
        novo.nome_prato = request.form["nome_prato"]
        novo.valor = request.form["valor"]
        novo.ingredientes = request.form["ingredientes"]
        novo.tempo_preparo = request.form["tempo_preparo"]
        novo.restaurante_id = restaurante.id
        novo.restaurante_adicionou = restaurante.nome_restaurante
        novo.restaurante_categoria = restaurante.categoria
        try:
            if imagem_prato.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if imagem_prato and allowed_file(imagem_prato.filename):
                filename = secure_filename(imagem_prato.filename)
                app = create_app()
                imagem_prato.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                novo.imagem_prato = filename

            db.session.add(novo)
            db.session.commit()
            return redirect(url_for('restaurante.pagina_restaurante', id=restaurante.id))
        except:
            return "Não deu certo salvar a imagem"
    else:
        return render_template("restaurante/adicionar_cardapio.html")

@bp.route("/upload/<int:id>/<path:filename>")
@login_required
def upload(id,filename):
    app = create_app()
    return send_from_directory(app.config['UPLOAD_FOLDER'], id, filename)

@bp.route("/pedido_solicitado/<int:id>")
@login_required
def pedido_solicitado(id):
    restaurante = Restaurante.query.get_or_404(id)
    pedido = Pedidofeito.query.filter(Pedidofeito.restaurante_id.contains(id))
    pedidos = Pedidofeito.query.filter_by(restaurante_id=restaurante.id).all()
    return render_template("restaurante/pedido_solicitado.html", restaurante=restaurante, pedido=pedido, pedidos=pedidos)

def init_app(app):
    app.register_blueprint(bp)