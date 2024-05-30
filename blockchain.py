import hashlib
import dataclasses
import copy
import json
from dacite import from_dict

@dataclasses.dataclass
class Transaction:
    sender: str
    recipient: str
    amount: float

@dataclasses.dataclass
class SignedTransaction:
    transaction: Transaction
    signature: str

@dataclasses.dataclass
class Block:
    index: int
    transactions: list[SignedTransaction]
    proof: int
    previous_hash: str


class Blockchain:
    def __init__(self, address, difficulty_number, mining_reward, signer):
        self.address = address
        self.difficulty_number = difficulty_number
        self.mining_reward = mining_reward
        self.signer = signer
        self.pubkeylist = {}

        self.chain = []
        self.current_transactions = []
        self.players = set()

        # Create first block
        first_block = self.create_block(1, [], 0, "0")
        while not self.check_proof(first_block):
            first_block.proof += 1
        self.chain.append(first_block)

    def create_block(self, index, transactions, proof, previous_hash):
        return Block(index, copy.copy(transactions), proof, previous_hash)

    def create_transaction(self, sender, recipient, amount):
        return Transaction(sender, recipient, amount)

    def get_transactions(self):
        return self.current_transactions

    def current_block(self):
        return self.chain[-1]

    
    def add_transaction(self, recipient, amount, mining=False):

        # If it is a self-reward for mining, set the sender to None
        if mining is True: 
            transaction = Transaction(None, recipient, amount)
        else: transaction = Transaction(self.address, recipient, amount)

        transaction_bytes = json.dumps(dataclasses.asdict(transaction)).encode('utf-8')

        signature = str(self.signer.generate_signature(transaction_bytes))
        self.current_transactions.append(SignedTransaction(transaction, signature))
    
    
    def add_player(self, address, pubkey): 
        self.players.add(address)
        self.pubkeylist[address] = pubkey

    def next_index(self):
        return len(self.chain) + 1

    def get_length(self):
        return len(self.chain)

    def add_block(self, block): 
        if self.check_proof(block):
            self.chain.append(block)

    def hash_block(self, block): 
        return hashlib.sha256(str(block).encode()).hexdigest()

    def check_proof(self, block):
        # Check that the hash of the block ends in difficulty_number many zeros
        block_hash = self.hash_block(block)
        for i in range(1, self.difficulty_number + 1):
            if block_hash[-i] != '0':
                return False
        return True

    def mine(self):
        # TODO: Don't mine if there have been no transactions to be mined

        # Give yourself a reward at the beginning of the transactions
        self.add_transaction(self.address, 10, mining=True)

        # Find the right value for proof
        guess = 0
        while True:
            block = self.create_block(self.next_index(), self.current_transactions, guess, self.hash_block(self.current_block()))
            if(self.check_proof(block)):
                self.add_block(block)
                break
            guess+=1
        
        # Add the block to the chain
        # Clear your current transactions
        self.current_transactions = []

    # TODO: Add signature checking to validate_chain to check the transaction of each block
    def validate_chain(self, chain):
        # Check that the chain is valid
        # The chain is an array of blocks
        # You should check that the hashes chain together
        # The proofs of work should be valid

        prev_hash = 0
        for i in range(len(chain)):
            if not self.check_proof(chain[i]):
                print(i + " check_proof fail")
                return False

            if i > 0 and prev_hash != chain[i].previous_hash:
                print(i + " prev_hash fail")
                return False
            
            prev_hash = self.hash_block(chain[i])

        return True

    def receive_chain(self, chain_raw_json):
        chain = [from_dict(Block, b) for b in chain_raw_json]
        if self.validate_chain(chain) and len(chain) > self.get_length():
            self.chain = chain
            return True
        return False