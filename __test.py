from blockchain import Blockchain
from signer import Signer
import dataclasses

@dataclasses.dataclass
class Transaction:
    sender: str
    recipient: str
    amount: float

identifier = 'TS'
difficulty_number = 2
mining_reward = 10
local_signer = Signer('http://127.0.0.1:5000')
local_signer.sign_transaction(Transaction("asdiml", "ravvy", 10.0))

#local_blockchain = Blockchain(identifier, difficulty_number, mining_reward, local_signer)

#local_blockchain.add_transaction('Joshua', 10.0)
#local_blockchain.mine()
#print([dataclasses.asdict(t) for t in local_blockchain.current_block().transactions])