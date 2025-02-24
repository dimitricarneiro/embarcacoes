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
    Valida se o CPF informado é válido.
    
    O CPF deve conter 11 dígitos e não pode ser uma sequência com todos os dígitos iguais.
    São calculados os dois dígitos verificadores conforme o algoritmo padrão.
    
    Parâmetros:
        cpf (str): CPF a ser validado, com ou sem formatação.
        
    Retorna:
        bool: True se o CPF for válido, False caso contrário.
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)
    
    # Verifica se o CPF possui 11 dígitos ou se é composto por números repetidos
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calcular_digito(cpf, tamanho, peso_inicial):
        """
        Calcula um dígito verificador do CPF.
        
        Parâmetros:
            cpf (str): CPF sem formatação.
            tamanho (int): Quantidade de dígitos a serem considerados para o cálculo.
            peso_inicial (int): Valor do peso inicial para a multiplicação.
            
        Retorna:
            int: Dígito verificador calculado.
        """
        soma = sum(int(cpf[i]) * (peso_inicial - i) for i in range(tamanho))
        resto = (soma * 10) % 11
        # Se o resto for 10 ou 11, considera-se 0
        return resto if resto < 10 else 0

    # Calcula o primeiro dígito verificador utilizando os 9 primeiros dígitos
    primeiro_digito = calcular_digito(cpf, 9, 10)
    # Calcula o segundo dígito verificador utilizando os 9 primeiros dígitos + o primeiro dígito verificador
    segundo_digito = calcular_digito(cpf, 10, 11)
    
    # Verifica se os dígitos calculados conferem com os dígitos informados
    if int(cpf[9]) != primeiro_digito or int(cpf[10]) != segundo_digito:
        return False

    return True