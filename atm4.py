"""
L'atm 4 svolge un'operazione, un prelievo di 500 €
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from atm_node import run_node

NODE_ID = 4
MY_PORT = 5004
TRANSACTIONS = [
    {"type": "withdraw", "amount": 500.0},
    {"type": "withdraw", "amount": 200.0},
    {"type": "withdraw", "amount": 45.0},
    {"type": "withdraw", "amount": 35.0},
]
if __name__ == "__main__":
    run_node(NODE_ID, MY_PORT, TRANSACTIONS)