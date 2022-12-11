import re
from itertools import cycle

from django.core.exceptions import ValidationError


def validate_cpf(cpf: str) -> str:
    """ Efetua a validação do CPF usando dígito verificadores.

    Parâmetros:
        cpf (str): CPF a ser validado

    Retorno:
        bool:
            - Falso, quando o CPF não possuir o formato 999.999.999-99;
            - Falso, quando o CPF não possuir 11 caracteres numéricos;
            - Falso, quando os dígitos verificadores forem inválidos;
            - Verdadeiro, caso contrário.

    Exemplos:

    >>> validate_cpf('529.982.247-25')
    True
    >>> validate_cpf('52998224725')
    True
    >>> validate_cpf('111.111.111-11')
    False
    """

    # # Verifica a formatação do CPF
    # if not re.match(r'\d{3}\.\d{3}\.\d{3}-\d{2}', cpf):
    #     return False

    # Obtém apenas os números do CPF, ignorando pontuações
    numbers = [int(digit) for digit in cpf if digit.isdigit()]

    # Verifica se o CPF possui 11 números ou se todos são iguais:
    if len(numbers) != 11:
        raise ValidationError('CPF deve possuir 11 digitos numéricos.')

    if len(set(numbers)) == 1:
        raise ValidationError('CPF não pode possuir todos os digitos iguais.')

    # Validação do primeiro dígito verificador:
    sum_of_products = sum(a * b for a, b in zip(numbers[0:9], range(10, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[9] != expected_digit:
        raise ValidationError('CPF inválido.')

    # Validação do segundo dígito verificador:
    sum_of_products = sum(a * b for a, b in zip(numbers[0:10], range(11, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[10] != expected_digit:
        raise ValidationError('CPF inválido.')

    return cpf


def validate_cnpj(cnpj: str) -> str:
    """ Efetua a validação do CNPJ.

    Parâmetros:
        cnpj (str): cnpj a ser validado

    Retorno:
        bool:
            - Falso, quando o CNPJ não possuir 14 caracteres numéricos;
            - Falso, quando os dígitos verificadores forem inválidos;
            - Verdadeiro, caso contrário.

    Exemplos:

    >>> validate_cnpj('12345678901234')
    False
    >>> validate_cnpj("0" * 14)
    False
    >>> validate_cnpj('77437514000133')
    True
    """

    # # Verifica a formatação do CPF
    # if not re.match(r'\d{3}\.\d{3}\.\d{3}-\d{2}', cpf):
    #     return False
    # Obtém apenas os números do CPF, ignorando pontuações
    numbers = [int(digit) for digit in cnpj if digit.isdigit()]

    # Verifica se o CPF possui 14 números ou se todos são iguais:
    if len(numbers) != 14:
        raise ValidationError('CPNJ deve possuir 14 digitos numéricos.')

    if len(set(numbers)) == 1:
        raise ValidationError('CPNJ não pode possuir todos os digitos iguais.')

    cnpj_r = cnpj[::-1]
    for i in range(2, 0, -1):
        cnpj_enum = zip(cycle(range(2, 10)), cnpj_r[i:])
        dv = sum(map(lambda x: int(x[1]) * x[0], cnpj_enum)) * 10 % 11
        if cnpj_r[i - 1:i] != str(dv % 10):
            raise ValidationError('CNPJ inválido.')

    return cnpj
