import re

def validar_cnpj(cnpj):
    """Valida se o CNPJ informado é válido."""
    cnpj = re.sub(r'\D', '', cnpj)  # Remove caracteres não numéricos

    if len(cnpj) != 14 or cnpj in (c * 14 for c in "0123456789"):
        return False

    def calcular_digito(cnpj, pesos):
        soma = sum(int(cnpj[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1

    if int(cnpj[12]) != calcular_digito(cnpj[:12], pesos1):
        return False
    if int(cnpj[13]) != calcular_digito(cnpj[:13], pesos2):
        return False

    return True

def validar_cpf(cpf):
    """
    Valida o CPF removendo caracteres não numéricos, verificando o tamanho,
    checando se não são todos dígitos iguais e calculando os dígitos verificadores.

    Args:
        cpf (str): CPF a ser validado.

    Returns:
        bool: True se o CPF for válido, False caso contrário.
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)

    # CPF deve ter 11 dígitos
    if len(cpf) != 11:
        return False

    # Verifica se todos os dígitos são iguais (ex.: 11111111111)
    if cpf == cpf[0] * 11:
        return False

    # Cálculo do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = 11 - (soma % 11)
    if digito1 >= 10:
        digito1 = 0

    # Cálculo do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = 11 - (soma % 11)
    if digito2 >= 10:
        digito2 = 0

    # Verifica se os dígitos calculados batem com os dígitos informados
    return cpf[-2:] == f"{digito1}{digito2}"