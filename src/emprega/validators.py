import re
from itertools import cycle

from django.core.exceptions import ValidationError


def validate_cpf(cpf: str) -> str:
    """Efetua a validação do CPF usando dígito verificadores.

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
    Raises ValidationError
    >>> validate_cpf('52998224725')
    '52998224725'
    >>> validate_cpf('111.111.111-11')
    Raises ValidationError
    """

    # # Verifica a formatação do CPF
    # if not re.match(r'\d{3}\.\d{3}\.\d{3}-\d{2}', cpf):
    #     return False

    # Obtém apenas os números do CPF, ignorando pontuações

    if not cpf.isdigit():
        raise ValidationError("CNPJ deve possuir apenas números.")

    numbers = [int(digit) for digit in cpf if digit.isdigit()]

    # Verifica se o CPF possui 11 números ou se todos são iguais:
    if len(numbers) != 11:
        raise ValidationError("CPF deve possuir 11 digitos numéricos.")

    if len(set(numbers)) == 1:
        raise ValidationError("CPF não pode possuir todos os digitos iguais.")

    # Validação do primeiro dígito verificador:
    sum_of_products = sum(a * b for a, b in zip(numbers[0:9], range(10, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[9] != expected_digit:
        raise ValidationError("CPF inválido.")

    # Validação do segundo dígito verificador:
    sum_of_products = sum(a * b for a, b in zip(numbers[0:10], range(11, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[10] != expected_digit:
        raise ValidationError("CPF inválido.")

    return cpf


def validate_cnpj(cnpj: str) -> str:
    """Efetua a validação do CNPJ.

    Parâmetros:
        cnpj (str): cnpj a ser validado

    Retorno:
        bool:
            - Falso, quando o CNPJ não possuir 14 caracteres numéricos;
            - Falso, quando os dígitos verificadores forem inválidos;
            - Verdadeiro, caso contrário.

    Exemplos:

    >>> validate_cnpj('85059325000100')
    '85059325000100'
    >>> validate_cnpj("0" * 14)
    Raises ValidationError
    >>> validate_cnpj('77437514000133')
    '77437514000133'
    """

    cnpj = "".join(re.findall("\d", cnpj))

    if not cnpj.isdigit():
        raise ValidationError("CNPJ deve possuir apenas números.")

    if len(cnpj) != 14:
        raise ValidationError("CNPJ deve possuir 14 digitos numéricos.")

    if cnpj in [
        "00000000000000",
        "11111111111111",
        "22222222222222",
        "33333333333333",
        "44444444444444",
        "55555555555555",
        "66666666666666",
        "77777777777777",
        "88888888888888",
        "99999999999999",
    ]:
        raise ValidationError("CNPJ não pode possuir todos os digitos iguais.")

    # Validação do primeiro dígito verificador
    soma = 0
    peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    for i in range(12):
        soma += int(cnpj[i]) * peso[i]

    digito = 11 - (soma % 11)
    if digito > 9:
        digito = 0
    if int(cnpj[12]) != digito:
        raise ValidationError("CNPJ inválido.")

    # Validação do segundo dígito verificador
    soma = 0
    peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    for i in range(13):
        soma += int(cnpj[i]) * peso[i]

    digito = 11 - (soma % 11)
    if digito > 9:
        digito = 0
    if int(cnpj[13]) != digito:
        raise ValidationError("CNPJ inválido.")

    return cnpj
