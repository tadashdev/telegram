import requests
import os
import time
from threading import Thread, Lock
from colorama import Fore, Style

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_status_line(account_name, status, energy, balance=None, taps=None):
    if status == "waiting":
        return (
            f"{Fore.YELLOW}[ ESPERANDO VALOR MÍNIMO ]{Style.RESET_ALL} "
            f"500 ENERGY [ {account_name} ] [ {energy} ]"
        )
    elif status == "success":
        return (
            f"{Fore.GREEN}[ SUCESSO ]{Style.RESET_ALL} "
            f"[ TOTAL DE TAPS: {taps} ] [ BALANCE: {balance:.2f} ] "
            f"[ {account_name} ]"
        )

def get_profile(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def start_autotap(profile_url, tap_url, headers, account_name, line_positions, lock):
    last_log = None  # Armazena o último log para evitar duplicação
    while True:
        profile_data = get_profile(profile_url, headers)
        if profile_data:
            remaining_energy = profile_data['assets']['remaining_energy']
            if remaining_energy >= 500:
                payload = {"amount": remaining_energy}
                response = requests.post(tap_url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    log = display_status_line(
                        account_name, "success", remaining_energy, balance=data.get("balance", 0), taps=remaining_energy
                    )
                else:
                    log = f"{Fore.RED}[ ERRO ] Status Code: {response.status_code} [ {account_name} ]{Style.RESET_ALL}"
            else:
                log = display_status_line(account_name, "waiting", remaining_energy)

            # Atualiza apenas se o log mudou
            if log != last_log:
                last_log = log
                with lock:
                    line_positions[account_name] = log
                    clear_terminal()
                    for _, line_content in line_positions.items():
                        print(line_content)
        time.sleep(5)

def start_multicontas(profile_url, tap_url):
    clear_terminal()
    print("Quantas contas deseja farmar?")
    num_accounts = int(input("Quantidade: "))

    accounts = []
    line_positions = {}
    lock = Lock()  # Bloqueio para sincronizar atualizações

    for i in range(1, num_accounts + 1):
        clear_terminal()
        print(f"Forneça o initdata para a conta {i}:")
        initdata = input(f"initdata {i}: ")

        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "if-none-match": "W/\"2ae-KufCIu3SAi1Ib8NqKKWBv12VWhw\"",
            "initdata": initdata,
            "priority": "u=1, i",
            "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "token": ""
        }

        profile_data = get_profile(profile_url, headers)
        if profile_data:
            accounts.append((profile_data, headers))
            account_name = profile_data["name"]
            initial_log = display_status_line(account_name, "waiting", profile_data["assets"]["remaining_energy"])
            line_positions[account_name] = initial_log
        else:
            print(f"{Fore.RED}[ ERRO AO OBTER PERFIL PARA A CONTA {i} ]{Style.RESET_ALL}")

    clear_terminal()
    print(f"{Fore.CYAN}[ MULTICONTAS PERFIS ]{Style.RESET_ALL}\n")
    for account_name, log in line_positions.items():
        print(log)

    print("\nIniciando farm para todas as contas...")
    for profile, headers in accounts:
        account_name = profile['name']
        Thread(target=start_autotap, args=(profile_url, tap_url, headers, account_name, line_positions, lock)).start()

profile_url = "https://app.blombard.com/api/v1/profile"
tap_url = "https://app.blombard.com/api/v1/tap"

clear_terminal()
print("Opções:")
print("1 - Iniciar Autotap")
print("2 - Multicontas")
print("3 - Sair")

choice = input("\nEscolha uma opção: ")

if choice == "2":
    start_multicontas(profile_url, tap_url)
else:
    print("Encerrando...")
