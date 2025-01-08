import requests
import os
import time
from colorama import Fore, Style
from threading import Thread

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_profile_info(profile):
    print(f"\n{Fore.CYAN}[ PROFILE INFO ]{Style.RESET_ALL}")
    print(f"Name: {Fore.GREEN}{profile['name']}{Style.RESET_ALL}")
    print(f"Username: {Fore.GREEN}{profile['username']}{Style.RESET_ALL}")
    print(f"Balance: {Fore.GREEN}{profile['assets']['balance']:.2f}{Style.RESET_ALL}")
    print(f"Energy: {Fore.GREEN}{profile['assets']['remaining_energy']}/{profile['assets']['total_energy']}{Style.RESET_ALL}")
    print(f"Referral Link: {profile['referral']['link']}\n")

def get_profile(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"{Fore.RED}[ ERRO AO OBTER PERFIL ] Status Code: {response.status_code}, Response: {response.text}{Style.RESET_ALL}")
        return None

def start_autotap(profile_url, tap_url, headers, account_name):
    while True:
        profile_data = get_profile(profile_url, headers)
        if profile_data:
            remaining_energy = profile_data['assets']['remaining_energy']

            if remaining_energy >= 500:
                payload = {"amount": remaining_energy}
                response = requests.post(tap_url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    print(
                        f"{Fore.GREEN}[ SUCESSO ]{Style.RESET_ALL} "
                        f"[ TOTAL DE TAPS: {remaining_energy} ] "
                        f"[ BALANCE: {data.get('balance', 0):.2f} ] "
                        f"[ {account_name} ]"
                    )
                else:
                    print(f"{Fore.RED}[ ERRO ] Status Code: {response.status_code}, Response: {response.text} [ {account_name} ]{Style.RESET_ALL}")
            else:
                print(
                    f"{Fore.YELLOW}[ ESPERANDO VALOR MÍNIMO ]{Style.RESET_ALL} "
                    f"500 ENERGY [ {account_name} ] [ {remaining_energy} ]"
                )
        else:
            print(f"{Fore.RED}[ ERRO AO ATUALIZAR PERFIL ]{Style.RESET_ALL} [ {account_name} ]")

        time.sleep(20)

def start_multicontas(profile_url, tap_url):
    clear_terminal()
    print("Quantas contas deseja farmar?")
    num_accounts = int(input("Quantidade: "))

    accounts = []

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
        else:
            print(f"{Fore.RED}[ ERRO AO OBTER PERFIL PARA A CONTA {i} ]{Style.RESET_ALL}")

    clear_terminal()
    print(f"{Fore.CYAN}[ MULTICONTAS PERFIS ]{Style.RESET_ALL}\n")
    for i, (profile, _) in enumerate(accounts):
        print(f"Conta {i + 1}:")
        display_profile_info(profile)

    print("\nIniciando farm para todas as contas...")

    threads = []
    for profile, headers in accounts:
        account_name = profile['name']
        thread = Thread(target=start_autotap, args=(profile_url, tap_url, headers, account_name))
        thread.start()
        threads.append(thread)

    # Aguarda todas as threads finalizarem (teoricamente nunca finalizam pois o farm é contínuo)
    for thread in threads:
        thread.join()

profile_url = "https://app.blombard.com/api/v1/profile"
tap_url = "https://app.blombard.com/api/v1/tap"

clear_terminal()
print("Opções:")
print("1 - Iniciar Autotap")
print("2 - Multicontas")
print("3 - Sair")

choice = input("\nEscolha uma opção: ")

if choice == "1":
    clear_terminal()
    print(f"{Fore.CYAN}Por favor, insira o valor do initdata para iniciar:{Style.RESET_ALL}")
    user_initdata = input("initdata: ")

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "if-none-match": "W/\"2ae-KufCIu3SAi1Ib8NqKKWBv12VWhw\"",
        "initdata": user_initdata,
        "priority": "u=1, i",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "token": ""
    }

    profile_data = get_profile(profile_url, headers)
    if profile_data:
        display_profile_info(profile_data)
        start_autotap(profile_url, tap_url, headers, profile_data['name'])
    else:
        print(f"{Fore.RED}Não foi possível obter informações do perfil. Encerrando...{Style.RESET_ALL}")

elif choice == "2":
    start_multicontas(profile_url, tap_url)
else:
    print("Encerrando...")
