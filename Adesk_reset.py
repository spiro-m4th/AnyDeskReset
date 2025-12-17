import os
import shutil
import subprocess
import time
from colorama import init, Fore
from colorama import Back
from colorama import Style
from id_changer import change_id
from backup_restore import restore_user_conf_interactive
import random
import pyfiglet
init(autoreset=True)


# Backup user.conf
def backup_user_conf_main():
    user_conf = os.path.expandvars(r"%APPDATA%\AnyDesk\user.conf")
    backup_conf = os.path.expanduser("~/Desktop/user.conf.backup")

    if os.path.exists(user_conf):
        if os.path.exists(backup_conf):
            print(Style.BRIGHT + Fore.YELLOW + "A Pasta backup user.conf.backup ja existe no Desktop.")
            choice = input(Style.BRIGHT + Fore.CYAN + "Deseja sobrescrever? (y = Sobrescrever, n = Manter): ").strip().lower()
            if choice == 'y':
                shutil.copy(user_conf, backup_conf)
                print(Style.BRIGHT + Fore.GREEN + "Pasta backup sobrescrita com sucesso.")
            elif choice == 'n':
                print(Style.BRIGHT + Fore.YELLOW + "Usando pasta de backup existente.")
            else:
                print(Style.BRIGHT + Fore.RED + "Escolha invalida. Mantendo a pasta de backup antiga")
        else:
            print(Style.BRIGHT + Fore.YELLOW + "Criando um novo backup em user.conf...")
            shutil.copy(user_conf, backup_conf)
            print(Style.BRIGHT + Fore.GREEN + "Backup concluido.")
    else:
        print(Style.BRIGHT + Fore.YELLOW + "A pasta user.conf não foi encontrada. Pulando o save.")

 # Matar o processo AnyDesk
