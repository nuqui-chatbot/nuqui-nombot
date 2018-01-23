import re


def request_has_param(request, property):
    return True if request.query_params.get(property) else False


def request_get_param(request, property):
    return request.query_params.get(property)


def extract_numbers(string):
    non_decimal = re.compile(r'[^\d.]+')
    numbers = non_decimal.sub(' ', string).split(' ')
    return [float(number) for number in numbers if number != '' and number != '.']

