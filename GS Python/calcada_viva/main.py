import sys

import integrantes
import interface
import persistencia


def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else persistencia.ARQUIVO_PADRAO
    dados, aviso = persistencia.carregar(caminho)
    integrantes.exibir_banner()
    if aviso:
        print(f"\n  ! {aviso}")
    try:
        interface.menu_principal(dados, caminho)
    except (KeyboardInterrupt, EOFError):
        print("\n\n  Programa encerrado. Os dados já registrados ficaram salvos.")


if __name__ == "__main__":
    main()
