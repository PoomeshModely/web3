from solcx import compile_standard, install_solc
import inspect
from web3 import Web3
import json
from dotenv import load_dotenv
import os
from web3.middleware import geth_poa_middleware

load_dotenv()


# Open contract
with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()


# Solidity source code of the contact
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)


# saving abi as json file
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode from json
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi from json
abi = json.loads(
    compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["metadata"]
)["output"]["abi"]


# Connection to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1
my_address = "0xfcf181b3A752F2925A1Aa89033aC9F982Da7DdB6"
private_key = os.getenv("PRAVITE_KEY")
print(private_key)


# Building the transcation
# Create the contract in Python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)
# Submit the transaction that deploys the contract
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": w3.eth.chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)

# Sign the transaction of contract
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# Send the sign transcation
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print(
    "Waiting for transaction to finish..."
)  # Wait for the transaction to be mined in Ganache
# And get the transaction receipt
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Done! Contract deployed to {tx_receipt.contractAddress}")


# Working with deployed Contracts (working with contract needs contract address and contract abi)
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(f"Initial Stored Value {simple_storage.functions.retrieve().call()}")
# call and transact are two things done with contract (calls dont make state change but transact need gas)


# Initialing the value 15
greeting_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": w3.eth.chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,  # +1 because every transaction creates new nonce
    }
)

signed_greeting_txn = w3.eth.account.sign_transaction(
    greeting_transaction, private_key=private_key
)

tx_greeting_hash = w3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
print("Updating stored Value...")

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_greeting_hash)
print(simple_storage.functions.retrieve().call())
print("Deployed Sucessfully..!")
