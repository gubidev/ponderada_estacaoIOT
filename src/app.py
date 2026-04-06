from flask import Flask, request, jsonify, render_template
import database

app = Flask(__name__)

# Inicializa o banco ao rodar
database.init_db()

@app.route('/', methods=['GET'])
def index():
    # Endpoint do painel principal (exibe as últimas 10 leituras)
    leituras = database.listar_leituras(limite=10)
    return render_template('index.html', leituras=leituras)

@app.route('/leituras', methods=['POST'])
def criar():
    # Recebe JSON do Arduino / simulador
    dados = request.get_json()

    if not dados:
        return jsonify({'erro': 'JSON inválido'}), 400

    if 'temperatura' not in dados or 'umidade' not in dados:
        return jsonify({'erro': 'Campos temperatura e umidade são obrigatórios'}), 400

    id_novo = database.inserir_leitura(
        dados['temperatura'],
        dados['umidade'],
        dados.get('pressao')
    )
    return jsonify({'id': id_novo, 'status': 'criado'}), 201

@app.route('/leituras', methods=['GET'])
def listar():
    leituras = database.listar_leituras(limite=100)
    if request.args.get('formato') == 'json':
        return jsonify(leituras)
    return render_template('historico.html', leituras=leituras)

@app.route('/historico', methods=['GET'])
def historico():
    return listar()

@app.route('/leituras/<int:id>', methods=['GET'])
def detalhe(id):
    leitura = database.buscar_leitura(id)
    if leitura is None:
        return jsonify({'erro': 'Leitura não encontrada'}), 404
    if request.args.get('formato') == 'json':
        return jsonify(leitura)
    return jsonify(leitura)

@app.route('/editar/<int:id>', methods=['GET'])
def editar(id):
    leitura = database.buscar_leitura(id)
    if leitura is None:
        return jsonify({'erro': 'Leitura não encontrada'}), 404
    return render_template('editar.html', leitura=leitura)

@app.route('/leituras/<int:id>', methods=['PUT'])
def atualizar(id):
    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'JSON inválido'}), 400
    if 'temperatura' not in dados or 'umidade' not in dados:
        return jsonify({'erro': 'Campos temperatura e umidade são obrigatórios'}), 400
    database.atualizar_leitura(id, dados['temperatura'], dados['umidade'], dados.get('pressao'))
    return jsonify({'status': 'atualizado'})

@app.route('/leituras/<int:id>', methods=['DELETE'])
def deletar(id):
    database.deletar_leitura(id)
    return jsonify({'status': 'deletado'})

@app.route('/api/estatisticas', methods=['GET'])
def estatisticas():
    return jsonify(database.calcular_estatisticas())

@app.route('/api/leituras/recentes', methods=['GET'])
def leituras_recentes():
    # Usado pelo gráfico no frontend
    leituras = database.listar_leituras(limite=20)
    return jsonify(leituras)

if __name__ == '__main__':
    # Use o modo debug apenas em desenvolvimento
    app.run(debug=True)
