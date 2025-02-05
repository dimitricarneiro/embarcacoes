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
