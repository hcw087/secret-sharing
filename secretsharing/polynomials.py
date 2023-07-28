from utilitybelt import secure_randint as randint


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def mod_inverse(k, prime):
    k = k % prime
    if k < 0:
        r = egcd(prime, -k)[2]
    else:
        r = egcd(prime, k)[2]
    return (prime + r) % prime


def random_polynomial(degree, intercept, upper_bound):
    if degree < 0:
        raise ValueError('Degree must be a non-negative number.')
    coefficients = [intercept]
    for i in range(degree):
        random_coeff = randint(0, upper_bound-1)
        coefficients.append(random_coeff)
    return coefficients


def get_polynomial_points(coefficients, num_points, prime):
    points = []
    for x in range(1, num_points+1):
        y = coefficients[0]
        for i in range(1, len(coefficients)):
            exponentiation = (x**i) % prime
            term = (coefficients[i] * exponentiation) % prime
            y = (y + term) % prime
        points.append((x, y))
    return points


def modular_lagrange_interpolation(x, points, prime):
    x_values, y_values = zip(*points)
    f_x = 0
    for i in range(len(points)):
        numerator, denominator = 1, 1
        for j in range(len(points)):
            if i == j:
                continue
            numerator = (numerator * (x - x_values[j])) % prime
            denominator = (denominator * (x_values[i] - x_values[j])) % prime
        lagrange_polynomial = numerator * mod_inverse(denominator, prime)
        f_x = (prime + f_x + (y_values[i] * lagrange_polynomial)) % prime
    return f_x
