import sympy

from typing import Dict
from polyvar import PolyVar


class PolyMoment:
    def __init__(self, poly: str, x: str, dist: Dict):
        # TODO: iron out poly and x type
        self.x = sympy.symbols(x)
        self.poly = sympy.poly(eval(poly.replace('x', 'self.x')))
        self.dist = {k: PolyVar(**v) for k, v in dist.items()}

    def __call__(self, *args, **kwargs):
        return self.get_moments(*args, **kwargs)

    def get_moments(self, order: int):
        # expand polynomial for moment order
        p = self.poly ** order

        # coefficients and monomials
        coeffs = p.coeffs()
        monoms = p.monoms()

        for monom in monoms:
            for m_index, m in enumerate(monom):
                # check the feasibility of analytic expansion
                if (m < 0 or m % 1 != 0) and self.dist.get(f'x{m_index}').translation != 0.0:
                    raise Exception('No known finite expression for this type of distribution')

        return self.dist


if __name__ == '__main__':
    polymoment = PolyMoment(
        poly='x[0]+2*x[1]-x[2]',
        x='x0,x1,x2',
        dist={
            'x0': {
                'distribution': 'normal',
                'type': 'symmetrical',
                'translation': 0,
                'scale': 0,
            },
            'x1': {
                'distribution': 'normal',
                'type': 'symmetrical',
                'translation': 0,
                'scale': 0,
            },
            'x2': {
                'distribution': 'normal',
                'type': 'symmetrical',
                'translation': 0,
                'scale': 0,
            }
        }
    )

    print(
        polymoment.get_moments(order=2)
    )
