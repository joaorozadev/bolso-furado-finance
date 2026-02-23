from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from app.extensions import bcrypt, limiter
from app import database

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/registro', methods=['POST'])
@limiter.limit("5 per minute")
def registrar():
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    senha_pura = dados.get('senha')

    if not nome or not email or not senha_pura:
        return jsonify({"erro": "Dados incompletos"}), 400
    
    senha_hash = bcrypt.generate_password_hash(senha_pura).decode('utf-8')

    try:
        conn = database.criar_conexao()
        database.cadastrar_usuario(conn, nome, email, senha_hash)
        database.liberar_conexao(conn)
        return jsonify({"mensagem": "Usuário criado com sucesso"}), 201
    except Exception as e:
        return jsonify({"erro": "Email já cadastrado ou erro no banco"}), 500
    
@auth_bp.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    dados = request.get_json()
    email = dados.get('email')
    senha_pura = dados.get('senha')

    conn = database.criar_conexao()
    usuario = database.buscar_usuario_por_email(conn, email)
    database.liberar_conexao(conn)

    if usuario:
        id_user, nome_user, hash_banco = usuario
        if bcrypt.check_password_hash(hash_banco, senha_pura):
            token = create_access_token(identity=str(id_user))
            return jsonify({
                "mensagem": "Login realizado!",
                "token": token,
                "usuario": nome_user
            }), 200
    return jsonify({"erro": "Email ou senha incorreta"}), 401