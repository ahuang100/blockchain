import os
import sys
import requests
import json
import dataclasses

from signer import Signer

@dataclasses.dataclass
class Transaction:
    sender: str
    recipient: str
    amount: float

@dataclasses.dataclass
class SignedTransaction:
    transaction: str
    signature: str


os.environ["NO_PROXY"] = "127.0.0.1"
# Change the following number to the port of the blockchain you want to interact with
port_num = "5000"
address = "http://127.0.0.1:" + port_num
signer = Signer(address)

if __name__ == "__main__":

    print("Input b to see the blockchain on the server.")
    print("Input m to make the server mine a block.")
    print("Input t to add a transaction to the server.")
    print("Input a to see the addresses known to the server.")
    print("Input a+ to add an address to the network.")
    print("Input br to broadcast the local blockchain to the network.")
    print("Input c to change the server.")
    print("Input q to quit.")
    while True:
        print("Interacting with the blockchain at:", address)
        choice = input("> ")
        if choice == "b":
            r = requests.get(address + "/chain")
            json.dump(r.json(), sys.stdout, indent=2)
            print()
            print(r.status_code)
        elif choice == "m":
            r = requests.get(address + "/mine")
            json.dump(r.json(), sys.stdout, indent=2)
            print()
            print(r.status_code)
        elif choice == "t":
            sender = input("Input the sender: ")
            recipient = input("Input the recipient: ")
            amount = input("Input an amount: ")
            try: 
                amount = float(amount)
                transaction = Transaction(sender, recipient, amount)
                transaction_bytes = json.dumps(dataclasses.asdict(transaction)).encode('utf-8')

                signature = signer.generate_signature(transaction_bytes).decode()
                signed_transaction = SignedTransaction(transaction_bytes.decode(), signature)
                payload = dataclasses.asdict(signed_transaction)

                r = requests.post(address + "/transactions/new", json=payload)
                json.dump(r.json(), sys.stdout, indent=2)
                print()
                print(r.status_code)
            except Exception as e: 
                print(e)
        elif choice == "a":
            r = requests.get(address + "/network")
            json.dump(r.json(), sys.stdout, indent=2)
            print()
            print(r.status_code)
        elif choice == "a+":
            new_address = input("Input the new address to add: ")
            new_pubkey = input("Input the public key to add: ")
            payload = {"address": new_address, "pubkey": new_pubkey}
            r = requests.post(address + "/network", json=payload)
            json.dump(r.json(), sys.stdout, indent=2)
            print()
            print(r.status_code)
        elif choice == "br":
            r = requests.get(address + "/broadcast")
            json.dump(r.json(), sys.stdout, indent=2)
            print()
            print(r.status_code)
        elif choice == "c":
            port_num = input("Input the new port: ")
            address = "http://127.0.0.1:" + port_num
        elif choice == "q":
            print("Goodbye.")
            exit()