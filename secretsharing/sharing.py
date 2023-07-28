import string
from six import integer_types
from utilitybelt import int_to_charset, charset_to_int, base58_chars, base32_chars, zbase32_chars
from .primes import get_large_enough_prime
from .polynomials import random_polynomial, get_polynomial_points, modular_lagrange_interpolation

def secret_int_to_points(secret_int, point_threshold, num_points, prime=None):
    if point_threshold < 2:
        raise ValueError("Threshold must be >= 2.")
    if point_threshold > num_points:
        raise ValueError("Threshold must be < the total number of points.")
    if not prime:
        prime = get_large_enough_prime([secret_int, num_points])
    if not prime:
        raise ValueError("Error! Secret is too long for share calculation!")
    coefficients = random_polynomial(point_threshold-1, secret_int, prime)
    points = get_polynomial_points(coefficients, num_points, prime)
    return points

def points_to_secret_int(points, prime=None):
    if not isinstance(points, list):
        raise ValueError("Points must be in list form.")
    for point in points:
        if not isinstance(point, tuple) and len(point) == 2:
            raise ValueError("Each point must be a tuple of two values.")
        if not (isinstance(point[0], integer_types) and isinstance(point[1], integer_types)):
            raise ValueError("Each value in the point must be an int.")
    x_values, y_values = zip(*points)
    if not prime:
        prime = get_large_enough_prime(y_values)
    free_coefficient = modular_lagrange_interpolation(0, points, prime)
    secret_int = free_coefficient
    return secret_int

def point_to_share_string(point, charset):
    if '-' in charset:
        raise ValueError('The character "-" cannot be in the supplied charset.')
    if not (isinstance(point, tuple) and len(point) == 2 and isinstance(point[0], integer_types) and isinstance(point[1], integer_types)):
        raise ValueError('Point format is invalid. Must be a pair of integers.')
    x, y = point
    x_string = int_to_charset(x, charset)
    y_string = int_to_charset(y, charset)
    share_string = x_string + '-' + y_string
    return share_string

def share_string_to_point(share_string, charset):
    if '-' in charset:
        raise ValueError('The character "-" cannot be in the supplied charset.')
    if not isinstance(share_string, str) and share_string.count('-') == 1:
        raise ValueError('Share format is invalid.')
    x_string, y_string = share_string.split('-')
    if (set(x_string) - set(charset)) or (set(y_string) - set(charset)):
        raise ValueError("Share has characters that aren't in the charset.")
    x = charset_to_int(x_string, charset)
    y = charset_to_int(y_string, charset)
    return (x, y)

class SecretSharer():
    secret_charset = string.hexdigits[0:16]
    share_charset = string.hexdigits[0:16]

    def __init__(self):
        pass

    @classmethod
    def split_secret(cls, secret_string, share_threshold, num_shares):
        secret_int = charset_to_int(secret_string, cls.secret_charset)
        points = secret_int_to_points(secret_int, share_threshold, num_shares)
        shares = []
        for point in points:
            shares.append(point_to_share_string(point, cls.share_charset))
        return shares

    @classmethod
    def recover_secret(cls, shares):
        points = []
        for share in shares:
            points.append(share_string_to_point(share, cls.share_charset))
        secret_int = points_to_secret_int(points)
        secret_string = int_to_charset(secret_int, cls.secret_charset)
        return secret_string

class HexToHexSecretSharer(SecretSharer):
    secret_charset = string.hexdigits[0:16]
    share_charset = string.hexdigits[0:16]

class PlaintextToHexSecretSharer(SecretSharer):
    secret_charset = string.printable
    share_charset = string.hexdigits[0:16]

class BitcoinToB58SecretSharer(SecretSharer):
    secret_charset = base58_chars
    share_charset = base58_chars

class BitcoinToB32SecretSharer(SecretSharer):
    secret_charset = base58_chars
    share_charset = base32_chars

class BitcoinToZB32SecretSharer(SecretSharer):
    secret_charset = base58_chars
    share_charset = zbase32_chars
