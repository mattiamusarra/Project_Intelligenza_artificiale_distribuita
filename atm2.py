"""
L'atm 2 svolge un'operazione, un prelievo di 200 €
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from atm_node import run_node

NODE_ID = 2
MY_PORT = 5002
TRANSACTIONS = [
    {"type": "withdraw", "amount": 200.0},
    {"type": "withdraw", "amount": 50.0},
    {"type": "withdraw", "amount": 30.0},
    {"type": "withdraw", "amount": 25.0},
]

if __name__ == "__main__":
    run_node(NODE_ID, MY_PORT, TRANSACTIONS)