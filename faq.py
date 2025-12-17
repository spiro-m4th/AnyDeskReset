import sys
from colorama import init, Fore, Style

# Inicializa o colorama para cores no terminal
init(autoreset=True)


def display_faq():
    """Exibe as Perguntas Frequentes (FAQ) em Português."""

    # Conteúdo das Perguntas e Respostas
    faq_data = [
        (
            "P: O que é este script e para que serve?",
            "R: Este script é uma coleção de utilitários para gerenciar o AnyDesk no Windows. Ele começou como uma ferramenta para resetar o ID do AnyDesk (geralmente necessário após expiração da licença ou clonagem de máquinas) deletando arquivos de configuração específicos. Hoje ele inclui funções de backup, restauração e limpeza de cache."
        ),
        (
            "P: Por que preciso executar como Administrador?",
            "R: Para que o script funcione corretamente (especialmente a troca de ID e limpeza profunda), ele precisa parar o Serviço do Windows do AnyDesk e deletar arquivos em pastas protegidas do sistema (ProgramData). Sem permissão de admin, essas ações falham."
        ),
        (
            "P: Como funciona a troca de ID (Reset ID)?",
            "R: O AnyDesk gera seu ID baseado no arquivo 'service.conf'. O script força a parada do AnyDesk e deleta este arquivo. Na próxima vez que o AnyDesk abrir, ele será forçado a gerar um novo arquivo e, consequentemente, um novo ID."
        ),
        (
            "P: O que é salvo no Backup?",
            "R: O backup principal salva o arquivo 'user.conf'. É nele que ficam seus favoritos, histórico de conexões recentes e configurações de apelido/imagem. O script também tem uma opção separada para salvar as gravações de tela (.any)."
        ),
        (
            "P: Onde os backups são salvos?",
            "R: Por padrão, o script tenta salvar na sua Área de Trabalho (Desktop) ou na pasta onde o script está rodando. Você pode alterar esse local no menu de configurações de Backup."
        ),
        (
            "P: Existe algum risco ao usar a 'Limpeza' ou 'Troca de ID'?",
            "R: O risco técnico é baixo, mas você perderá o histórico de conexões e configurações de acesso não supervisionado (senha de acesso) se deletar os arquivos de configuração. Recomenda-se sempre fazer um backup do 'user.conf' antes de realizar limpezas profundas."
        )
    ]

    print("\n" + Style.BRIGHT + Fore.MAGENTA + "=" * 70)
    print(Style.BRIGHT + Fore.CYAN + "--- Perguntas Frequentes (FAQ) ---")
    print(Style.BRIGHT + Fore.MAGENTA + "=" * 70)

    for question, answer in faq_data:
        print(Style.BRIGHT + Fore.YELLOW + question)
        print(Fore.WHITE + answer)
        print("-" * 60)  # Separador entre perguntas

    print(Style.BRIGHT + Fore.MAGENTA + "=" * 70)


# --- Bloco para teste isolado do arquivo ---
if __name__ == "__main__":
    display_faq()
    if sys.stdin.isatty():
        input("Pressione Enter para sair...")