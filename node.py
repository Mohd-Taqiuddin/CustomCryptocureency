from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_pymongo import PyMongo
import pymongo
from flask_sqlalchemy import SQLAlchemy
# from pymongo.common import SERVER_SELECTION_TIMEOUT
# from wallet import Wallet
# from blockchain import Blockchain
# import uuid
from utility.hash_util import *

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blockchain.sqlite3'

db = SQLAlchemy(app)


class blockchain(db.Model):
    index = db.Column(db.Integer, primary_key=True)
# app.config['MONGO_URI'] = "mongodb://localhost:27017/sdcoin"

# mongo = PyMongo(app)
# db = mongo.db
# try:
#     # mongo = pymongo.MongoClient(
#     #     host = "localhost",
#     #     port = 27017,
#     #     SERVER_SELECTION_TIMEOUT = 1000
#     # )
#     # mongo = PyMongo(app)
#     # db = mongo.sdcoin

#     app.config['MONGO_URI'] = "mongodb://localhost:27017/sdcoin"

#     mongo = PyMongo(app)
#     db = mongo.db

# except Exception as ex:
    print('*****************')
    print
    print("ERROR - Cannot Connect to db")


@app.route('/', methods=['GET'])
def get_node_ui():
    return send_from_directory('ui', 'node.html')


@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('ui', 'network.html')


@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    global blockchain
    blockchain = Blockchain(wallet.public_key, wallet.node_id)
    # print('*********BLOCKCHAIN_KEY***********')
    # print(blockchain.public_key)

    # if wallet.save_keys():
    #     global blockchain
    #     blockchain = Blockchain(wallet.public_key, port)

    try:

        print('***********x')
        response = {
            '_id': wallet.node_id,
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        print(response)
        # saveable_keys = [keys.__dict__ for keys in response]
        json_res = jsonify(response)
        # print('**********JSONIFIED RESPOSNE********************')
        # print(response)
        # db.wallet_keys.insert_one(response)
        return json_res, 201

    except Exception as ex:
        print('***************************')
        print(ex)
        print('***************************')
        response = {
            'message': 'Saving the keys failed. OR Keys already created, cannot duplicate'
        }
        return jsonify(response), 500
    # else:
    #     response = {
    #         'message': 'Saving the keys failed.'
    #     }
    #     return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
    try:
        # if wallet.load_keys():

        print('*********IDD*************')
        print(wallet.node_id)
        # response = db.wallet_keys.find_one({'_id':wallet.node_id})
        global blockchain
        blockchain = Blockchain(wallet.public_key, wallet.node_id)
        response = {
            '_id': wallet.node_id,
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        json_res = jsonify(response)
        if response['public_key'] == None:
            response = {
                'message': 'Cannot Load Keys, Create Wallet'
            }
            return jsonify(response), 201
        # db
        # return json_res, 201
        print('****************x')
        print(response)

        return json_res, 201
    except Exception as ex:
        print('***************************')
        print(ex)
        print('***************************')
        response = {
            'message': 'Loading the keys failed.'
        }
        return jsonify(response), 500


@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance is not None:
        response = {
            'message': 'Fetched balance successfully.',
            'funds': balance
        }
        return jsonify(response), 200
    else:
        response = {
            'messsage': 'Loading balance failed.',
            'wallet_set_up': wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(key in values for key in required):
        response = {'message': 'Some data is missing.'}
        return jsonify(response), 400
    success = blockchain.add_transaction(
        values['recipient'],
        values['sender'],
        values['signature'],
        values['amount'],
        is_receiving=True)
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': values['sender'],
                'recipient': values['recipient'],
                'amount': values['amount'],
                'signature': values['signature']
            }
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500


@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    if 'block' not in values:
        response = {'message': 'Some data is missing.'}
        return jsonify(response), 400
    block = values['block']
    if block['index'] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):
            response = {'message': 'Block added'}
            return jsonify(response), 201
        else:
            response = {'message': 'Block seems invalid.'}
            return jsonify(response), 409
    elif block['index'] > blockchain.chain[-1].index:
        response = {
            'message': 'Blockchain seems to differ from local blockchain.'}
        blockchain.resolve_conflicts = True
        return jsonify(response), 200
    else:
        response = {
            'message': 'Blockchain seems to be shorter, block not added'}
        return jsonify(response), 409


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key is None:
        response = {
            'message': 'No wallet set up.'
        }
        return jsonify(response), 400
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found.'
        }
        return jsonify(response), 400
    required_fields = ['recipient', 'amount']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data is missing.'
        }
        return jsonify(response), 400
    recipient = values['recipient']
    amount = values['amount']
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    success = blockchain.add_transaction(
        recipient, wallet.public_key, signature, amount)
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine():
    if blockchain.resolve_conflicts:
        response = {'message': 'Resolve conflicts first, block not added!'}
        return jsonify(response), 409
    block = blockchain.mine_block()
    # sd_node = db.nodes.find_one({'_id':wallet.node_id})
    # print(f'***********{sd_node}***************')
    # if sd_node is not None:
    #     if sd_node['_id'] != wallet.node_id:
    #         db.nodes.insert_one({'_id':wallet.node_id})
    # else:
    #     db.nodes.insert_one({'_id':wallet.node_id})
    # # values = request.get_json()
    # if not values:
    #     pass
    # else:
    #     node = values['node']
    #     blockchain.add_peer_node(node)
    if block is not None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message': 'Block added successfully.',
            'node_id': wallet.node_id,
            'block': dict_block,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding a block failed.',
            'wallet_set_up': wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route('/resolve-conflicts', methods=['POST'])
def resolve_conflicts():
    replaced = blockchain.resolve()
    if replaced:
        response = {'message': 'Chain was replaced!'}
    else:
        response = {'message': 'Local chain kept!'}
    return jsonify(response), 200


@app.route('/transactions', methods=['GET'])
def get_open_transaction():
    transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transactions), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
    return jsonify(dict_chain), 200


@app.route('/node', methods=['POST'])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data attached.'
        }
        return jsonify(response), 400
    if 'node' not in values:
        response = {
            'message': 'No node data found.'
        }
        return jsonify(response), 400
    node = values['node']
    blockchain.add_peer_node(node)
    response = {
        'message': 'Node added successfully.',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url == '' or node_url is None:
        response = {
            'message': 'No node found.'
        }
        return jsonify(response), 400
    blockchain.remove_peer_node(node_url)
    response = {
        'message': 'Node removed',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def get_nodes():
    # nodes = list(db.nodes.find())
    response = {
        'all_nodes': nodes
    }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser
    from requests import get
    from wallet import Wallet
    from blockchain import Blockchain
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    ip = get('https://api.ipify.org').text
    ip = str(ip).encode('utf-8')
    id = hash_string_256(ip)
    wallet = Wallet(id)
    blockchain = Blockchain(wallet.public_key, id)
    app.run(host='0.0.0.0', port=port, debug=True)
