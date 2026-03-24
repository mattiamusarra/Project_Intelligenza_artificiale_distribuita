"""
L'atm 3 svolge un'operazione, un deposito di 100 €
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from atm_node import run_node

NODE_ID = 3
MY_PORT = 5003
TRANSACTIONS = [
    {"type": "deposit", "amount": 100.0},
    {"type": "deposit", "amount": 200.0},
    {"type": "deposit", "amount": 100.0},
    {"type": "deposit", "amount": 50.0},
]
if __name__ == "__main__":
    run_node(NODE_ID, MY_PORT, TRANSACTIONS)