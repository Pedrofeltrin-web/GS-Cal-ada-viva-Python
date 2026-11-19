def ler_texto(prompt, minimo=1, maximo=120, obrigatorio=True):
    while True:
        valor = input(prompt).strip()
        if not valor:
            if not obrigatorio:
                return ""
            print("  Campo obrigatório. Tente novamente.")
            continue
        if len(valor) < minimo:
            print(f"  Digite pelo menos {minimo} caracteres.")
            continue
        if len(valor) > maximo:
            print(f"  Máximo de {maximo} caracteres (você digitou {len(valor)}).")
            continue
        return valor


def ler_inteiro(prompt, minimo=None, maximo=None, obrigatorio=True):
    while True:
        bruto = input(prompt).strip()
        if not bruto:
            if not obrigatorio:
                return None
            print("  Campo obrigatório. Tente novamente.")
            continue
        try:
            numero = int(bruto)
        except ValueError:
            print("  Digite um número inteiro válido.")
            continue
        if minimo is not None and numero < minimo:
            print(f"  O valor mínimo é {minimo}.")
            continue
        if maximo is not None and numero > maximo:
            print(f"  O valor máximo é {maximo}.")
            continue
        return numero


def ler_decimal(prompt, minimo=None, maximo=None, obrigatorio=True):
    while True:
        bruto = input(prompt).strip().replace(",", ".")
        if not bruto:
            if not obrigatorio:
                return None
            print("  Campo obrigatório. Tente novamente.")
            continue
        try:
            numero = float(bruto)
        except ValueError:
            print("  Digite um número válido (ex.: 25 ou 25,5).")
            continue
        if numero != numero or numero in (float("inf"), float("-inf")):
            print("  Valor inválido.")
            continue
        if minimo is not None and numero < minimo:
            print(f"  O valor mínimo é {minimo}.")
            continue
        if maximo is not None and numero > maximo:
            print(f"  O valor máximo é {maximo}.")
            continue
        return numero


def ler_opcao(prompt, validas):
    validas_norm = [str(o).lower() for o in validas]
    while True:
        valor = input(prompt).strip().lower()
        if valor in validas_norm:
            return valor
        print("  Opção inválida. Opções: " + ", ".join(str(o) for o in validas))


def confirmar(prompt):
    return ler_opcao(prompt + " (s/n): ", ["s", "n"]) == "s"
