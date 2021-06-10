from block import Block
import json
from flask_pymongo import PyMongo
from node import *
from blockchain import Blockchain

def save_data(self):
        """Save blockchain + open transactions snapshot to a file."""
        try:
            print('xxxxxxxxxxxxxxxxxxxxxx')
            # savable_chain = {
            #     'index': Blockchain.chain.index,
            #     'previous_hash': 
            # }
            # with open('blockchain-{}.json'.format(self.node_id), mode='w') as f:
            # saveable_chain = [
            #     block.__dict__ for block in
            #     [
            #         Block(block_el.index,
            #                 block_el.previous_hash,
            #                 [tx.__dict__ for tx in block_el.transactions],
            #                 block_el.proof,
            #                 block_el.timestamp) for block_el in self.__chain
            #     ]
            # ]
            #     f.write(json.dumps(saveable_chain))
            #     f.write('\n')
            # saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
            # #     f.write(json.dumps(saveable_tx))
            # #     f.write('\n')
            # #     f.write(json.dumps(list(self.__peer_nodes)))
            # print('******IN SAVE_DATA*****')
            # nodes = list(self.__peer_nodes)
            # db.blockchain.insert_one({saveable_chain})
            # db.transaction.insert_one({saveable_tx})
            # db.nodes.insert_one({nodes})
    
        except Exception as ex:
            print(f'**********{ex}************')
            print('Saving failed!')
            
            
from transaction import Transaction        
            
def load_data(self):
        """Initialize blockchain + open transactions data from a file."""
        try:
            print('***********IN_LOAD_DATA****************')
            blockchain = db.blochain.find()
            #We need to convert  the loaded data because Transactions
            # should use OrderedDict
            updated_blockchain = []
            for block in blockchain:
                converted_tx = [Transaction(
                    tx['sender'],
                    tx['recipient'],
                    tx['signature'],
                    tx['amount']) for tx in block['transactions']]
                updated_block = Block(
                    block['index'],
                    block['previous_hash'],
                    converted_tx,
                    block['proof'],
                    block['timestamp'])
                updated_blockchain.append(updated_block)
            self.chain = updated_blockchain
            open_transactions = db.transaction.find()
            # We need to convert  the loaded data because Transactions
            # should use OrderedDict
            updated_transactions = []
            for tx in open_transactions:
                updated_transaction = Transaction(
                    tx['sender'],
                    tx['recipient'],
                    tx['signature'],
                    tx['amount'])
                updated_transactions.append(updated_transaction)
            self.__open_transactions = updated_transactions
            # get peer nodes
            peer_nodes = db.nodes.find()
            # peer_nodes = json.loads(file_content[2])
            self.__peer_nodes = set(peer_nodes)
            
        except Exception as ex:
            print(f'**********{ex}************')
            print('LOADING FAILED!!')
        finally:
            print('Cleanup!')
            
            
            
            
# saveable_keys = [keys.__dict__ for keys in response]