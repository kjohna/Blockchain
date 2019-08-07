# Paste your version of blockchain.py from the basic_block_gp
# folder here

import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block

        :param sender: <str> Address of the Recipient
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the BLock that will hold this transaction
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 6
        leading zeroes?
        """
        guess = f'{block_string}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        # SET DIFFICULTY HERE
        # TODO: set to 6 zeros for production
        difficulty = 4
        check = "0" * difficulty
        # print(guess_hash)
        return guess_hash[:difficulty] == check

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid

        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        prev_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{prev_block}')
            print(f'{block}')
            print("\n-------------------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(prev_block):
                print("block hash bad")
                return False
            # Check that the Proof of Work is correct
            block_string = json.dumps(prev_block, sort_keys=True).encode()
            proof_correct = self.valid_proof(block_string, block['proof'])
            if not proof_correct:
                print("block proof of work bad")
                return False

            prev_block = block
            current_index += 1

        return True


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

# return the proof of the last block
@app.route('/latest_block', methods=['GET'])
def latest_block():
    res = {
        'latest_block': blockchain.last_block
    }
    return jsonify(res), 200

# test valid_chain method
@app.route('/check_chain', methods=['GET'])
def check_chain():
    res = {
        "valid_chain": blockchain.valid_chain(blockchain.chain)
    }

    return jsonify(res), 200


@app.route('/mine', methods=['POST'])
def mine():
    # receive a proof of work from the client
    data = request.get_json()
    print(f"proof: {data['proof']}")
    proof = int(data['proof'])
    miner_id = data['miner_id']
    # validate the proof
    block_string = json.dumps(blockchain.last_block, sort_keys=True).encode()
    if blockchain.valid_proof(block_string, proof):
        response = {'message': 'good proof!'}
        print("good proof!")
        # We must give a reward for finding the proof.
        # The sender is "0" to signify that this node has mine a new coin
        # The recipient is the miner_id, it did the mining!
        # The amount is 1 coin as a reward for mining the next block
        blockchain.new_transaction(0, miner_id, 1)
        # # Forge the new Block by adding it to the chain
        last_block_hash = blockchain.hash(blockchain.last_block)
        block = blockchain.new_block(proof, last_block_hash)
        # Send a response with the new block
        response = {
            'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
        }
    else:
        response = {'message': 'bad proof!'}
        print("bad proof!")

    # We run the proof of work algorithm to get the next proof...
    # proof = blockchain.proof_of_work()
    # # We must receive a reward for finding the proof.
    # # The sender is "0" to signify that this node has mine a new coin
    # # The recipient is the current node, it did the mining!
    # # The amount is 1 coin as a reward for mining the next block
    # blockchain.new_transaction(0, node_identifier, 1)

    # # Forge the new Block by adding it to the chain
    # last_block_hash = blockchain.hash(blockchain.last_block)
    # block = blockchain.new_block(proof, last_block_hash)

    # # Send a response with the new block
    # response = {
    #     'message': "New Block Forged",
    #     'index': block['index'],
    #     'transactions': block['transactions'],
    #     'proof': block['proof'],
    #     'previous_hash': block['previous_hash'],
    # }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing Values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'],
                                       values['recipient'],
                                       values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    # Return the chain and its current length
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
