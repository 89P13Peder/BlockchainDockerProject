import hashlib
import json 
from time import time
import requests #hacer solicitudes HTTP a otros nodos
from urllib.parse import urlparse #Registrar nodos

class Blockchain:
    def __init__(self):
        self.chain = [] #Lista de cadena de bloques
        self.current_transactions = [] #Lista de transacciones actuales
        self.nodes = set() #Almacenar nodos
        self.new_block(previous_hash='1', proof=100) #Bloque génesis con su hash predefinido
                                                     # y un proof o prueba de trabajo.
    #Agregar nuevo nodo a la lista de nodso:                                                 
    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc) 
        print(f'Nodo registrado: {parsed_url.netloc}') 
        
    #Validar la blockchain:    
    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1
        
        while current_index < len(chain):
            
            block = chain[current_index]
            #Verificar hash del bloque anterior, tiene que ser correcto:
            if block['previous_hash'] != self.hash(last_block):
                return False
            #Verificar la prueba de trabajo:
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            
            last_block = block
            current_index += 1
            
        return True
    
     # Algoritmo de consenso, se resuelve un conficto 
     # reemplazando una cadena con la más larga en la red:
    def resolve_conflicts(self):
        
        neighbours = self.nodes
        new_chain = None
        
        max_length = len(self.chain)
        
        for node in neighbours:
            try:
                response = requests.get(f'http://{node}/chain')

                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']
        
                    if length > max_length and self.valid_chain(chain):
                        max_length = length
                        new_chain = chain
            except requests.exceptions.RequestException as e:
                print(f"Error al conectar con {node}: {e}")

        if new_chain:
            self.chain = new_chain
            return True
        
        return False
        
        
    #Funcion para crear un bloque y añadirlo a la cadena: 
    def new_block(self, proof, previous_hash=None):
        
        block = {
                'index':len(self.chain) + 1, # índice del bloque
                'timestamp':time(), # tiempo en que el bloque se creó
                'transactions':self.current_transactions, # Transacciones del bloque (informacióncon la que se crea el hash)
                'proof': proof, # Prueba de trabajo para validar el bloque
                'previous_hash': previous_hash or self.hash(self.chain[-1]), #Hash del bloque anterior
            }
        self.current_transactions = [] #Reinicia la lista de transacciones, las actuales fueron añadidas al bloque.
        self.chain.append(block)
        return block
    
    #Función para añadir una nueva transacción a la lista de transacciones actuales:
    def new_transaction(self, sender, recipient, amount):
        #Añadir una nueva transacción: 
        self.current_transactions.append({
            'sender': sender, #Dirección de a quién envía los fondos
            'recipient':recipient, #Dirección de quién recibe los fondos
            'amount': amount, #Monto de la transacción
            })
        #Retornar el índice del bloque que contiene la transacción
        return self.last_block['index'] + 1
    
    #Método estático para crear el hash de un bloque
    @staticmethod
    def hash(block):
        #Se ordena y convierte el bloque en una cadena JSON
        block_string = json.dumps(block, sort_keys=True).encode()
        #Crear un hash SHA-256 de esa cadena y lo devuelve:
        return hashlib.sha256(block_string).hexdigest()
        
    
    #Propiedad que obtiene el último bloque de la cadena:
    @property
    def last_block(self):
        return self.chain[-1]
    
    #Proof of work que resuelve el problema de prueba de trabajo:
    def proof_of_work(self, last_proof):
        proof = 0
        #Se repite hasta encontrar una prueba válida:
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof
    
    #Método estático para validar si la prueba es correcta: 
    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode() #Se crea un valor basandose en la prueba anterior y la nueva
        guess_hash = hashlib.sha256(guess).hexdigest() #Crea un hash del valor guess
        #Retorna true si tiene 4 ceros inicialmente en el hash
        return guess_hash[:4] == "0000"
    
        
        
        
        
        
        
        