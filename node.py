from flask import Flask, jsonify, request
from blockchain import Blockchain
from signer import Signer
import dataclasses
import requests
import base64
import argparse

app = Flask(__name__)

@app.route("/chain", methods=["GET", "POST"])
def chain():
    if request.method == "GET":
        response = {
            "chain": [dataclasses.asdict(block) for block in local_blockchain.chain],
            "length": len(local_blockchain.chain),
        }
        return jsonify(response), 200
    else:
        new_chain = request.get_json()
        replaced = local_blockchain.receive_chain(new_chain)
        if replaced: 
            response = {
                "message": "The chain was replaced",
                "chain": local_blockchain.chain,
            }
        else:
            response = {
                "message": "No changes to the chain",
                "chain": local_blockchain.chain,
            }

        return jsonify(response), 200


@app.route("/mine", methods=["GET"])
def mine():
    local_blockchain.mine()

    response = {
        "status": "Success",
        "index": local_blockchain.current_block().index,
        "transactions": [
            dataclasses.asdict(t) for t in local_blockchain.current_block().transactions
        ],
        "proof": local_blockchain.current_block().proof,
    }
    return jsonify(response), 200


@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    values = request.get_json()
    transaction = values.transaction
    signature_bytes = base64.b64decode(values.signature)

    # Ensure fields are present in transaction
    required = ["sender", "recipient", "amount"]
    if not transaction or not all(k in transaction for k in required):
        return "Missing values in transaction", 400
    
    # Check signature
    # TODO

    local_blockchain.add_transaction(
        values["recipient"], values["amount"]
    )

    response = {
        "message": f"Transaction will be added to block {local_blockchain.next_index()}"
    }
    return jsonify(response), 201


@app.route("/network", methods=["GET", "POST"])
def network():
    # grabbing addresses
    if request.method == "GET":
        response = {"nodes": list(local_blockchain.players)}
        return jsonify(response), 200
    # post
    else:
        value = request.get_json()
        if not value or not ("address" in value):
            return "Missing values", 400

        local_blockchain.add_player(value["address"], value["pubkey"])

        response = {"message": f"Added player address {value['address']} and public key successfully"}
        return jsonify(response), 200

# Add public key to broadcast
@app.route("/broadcast", methods=["GET"])
def broadcast(): 
    successful_broadcasts = []
    for a in local_blockchain.players:
        try:
            r = requests.post(
                a + "/chain",
                json={
                    'pubkey': local_signer.get_pubkey(),
                    'blockchain': [dataclasses.asdict(block) for block in local_blockchain.chain]
                },
            )
            successful_broadcasts.append(a)
        except Exception as e:
            print("Failed to send to ", a)
            print(e)
    response = {"message": "Chain broadcasted", "recipients": successful_broadcasts}
    print({
                    'pubkey': local_signer.pubkey_pem,
                    'blockchain': [dataclasses.asdict(block) for block in local_blockchain.chain]
                })
    return jsonify(response), 200


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a node in a blockchain network.")
    parser.add_argument("-i", "--identifier", default="")
    parser.add_argument("port", default="5000")

    args = parser.parse_args()
    identifier = args.identifier
    port_num = args.port
    difficulty_number = 2
    mining_reward = 10
    local_signer = Signer(identifier)
    local_blockchain = Blockchain(identifier, difficulty_number, mining_reward, local_signer)

    app.run(port=port_num)
