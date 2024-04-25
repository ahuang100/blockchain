import hashlib
import time
from dataclasses import dataclass
import copy

@dataclass
class Transaction:
    sender: str
    recipient: str
    amount: float


@dataclass
class Block:
    index: int
    transactions: list[Transaction]
    proof: int
    previous_hash: str


class Blockchain:
    def __init__(self, address, difficulty_number, mining_reward):
        self.address = address
        self.difficulty_number = difficulty_number
        self.mining_reward = mining_reward
        self.chain = []
        self.current_transactions = []
    
        # manually added first block to the chain so adding another block is possible since it requires hash of prev block
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

    def add_transaction(self, sender, recipient, amount):
        self.current_transactions.append(Transaction(sender, recipient, amount))

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
        hashed = self.hash_block(block)
        checkzeros = hashed[-self.difficulty_number:]
        for i in checkzeros:
            if i != '0':
                return False
        return True

    def mine(self):
        # Give yourself a reward at the beginning of the transactions
        reward = self.create_transaction("Block reward", self.address, self.mining_reward)
        self.current_transactions.insert(0, reward)

        # Find the right value for proof
        prevblock = self.current_block()
        prevhashvalue = self.hash_block(prevblock)

        powguess = 0 
        while(True):
            testblock = self.create_block(self.next_index(), self.current_transactions, powguess, prevhashvalue)
            if(self.check_proof(testblock)):
                break
            powguess += 1
        
        # Add the block to the chain
        self.add_block(testblock)

        # Clear your current transactions
        self.current_transactions = []



# (_)