"""
L'atm 1 è il creatore del token, ed è responsabile di inizializzare balance.txt, con il saldo di partenza, inizializzare transactions.log e generare il token
ed avviareil processo di circolazione nell'anello.
Il token generato contiene solo metadati di controllo:
{"round" : 1, "max_rounds": 20}
ISTRUZIONI  DI AVVIO ( 4 terminali separati, stessa cartella):
Terminale 2: python atm2.py
Terminale 3 python atm3.py
Terminale 4: python atm4.py
Terminale 1: python atm1.py (avviare per ultimo)
"""

import sys,os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))) #Per trovare atm_node.py, la primac cartella dove lo cerca è in questa cartella di progetto
from atm_node import run_node, forward_token, log, write_balance, BALANCE_FILE, TRANSACTION_LOG

NODE_ID = 1
MY_PORT = 5001
MAX_ROUNDS = 20
TRANSACTIONS = [] #atm1 non ha transazioni da eseguire

if __name__ == "__main__":
    log(NODE_ID, "SISTEMA BANCARIO DISTRIBUITO - TOKEN RING")

    #Inizializzazione della risorsa condivisa
    write_balance(1000.0)
    log(NODE_ID, f"Risorsa condivisa inizializzata: {BALANCE_FILE} = 1000.00 €")
    #Pulisce il log precedente 
    with open(TRANSACTION_LOG, "w") as f:
        f.write(f" Log transazioni - avvio sistema\n")
    log(NODE_ID, f"Audit trail inizializzato:{TRANSACTION_LOG}")
    log(NODE_ID, "Attendo 3 secondi per assicurarmi che  agli altri nodi siano avviati...")
    time.sleep(3)

    #---- Creazione del token ----
    #Il token contiene SOLO il permesso di accesso.
    token={
        "finished": {"1": False, "2" : False, "3":False, "4": False}
    }
    log(NODE_ID, f"Token generato: {token}")
    log(NODE_ID, "Nessuna transazione pianificata -> marcato come FINISHED")
    log(NODE_ID, "Nessuna transazione prendente -> sezione critica non richiesta ")
    #Primo invio del token al successore senza entrare nella sezione critica"
    time.sleep(0.4)
    forward_token(NODE_ID, MY_PORT, token)

    #Entra nel loop di ricezione
    run_node(NODE_ID, MY_PORT, TRANSACTIONS)