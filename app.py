from solcx import compile_standard, install_solc
import json
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

install_solc("0.8.0")

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.0",
)

with open("compiled_sol.json", "w") as file:
    json.dump(compiled_sol, file)

"get bytecode"
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

"get abi"
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

w3 = Web3(Web3.HTTPProvider("https://kovan.infura.io/v3/c96233b0679b462a8377b0495128c1bf"))
chain_id = 42
"0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
my_address = "0x48F32aC1c6FA1Cc90Cb92959f7b807282069B246"
PRIVATE_KEY = os.getenv("PRIV_KEY")

# Creating contract
print('deploying...')
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get latest transaction
nonce = w3.eth.getTransactionCount(my_address)
# Submit transaction to create contract
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)

# signed the transaction with own private key
signed_transaction = w3.eth.account.sign_transaction(
    transaction, private_key=PRIVATE_KEY
)
# Simulate the transaction with signed transaction
transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
# wait for previous transaction
transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
print("deployed!")


simple_storage = w3.eth.contract(address=transaction_receipt.contractAddress, abi=abi)
print("favorite number: " + str(simple_storage.functions.retrieve().call()))

print("updating favorite number")
store_transaction = simple_storage.functions.store(10).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
    }
)

store_signed_transaction = w3.eth.account.sign_transaction(
    store_transaction, private_key=PRIVATE_KEY
)

store_transaction_hash = w3.eth.send_raw_transaction(store_signed_transaction.rawTransaction)

store_receipt = w3.eth.wait_for_transaction_receipt(store_transaction_hash)
print("updated")

print("favorite number: " + str(simple_storage.functions.retrieve().call()))
