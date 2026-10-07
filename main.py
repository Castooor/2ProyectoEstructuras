from ArbolDirectorios import ArbolDirectorios
from auditoria import Auditoria


def main():
    auditoria = Auditoria()

    print("========================================")
    print(" SISTEMA DE ARCHIVOS DISTRIBUIDO")
    print("========================================")

    arbol = ArbolDirectorios()

    print("\nSistema iniciado correctamente.")
    print("Arbol de directorios: OK")
    print("Auditoria: OK")


if __name__ == "__main__":
    main()