import requests
import os
import time
from colorama import Fore, Style

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

def start_autotap(profile_url, tap_url, headers):
    while True:
        profile_data = get_profile(profile_url, headers)
        if profile_data:
            clear_terminal()
            display_profile_info(profile_data)
            remaining_energy = profile_data['assets']['remaining_energy']

            if remaining_energy >= 500:
                payload = {"amount": remaining_energy}
                response = requests.post(tap_url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    print(
                        f"{Fore.GREEN}[ SUCESSO ]{Style.RESET_ALL} "
                        f"[ TOTAL DE TAPS: {remaining_energy} ] "
                        f"[ BALANCE: {data.get('balance', 0):.2f} ]"
                    )
                else:
                    print(f"{Fore.RED}[ ERRO ] Status Code: {response.status_code}, Response: {response.text}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[ ESPERANDO VALOR MÍNIMO ]{Style.RESET_ALL} 500 ENERGY")
        else:
            print(f"{Fore.RED}[ ERRO AO ATUALIZAR PERFIL ]{Style.RESET_ALL}")

        time.sleep(20)

profile_url = "https://app.blombard.com/api/v1/profile"
tap_url = "https://app.blombard.com/api/v1/tap"

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "if-none-match": "W/\"2ae-KufCIu3SAi1Ib8NqKKWBv12VWhw\"",
    "initdata": "user=%7B%22id%22%3A6508132614%2C%22first_name%22%3A%22%F0%9D%95%BF%F0%9D%96%86%F0%9D%96%89%F0%9D%96%86%F0%9D%96%98%F0%9D%96%8D%20%F0%9D%95%BF%F0%9D%96%98%20%3C%5C%2F%3E%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22devtadash%22%2C%22language_code%22%3A%22pt-br%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FeA-L95HIk4r6u16jiAckEytNa4ZbIfPnXHN1CFDKeqd3LdfWezK_R7iYF4skCq66.svg%22%7D&chat_instance=7426196504867965132&chat_type=private&start_param=6508132614&auth_date=1736361198&signature=G_RwQGs2NIICJgt0MZYaZm4R1M9sJMfufm1rtYgQOSSszLGTbxjhQ8GXGLWA7brKFEM-BHPgSiaMQOTcpmgiBQ&hash=0d5c5a9b950ed4fb2e98609290c0b9f9d0952bbce60a94b925794e8fb65744ad",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "token": ""
}

clear_terminal()

profile_data = get_profile(profile_url, headers)

if profile_data:
    display_profile_info(profile_data)

    print("Opções:")
    print("1 - Iniciar Autotap")
    print("2 - Sair")

    choice = input("\nEscolha uma opção: ")
    if choice == "1":
        start_autotap(profile_url, tap_url, headers)
    else:
        print("Encerrando...")
else:
    print(f"{Fore.RED}Não foi possível obter informações do perfil. Encerrando...{Style.RESET_ALL}")
