from flask import Flask, jsonify, request  
from blockchain import Blockchain 

import requests
from urllib.parse import urlparse
import argparse

app = Flask(__name__)  

blockchain = Blockchain()  # Crea una instancia de la blockchain
peers = set()

# Crear el parser
parser = argparse.ArgumentParser(description='Peer Node')

# Agregar argumentos
parser.add_argument('--host', type=str, default='localhost', help='Host address')
parser.add_argument('--port', type=int, required=True, help='Port number')

# Parsear los argumentos
args = parser.parse_args()

# Puedes acceder a los argumentos con args.host y args.port
print(f"Host: {args.host}")
print(f"Port: {args.port}")


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
 
@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Bienvenido a la API de Blockchain P2P'})

@app.route('/mine', methods=['POST'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    
    blockchain.new_transaction(sender="0", recipient="direccion", amount=1)
    block = blockchain.new_block(proof)
    
    response = {
        'message': 'Nuevo bloque minado.',
        'index': block['index'],
        'transactions': block['transactions'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Datos incompletos', 400
    
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transacción será añadida al bloque {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {'message': 'La cadena fue reemplazada.', 'new_chain': blockchain.chain}
    else:
        response = {'message': 'Nuestra cadena es autoritativa.', 'chain': blockchain.chain}
    
    return jsonify(response), 200

@app.route('/nodes/sync', methods=['POST'])
def sync_nodes():
    values = request.get_json()
    node_url = values.get('node_url')

    if not node_url:
        return 'Error: No se proporcionó la URL del nodo.', 400

    try:
        response = requests.get(f'{node_url}/chain')
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f'Error al conectar con el nodo remoto: {str(e)}', 500

    remote_chain = response.json().get('chain')
    if not remote_chain:
        return 'Error: No se pudo obtener la cadena del nodo remoto.', 500
    
    if len(remote_chain) > len(blockchain.chain):
        blockchain.chain = remote_chain
        return jsonify({'message': 'Cadena local actualizada con la cadena remota.'}), 200
    else:
        return jsonify({'message': 'La cadena local ya está actualizada o es igual en longitud.'}), 200

@app.route('/register_peer', methods=['POST'])
def register_peer():
    peer_data = request.get_json()
    
    if "nodes" in peer_data:  # Verifica que la clave "nodes" esté presente
        for node in peer_data["nodes"]:
            blockchain.register_node(node)
        return jsonify({
            'message': 'Nodos registrados.',
            'total_nodes': list(blockchain.nodes)
        }), 201
    else:
        return jsonify({"message": "Por favor proporciona una lista de nodos."}), 400
    
    
@app.route('/peers', methods=['GET'])
def get_peers():
    return jsonify({"peers": list(blockchain.nodes)}), 200

@app.route('/nodes', methods=['GET'])
def get_nodes():
    return jsonify({"nodes": list(blockchain.nodes)}), 200

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "Peer is alive!"}), 200

# Luego puedes usar estos valores en tu aplicación
if __name__ == '__main__':
    app.run(host=args.host, port=args.port)
    
    
    
    
    
    
    
    
    
    
    
