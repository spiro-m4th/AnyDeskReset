import os
import sys
import logging
from colorama import init, Fore, Style

# Inicializa o colorama
init(autoreset=True)
logger = logging.getLogger(__name__)


def change_id():
    """
    Tenta deletar o arquivo service.conf para resetar o ID do AnyDesk.
    Requer privilégios de administrador.
    """
    # O arquivo de configuração do serviço geralmente fica em C:\ProgramData\AnyDesk\service.conf
    service_conf_path = os.path.expandvars(r"%ALLUSERSPROFILE%\AnyDesk\service.conf")
    service_conf_filename = os.path.basename(service_conf_path)

    print(Style.BRIGHT + Fore.CYAN + f"Tentando remover o arquivo de ID: {Fore.YELLOW}{service_conf_path}")
    logger.info(f"Tentativa de remoção do arquivo {service_conf_path} para troca de ID.")

    if os.path.exists(service_conf_path):
        try:
            os.remove(service_conf_path)
            print(
                Style.BRIGHT + Fore.GREEN + f"Sucesso: O arquivo '{Fore.YELLOW}{service_conf_filename}{Style.BRIGHT + Fore.GREEN}' foi deletado.")
            print(
                Style.BRIGHT + Fore.YELLOW + "O AnyDesk deve gerar um novo ID na próxima vez que for iniciado (certifique-se de ter fechado ele totalmente).")
            logger.info(f"Arquivo {service_conf_filename} removido com sucesso.")
            return True  # Sucesso
        except PermissionError:
            print(Style.BRIGHT + Fore.RED + f"Erro de Permissão: Não foi possível deletar '{service_conf_path}'.")
            print(
                Style.BRIGHT + Fore.YELLOW + "Dica: Execute este script como Administrador para conseguir trocar o ID.")
            logger.error(f"Erro de permissão ao deletar {service_conf_filename}.")
            return False
        except OSError as e:
            print(Style.BRIGHT + Fore.RED + f"Erro de sistema ao deletar '{service_conf_filename}': {e.strerror}")
            logger.error(f"Erro de sistema ao deletar {service_conf_filename}: {e}", exc_info=False)
            return False
        except Exception as e:
            print(Style.BRIGHT + Fore.RED + f"Erro inesperado: {e}", file=sys.stderr)
            logger.exception(f"Erro inesperado ao deletar {service_conf_filename}: {e}")
            return False
    else:
        print(Style.BRIGHT + Fore.YELLOW + f"O arquivo '{service_conf_path}' não foi encontrado.")
        print(
            Style.BRIGHT + Fore.YELLOW + "Isso geralmente significa que o ID já foi resetado ou o AnyDesk nunca foi instalado/aberto nesta máquina.")
        logger.info(f"Arquivo {service_conf_filename} não existe, nada a fazer.")
        return True


# --- Ponto de entrada para testes (Modo Standalone) ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger.info("Iniciando id_changer em modo teste.")

    print(Style.BRIGHT + Fore.MAGENTA + "--- Alterador de ID AnyDesk (Modo Teste PT-BR) ---")
    change_id()
    if sys.stdin.isatty():
        input("Pressione Enter para sair...")