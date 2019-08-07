import hashlib
import requests

import sys


# TODO: Implement functionality to search for a proof

def proof_of_work(blockchain):
    """
    Simple Proof of Work Algorithm
    Find a number p such that hash(last_block_string, p) contains 6 leading
    zeroes
    """

    block_string = json.dumps(blockchain.last_block, sort_keys=True).encode()
    p = 0
    while not blockchain.valid_proof(block_string, p):
        p += 1

    return p


if __name__ == '__main__':
    # What node are we interacting with?
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    coins_mined = 0

    r = requests.get(node + '/latest_proof')
    print(r.status_code)
    print(r.json)
    print(r.text)
    # # Run forever until interrupted
    # while True:
    #     # TODO: Get the last proof from the server and look for a new one
    #     # TODO: When found, POST it to the server {"proof": new_proof}
    #     # TODO: We're going to have to research how to do a POST in Python
    #     # HINT: Research `requests` and remember we're sending our data as JSON
    #     # TODO: If the server responds with 'New Block Forged'
    #     # add 1 to the number of coins mined and print it.  Otherwise,
    #     # print the message from the server.
    #     pass
