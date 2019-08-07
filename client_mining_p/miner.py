import hashlib
import requests
import json
import time

import sys


# TODO: Implement functionality to search for a proof

def proof_of_work(block):
    """
    Simple Proof of Work Algorithm
    Find a number p such that hash(last_block_string, p) contains 6 leading
    zeroes
    """

    block_string = json.dumps(block, sort_keys=True).encode()
    p = 0
    while not valid_proof(block_string, p):
        p += 1
    print(block_string)
    guess = f'{block_string}{p}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    print(guess_hash)

    return p


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
    return guess_hash[:difficulty] == check


if __name__ == '__main__':
    # What node are we interacting with?
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    coins_mined = 0
    running = True

    # Run forever until interrupted
    while running:
        # Get the last block from the server and look for a new one
        r = requests.get(node + '/latest_block')
        # print(r.status_code)
        # # print(r.json)
        # print(r.text)
        block = json.loads(r.text)["latest_block"]
        found = False
        start_time = time.time()
        while not found:
            proof = proof_of_work(block)
            found = valid_proof(json.dumps(
                block, sort_keys=True).encode(), proof)
        find_time = time.time() - start_time
        running = False
        print(f"proof: {proof} found in {find_time}s")
        # When found, POST it to the server {"proof": new_proof}
        # TODO: We're going to have to research how to do a POST in Python
        # HINT: Research `requests` and remember we're sending our data as JSON
        data = json.dumps({'proof': proof})
        headers = {'content-type': 'application/json'}
        print(data)
        r = requests.post(node + '/mine', data=data, headers=headers)
        print(f"server responds: {r.status_code} - {r.text}")
        # TODO: If the server responds with 'New Block Forged'
        # add 1 to the number of coins mined and print it.  Otherwise,
        # print the message from the server.
        pass