def Killing_AnyDesk():
    print(Style.BRIGHT + Fore.GREEN + "Fechando o AnyDesk...")
    try:
        result = subprocess.run(
            ["taskkill", "/IM", "AnyDesk.exe", "/F"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(Style.BRIGHT + Fore.GREEN + "AnyDesk finalizado com sucesso.")
    except subprocess.CalledProcessError:
        print(Style.BRIGHT + Fore.RED + "Finalizar AnyDesk falhou. Pode não estar em execução ou não possui permissão elevada.")

# Remover versao antiga
def remove_anydesk():
    print(Style.BRIGHT + Fore.YELLOW + "Removendo versão antiga do AnyDesk...")

    choice = input(Style.BRIGHT + Fore.CYAN +
                   "Voce deseja remover o AnyDesk da pasta padrão - default (d) ou uma pasta especifica - custom (c)? (d/c): ").strip().lower()

    if choice == 'd':
        # Pasta padrão
        paths_to_remove = [
            r"C:\ProgramData\AnyDesk",
            os.path.expandvars(r"%APPDATA%\AnyDesk"),
            os.path.expandvars(r"%LOCALAPPDATA%\AnyDesk"),
            r"C:\Program Files (x86)\AnyDesk"
        ]
        for path in paths_to_remove:
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)
                print(Style.BRIGHT + Fore.YELLOW + f"Deletado: {path}")
            else:
                print(Style.BRIGHT + Fore.YELLOW + f"Pasta {path} não encontrada..")
    elif choice == 'c':
        # Diretorio customizado do usuario
        print(Style.BRIGHT + Fore.CYAN + "Por favor, selecione uma pasta para remocao.")
        root = tk.Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        custom_path = filedialog.askdirectory(title="Select AnyDesk Directory")

        if custom_path:
            if os.path.exists(custom_path):
                try:
                    shutil.rmtree(custom_path, ignore_errors=True)
                    print(Style.BRIGHT + Fore.GREEN + f"Deletado: {custom_path}")
                except OSError as e:
                    print(Style.BRIGHT + Fore.RED + f"Falha ao deletar {custom_path}: {e}")
            else:
                print(Style.BRIGHT + Fore.RED + f"O diretorio '{custom_path}' não existe..")
        else:
            print(Style.BRIGHT + Fore.GREEN + "Nenhuma pasta selecionada. Pulando remocao")
    else:
        print(Style.BRIGHT + Fore.RED + "Invalido. Pulando remocao.")


# Instalando novo anydesk se o usuario quiser
import tkinter as tk
from tkinter import filedialog
import subprocess


def install_anydesk():
    choice = input(Style.BRIGHT + Fore.CYAN + "Voce deseja instalar uma nova versão do AnyDesk? (y = instalar, n = pular): ").strip().lower()

    if choice == 'y':
        print(Style.BRIGHT + Fore.GREEN + "Por favor, selecione o executavel do AnyDesk (.exe).")
        root = tk.Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        installer_path = filedialog.askopenfilename(
            title="Select AnyDesk Installer",
            filetypes=[("Executable files", "*.exe")],
        )

        if installer_path:
            print(f"Instalador Selecionado: {installer_path}")
            try:
                print(Style.BRIGHT + Fore.YELLOW + "Rodando o instalador...")
                subprocess.run(installer_path, check=True)
                print(Style.BRIGHT + Fore.GREEN + "Instalacao completa.")
                restore_user_conf_main()
            except subprocess.CalledProcessError as e:
                print(Style.BRIGHT + Fore.RED + f"Erro durante instalacao: {e}")
        else:
            print(Style.BRIGHT + Fore.RED + "Nenhuma pasta selecionada. Pulando instalacao.")

    elif choice == 'n':
        print(Style.BRIGHT + Fore.GREEN + "Pulando instalacao.")

    else:
        print(Style.BRIGHT + Fore.RED + "Escolha invalida. Pulando instalacao.")

# Restaurando backup de usuario user.conf
def restore_user_conf_main():
    backup_conf = os.path.expanduser("~/Desktop/user.conf.backup")
    user_conf = os.path.expandvars(r"%APPDATA%\AnyDesk\user.conf")

    if os.path.exists(backup_conf):
        print(Style.BRIGHT + Fore.GREEN + "Restaurando user.conf...")
        os.makedirs(os.path.dirname(user_conf), exist_ok=True)
        shutil.copy(backup_conf, user_conf)
    else:
          print(Style.BRIGHT + Fore.RED + "Backup user.conf não encontrado. Pulando restauracao.") # pq?

# Rodar AnyDesk se o usuario quiser
def run_anydesk():
    choice = input(Style.BRIGHT + Fore.CYAN + "Deseja iniciar o AnyDesk agora? (y = rodar, n = não rodar): ").strip().lower()

    if choice == 'y':
        anydesk_path = r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe"
        if os.path.exists(anydesk_path):
            print(Style.BRIGHT + Fore.GREEN + "Inicializando AnyDesk...")

            subprocess.Popen([anydesk_path])

            if check_anydesk_running():
                print(Style.BRIGHT + Fore.GREEN + "AnyDesk esta rodando.")
                return
            else:
                print(Style.BRIGHT + Fore.RED + "Falha ao iniciar AnyDesk.")
        else:
            print(Style.BRIGHT + Fore.RED + f"AnyDesk nao encontrado {anydesk_path}. Confirme se esta instalado.")

    elif choice == 'n':
        print(Style.BRIGHT + Fore.GREEN + "Nao rodando AnyDesk...")

    else:
        print(Style.BRIGHT + Fore.RED + "Escolha invalida. Pulando inicializacao")

def check_anydesk_running():
    try:
        result = subprocess.run("tasklist /fi \"imagename eq AnyDesk.exe\"", capture_output=True, text=True)
        if "AnyDesk.exe" in result.stdout:
            return True
        else:
            return False
    except subprocess.CalledProcessError as e:
        print(Style.BRIGHT + Fore.RED + f"Erro ao checar processo do AnyDesk {e}")
        return False

# Starting ID Changer module
def IDchangerQuestion():
    choice = input(Style.BRIGHT + Fore.CYAN + "Mudar o ID do AnyDesk? (y = Sim, n = Nao): ").strip().lower()

    if choice == 'y':
        print(Style.BRIGHT + Fore.GREEN + "Mudando o ID...")
        change_id()
    elif choice == 'n':
        print(Style.BRIGHT + Fore.GREEN + "Pulando mudanca de ID.")
    else:
        print(Style.BRIGHT + Fore.RED + "Escolha invalida. Pulando mudanca de ID.")

#ASCII logo
anydesk_text = pyfiglet.figlet_format("AnyDesk", font="slant")
reset_text = pyfiglet.figlet_format("reset", font="slant")

anydesk_colored = Fore.RED + anydesk_text + Style.RESET_ALL
reset_colored = Fore.CYAN + reset_text + Style.RESET_ALL

def main_cleanup():
    backup_user_conf_main()
    Killing_AnyDesk()
    remove_anydesk()
    restore_user_conf_main()
    install_anydesk()
    IDchangerQuestion()
    run_anydesk()
    print(Style.BRIGHT + Fore.LIGHTGREEN_EX + "Concluido!")

if __name__ == "__main__":
    while True:
        print(anydesk_colored)
        print(reset_colored)
        print(Style.BRIGHT + Fore.LIGHTWHITE_EX + "Feito por spiro-m4th")
        print(Fore.LIGHTWHITE_EX + "GitHub: https://github.com/spiro-m4th")
        print(Style.BRIGHT + Fore.CYAN + "\nSelecione uma Acao:")
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + "1. Limpeza total")
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + "2. Mudar o ID do AnyDesk")
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + "3. Backup/ Restauracao de user.conf")
        print(Style.BRIGHT + Fore.LIGHTRED_EX + "4. Sair")

        choice = input(Style.BRIGHT + Fore.CYAN + "Digite sua Escolha (1, 2, 3, ou 4): ").strip()

        if choice == '1':
            print(Style.BRIGHT + Fore.GREEN + "Iniciando ferramenta de limpeza...")
            main_cleanup()
        elif choice == '2':
            print(Style.BRIGHT + Fore.GREEN + "Iniciando ferramenta de mudanca de ID...")
            Killing_AnyDesk()
            change_id()
        elif choice == '3':
            print(Style.BRIGHT + Fore.GREEN + "Rodando Backup...")
            restore_user_conf_interactive()
            run_anydesk()
        elif choice == '4':
            print(Style.BRIGHT + Fore.GREEN + "Fechando o Programa.")
            break
        else:
            print(Style.BRIGHT + Fore.RED + "Escolha invalida. Tente novamente.")