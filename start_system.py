"""
Lo scopo principale di questo file è avviare tutti i nodi ATM con terminale separato come da richiesta
"""
import subprocess
import sys
import os
import time
import platform

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_command(script_name: str) -> list:
    """
    Restituisce il comando per aprire un terminale seprato
    """
    script_path = os.path.join(BASE_DIR,script_name)
    system = platform.system()

    if system=="Windows":
        return ['start', "cmd", "/k", sys.executable, script_path]
    elif system=="Darwin":
        apple_script = (
            f'tell application "Terminal" to do script'
            f'"cd {BASE_DIR} && {sys.executable} {script_path}"'
        )
        return ["osascript", "-e", apple_script]
    else:
        terminals = [
            ["gnome-terminal", "--", sys.executable, script_path],
            ["xterm", "-e", sys.executable, script_path],
            ["konsole", "-e", sys.executable, script_path],
            ["xfce4-terminal", "-e", f"{sys.executable} {script_path}"],
        ]
        import shutil
        for terminal_cmd in terminals:
            if shutil.which(terminal_cmd[0]):
                return terminal_cmd
        print("ERRORE: nessun terminale trovato.")
        print("Installa gnome-terminal o xterm e riprova.")
        sys.exit(1)

def open_terminal(script_name: str):
    """
    Apre un terminale separato per il nodo specificato
    """
    system = platform.system()
    cmd = get_command(script_name)

    if system == "Windows":
        subprocess.Popen(cmd,shell=True)
    else:
        subprocess.Popen(cmd)
    
if __name__ =="__main__":
    print("Passo 1: avvio ATM2, ATM3, ATM4 (si mettono in ascolto...)\n")
    for script in ["atm2.py","atm3.py","atm4.py"]:
        open_terminal(script)
        time.sleep(0.5) #Piccola pausa tra uno e l'altro


    print("Passo 2: attendo 3 secondi per permettere ai nodi di avviarsi\n")
    for i in range(3,0,-1):
        print(f" {i}...")
        time.sleep(1)
    
    print("Passo 3: avvio ATM1 (genera il token e avvia il sistema)...\n")
    open_terminal("atm1.py")
    print("Tutti i nodi sono avviati. Controlla i 4 terminali")