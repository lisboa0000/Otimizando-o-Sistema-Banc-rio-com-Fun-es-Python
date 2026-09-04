"""Sistema bancário em terminal.

A camada de regras de negócio é mantida em funções pequenas e reutilizáveis,
enquanto o menu fica concentrado em ``main``. Os valores monetários usam
Decimal para evitar erros de arredondamento de ponto flutuante.
"""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

AGENCIA = "0001"
LIMITE_SAQUES = 3
LIMITE_VALOR_SAQUE = Decimal("500.00")
DUAS_CASAS = Decimal("0.01")

# Mantidos no módulo para preservar a simplicidade do desafio original.
usuarios = []
contas = {}
proximo_numero_conta = 1


def _dinheiro(valor):
    """Converte um valor numérico/textual em Decimal com duas casas."""
    try:
        if isinstance(valor, str):
            valor = valor.strip().replace("R$", "").replace(" ", "")
            # Aceita tanto 1234.56 quanto 1.234,56.
            if "," in valor:
                valor = valor.replace(".", "").replace(",", ".")
        return Decimal(str(valor)).quantize(DUAS_CASAS, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        return None


def _formatar_dinheiro(valor):
    valor = _dinheiro(valor) or Decimal("0.00")
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _normalizar_cpf(cpf):
    return "".join(str(cpf).split()).replace(".", "").replace("-", "")


def depositar(saldo, valor, extrato, /):
    """Realiza um depósito válido e retorna saldo e extrato atualizados."""
    saldo_decimal = _dinheiro(saldo)
    valor_decimal = _dinheiro(valor)
    if saldo_decimal is None or valor_decimal is None or valor_decimal <= 0:
        print("Valor inválido para depósito. Informe um valor positivo.")
        return saldo, extrato

    saldo_decimal += valor_decimal
    extrato += f"Depósito:\t{_formatar_dinheiro(valor_decimal)}\n"
    print("Depósito realizado com sucesso!")
    return saldo_decimal, extrato


def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    """Realiza saque aplicando saldo, limite por operação e limite diário."""
    saldo_decimal = _dinheiro(saldo)
    valor_decimal = _dinheiro(valor)
    limite_decimal = _dinheiro(limite)

    if valor_decimal is None or valor_decimal <= 0:
        print("Valor inválido para saque. Informe um valor positivo.")
    elif saldo_decimal is None or valor_decimal > saldo_decimal:
        print("Operação falhou! Saldo insuficiente.")
    elif limite_decimal is None or valor_decimal > limite_decimal:
        print(f"Operação falhou! Limite máximo de {_formatar_dinheiro(limite)} por saque.")
    elif numero_saques >= limite_saques:
        print(f"Operação falhou! Número máximo de {limite_saques} saques diários atingido.")
    else:
        saldo_decimal -= valor_decimal
        extrato += f"Saque:\t\t{_formatar_dinheiro(valor_decimal)}\n"
        numero_saques += 1
        print("Saque realizado com sucesso!")

    return saldo_decimal if saldo_decimal is not None else saldo, extrato, numero_saques


def exibir_extrato(saldo, /, *, extrato):
    """Exibe o histórico de movimentações e o saldo atual."""
    print(" EXTRATO ".center(40, "="))
    print(extrato if extrato else "Não foram realizadas movimentações.")
    print(f"Saldo:\t\t{_formatar_dinheiro(saldo)}")
    print("=" * 40)


def _buscar_usuario(cpf, usuarios):
    cpf = _normalizar_cpf(cpf)
    return next((usuario for usuario in usuarios if usuario["cpf"] == cpf), None)


def _validar_data_nascimento(valor):
    try:
        data = datetime.strptime(valor.strip(), "%d/%m/%Y")
        return data.strftime("%d/%m/%Y")
    except ValueError:
        return None


def criar_usuario(usuarios):
    """Cadastra usuário com CPF e data de nascimento validados."""
    cpf = _normalizar_cpf(input("CPF (somente números): "))
    if len(cpf) != 11 or not cpf.isdigit():
        print("CPF inválido. Informe 11 números.")
        return False
    if _buscar_usuario(cpf, usuarios):
        print("CPF já cadastrado!")
        return False

    nome = input("Nome completo: ").strip()
    data_nascimento = _validar_data_nascimento(input("Data de nascimento (dd/mm/aaaa): "))
    if not nome or not data_nascimento:
        print("Nome e data de nascimento são obrigatórios; data deve estar em dd/mm/aaaa.")
        return False

    logradouro = input("Logradouro: ").strip()
    nro = input("Número: ").strip()
    bairro = input("Bairro: ").strip()
    cidade = input("Cidade: ").strip()
    sigla_estado = input("Sigla do estado (UF): ").strip().upper()
    if not all((logradouro, nro, bairro, cidade)) or len(sigla_estado) != 2:
        print("Endereço inválido. Preencha todos os campos corretamente.")
        return False

    usuarios.append({
        "nome": " ".join(nome.title().split()),
        "data_nascimento": data_nascimento,
        "cpf": cpf,
        "endereco": f"{logradouro}, {nro} - {bairro} - {cidade}/{sigla_estado}",
    })
    print("Usuário cadastrado com sucesso!")
    return True


def criar_conta(agencia, numero_conta, usuarios, contas):
    """Cria uma conta para CPF existente e retorna True quando criada."""
    cpf = _normalizar_cpf(input("CPF do titular: "))
    usuario = _buscar_usuario(cpf, usuarios)
    if not usuario:
        print("Usuário não encontrado. Cadastre o usuário primeiro.")
        return False

    contas[numero_conta] = {
        "agencia": agencia, "numero_conta": numero_conta, "cpf": cpf,
        "saldo": Decimal("0.00"), "extrato": "",
        "numero_saques_hoje": 0, "ultima_data_saque": None,
    }
    print(f"Conta criada com sucesso! Agência {agencia} | Conta {numero_conta} | Titular: {usuario['nome']}")
    return True


def listar_contas(contas, usuarios=None):
    """Lista contas; usa índice por CPF quando fornecido para evitar buscas repetidas."""
    usuarios = usuarios if usuarios is not None else globals()["usuarios"]
    nomes = {usuario["cpf"]: usuario["nome"] for usuario in usuarios}
    if not contas:
        print("Nenhuma conta cadastrada.")
        return
    for numero, dados in contas.items():
        print(f"Agência:\t{dados['agencia']}")
        print(f"C/C:\t\t{numero}")
        print(f"Titular:\t{nomes.get(dados['cpf'], 'Desconhecido')}")
        print("=" * 40)


def obter_conta(contas):
    """Solicita número da conta, tratando entradas inválidas."""
    try:
        numero = int(input("Número da conta: ").strip())
    except (ValueError, EOFError):
        print("Número inválido.")
        return None
    conta = contas.get(numero)
    if conta is None:
        print("Conta não encontrada.")
    return conta


def menu():
    print("\n=========== MENU ==============")
    print("[d]\tDepositar\n[s]\tSacar\n[e]\tExtrato\n[nc]\tNova conta")
    print("[lc]\tListar contas\n[nu]\tNovo usuário\n[q]\tSair")
    return input("=> ").strip().lower()


def _ler_valor(mensagem):
    valor = _dinheiro(input(mensagem))
    if valor is None:
        print("Valor inválido.")
    return valor


def main():
    global proximo_numero_conta
    while True:
        try:
            opcao = menu()
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo do sistema...")
            break

        if opcao == "d":
            conta = obter_conta(contas)
            if conta:
                valor = _ler_valor("Valor do depósito: R$ ")
                if valor is not None:
                    conta["saldo"], conta["extrato"] = depositar(conta["saldo"], valor, conta["extrato"])
        elif opcao == "s":
            conta = obter_conta(contas)
            if conta:
                valor = _ler_valor("Valor do saque: R$ ")
                if valor is not None:
                    hoje = date.today()
                    if conta["ultima_data_saque"] != hoje:
                        conta["numero_saques_hoje"] = 0
                        conta["ultima_data_saque"] = hoje
                    conta["saldo"], conta["extrato"], conta["numero_saques_hoje"] = sacar(
                        saldo=conta["saldo"], valor=valor, extrato=conta["extrato"],
                        limite=LIMITE_VALOR_SAQUE, numero_saques=conta["numero_saques_hoje"],
                        limite_saques=LIMITE_SAQUES)
        elif opcao == "e":
            conta = obter_conta(contas)
            if conta:
                exibir_extrato(conta["saldo"], extrato=conta["extrato"])
        elif opcao == "nc":
            if criar_conta(AGENCIA, proximo_numero_conta, usuarios, contas):
                proximo_numero_conta += 1
        elif opcao == "lc":
            listar_contas(contas, usuarios)
        elif opcao == "nu":
            criar_usuario(usuarios)
        elif opcao == "q":
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
