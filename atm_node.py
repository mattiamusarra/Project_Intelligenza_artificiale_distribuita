#In questo file andimao ad implementare la logica comune per ogni nodo ATM nel sistema 
#TOKEN -> trasporta solo il permesso di accesso
#FILE ->  balance.txt è la risorsa condivisa persistente
#LOG -> transictions.log registra ogni operazione
#-------------

import socket
import json
import os 
import sys
import time 
from datetime import datetime


#----- CONFIGURAZIONE -----
HOST = "127.0.0.1" #Localhost
BALANCE_FILE = "balance.txt" #risorsa condivisa: saldo del conto
TRANSACTION_LOG = "transactions.log" #audit trail di tutte le operazioni

#Anello logico --> porta di ascolto : porta del successore
RING = {
    5001: 5002,
    5002: 5003,
    5003: 5004,
    5004: 5001,
}
PORT_TO_ID = {5001: 1, 5002: 2, 5003: 3, 5004: 4}


#Logging su console 
def log(node_id: int, msg: str):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] [ATM{node_id}] {msg}",flush=True)

#Accesso alla risorsa condivisa, le funzioni seguenti vengono chiamate solo dalla sezione critica, 
#ovvero solo dal nodo che possiede il token. 
#È il token stesso a garantire che non ci siano accessi concorrenti.
def read_balance() -> float:
    """
    Legge il saldo dal file 
    """
    with open(BALANCE_FILE, "r") as f:
        return float(f.read().strip())
    
def write_balance(amount:float): 
    """
    Scrive il nuovo saldo nel file
    """
    with open(BALANCE_FILE, "w") as f:
        f.write(f"{amount:.2f}")

def write_log(node_id: int, operation: str, amount: float, balance_before: float, balance_after: float):
    """
    Aggiunge una riga al log delle transazioni. Ci permette di ricostruire la storia
    del conto anche dopo un crash
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    entry = (f"{ts} | ATM{node_id} | {operation:<10} |"
             f"importo: {amount:>8.2f} € | "
             f"saldo prima: {balance_before:>8.2f} € |"
             f"saldo dopo: {balance_after:>8.2f} €\n")
    with open(TRANSACTION_LOG, "a") as f:
        f.write(entry)


#---- sezione critica ----
def execute_transaction(node_id: int, transaction: dict):
    """
    Questa funzione viene invocata esclusivamente dal nodo che possiede il token. Il token garantisce che nessun altro
    nodo possa eseguire questa funzione contemporaneamente (mutua esclusione). 
    """
    log(node_id, "Entra nella sezione critica")

    #Leggi il saldo dalla risorsa condivisa
    balance_before = read_balance()
    log(node_id,f"| [1] saldo letto da {BALANCE_FILE}: {balance_before:.2f} €")

    op = transaction["type"]
    amount = transaction["amount"]

    log(node_id, f"| [2] Validazione: {op.upper()} {amount:.2f} €")
    if op == "deposit":
        balance_after = balance_before + amount 
        outcome = f"DEPOSITO +{amount:.2f} € → APPROVATO"
    elif op == "withdraw": 
        if amount > balance_before:
            balance_after = balance_before 
            outcome = f"PRELIEVO - {amount:.2f} € -> RIFIUTATO (fondi insufficienti)"
        else:
            balance_after = balance_before - amount
            outcome = f"PRELIEVO - {amount:.2f} € -> APPROVATO"
    else:
        balance_after = balance_before
        outcome = f"OPERAZIONE SCONOSCIUTA -> IGNORA"
        log(node_id, f"| [3] Esito: {outcome}")

    #Scriviamo il nuovo saldo nella risorsa condivisa 
    write_balance(balance_after)
    log(node_id, f"| [4] Nuovo saldo scritto su {BALANCE_FILE}: {balance_after:.2f} €")
    #Registriamo sul log
    write_log(node_id, op.upper(), amount, balance_before, balance_after)
    log(node_id,f" [5] Operazione registrata in {TRANSACTION_LOG}")
    log(node_id, "Esce dalla sezione critica")


#--- Inoltre del token ---
def forward_token(node_id: int, my_port: int, token: dict):
    """
    Invia il token al nodo successore nell'anello. Il token contiene solo metadati di controllo
    """
    successor_port = RING[my_port]
    successor_id = PORT_TO_ID[successor_port]
    for attempt in range(10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, successor_port))
                s.sendall(json.dumps(token).encode())
            log(node_id, f"Token passato -> ATM{successor_id} (porta {successor_port})")
            return
        except ConnectionRefusedError:
            if all(token["finished"].values()):
                log(node_id, f"ATM{successor_id} già terminato — sistema concluso.")
                return  # ← esce senza errore
            log(node_id, f"ATM{successor_id} non raggiungibile, riprovo... ({attempt+1}/10)")
            time.sleep(1)
    sys.exit(1)

#--- Loop Principale ---
def run_node(node_id: int, my_port: int, transactions: list):
    """
    Loop principale del nodo ATM. Il nodo ascolta sulla propria porta TCP, ad ogni ricezione del token decide se entrare in sezione critica, oppure passare il token al successore dopo aver (eventualmente) operato
    """
    tx_index = 0
    log(node_id, f"Avviato | porta {my_port} -> successore porta {RING[my_port]}")
    if transactions:
        log(node_id, f"Transazioni pianificate: ({len(transactions)}):")
        for i, tx in enumerate(transactions):
            log(node_id, f" [{i+1}] {tx['type'].upper()} {tx['amount']:.2f} €")
    else:
        log(node_id, "Nessuna transazione pianificata")
        log(node_id, "In ascolto ...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, my_port))
        server.listen(1)

        while True:
            conn, _ = server.accept()
            with conn:
                raw = conn.recv(4096).decode()

            token = json.loads(raw)

            #Sezione critica: entra solo se ha transazioni pendenti
            if tx_index < len(transactions):
                execute_transaction(node_id, transactions[tx_index])
                tx_index += 1 
            else:
                log(node_id, "Nessuna transazione pendente -> sezione critica non richiesta")

            #Marca questo nodo come finished se ha finito tutto
            if tx_index >= len(transactions):
                if not token["finished"] [str(node_id)]:
                    token["finished"][str(node_id)] = True
                    log(node_id, "Tutte le transazioni complete -> marcato come FINISHED")

            #Controlla se tutti i nodi hanno finito
            print(token["finished"].values())
            if all(token["finished"].values()):
                log(node_id,"-"*54)
                log(node_id, "Tutti i nodi hanno completato le transazioni")
                log(node_id, f"Saldo finale in {BALANCE_FILE} :{read_balance():.2f} €")
                log(node_id, f"Audit trail disponible in: {TRANSACTION_LOG}")
                forward_token(node_id, my_port,token)
                break
            time.sleep(0.4)
            forward_token(node_id, my_port,token)