import sympy

from functools import lru_cache
from typing import Dict
from polyvar import PolyVar


class PolyMoment:
    def __init__(self, poly: str, x: str, dist: Dict):
        for key in x.replace(' ', '').split(','):
            self.__dict__[key] = sympy.symbols(key)
        self.poly = sympy.poly(eval(poly.replace('x', 'self.x')))
        self.dist = {k: PolyVar(**v) for k, v in dist.items()}

        # convert translations, scales, betas, and weights to type symbol if provided in string
        for k, v in self.dist.items():
            if isinstance(v.translation, str):
                v.translation = sympy.symbols(v.translation)
            if isinstance(v.scale, str):
                v.scale = sympy.symbols(v.scale)
            if v.beta1 and isinstance(v.beta1, str):
                v.beta1 = sympy.symbols(v.beta1)
            if v.beta2 and isinstance(v.beta2, str):
                v.beta2 = sympy.symbols(v.beta2)

    def __call__(self, *args, **kwargs):
        return self.moment(*args, **kwargs)

    def std(self):
        std = sympy.sqrt(self.variance())
        return sympy.simplify(std)

    def variance(self):
        var = self.moment(order=2) - (self.moment(order=1) ** 2)
        return sympy.simplify(var)

    def mean(self):
        mu = self.moment(order=1)
        return sympy.simplify(mu)

    def moment(self, order: int):
        # expand polynomial for moment order
        p = self.poly ** order

        # coefficients and monomials
        gens = p.gens
        coeffs = p.coeffs()
        monoms = p.monoms()

        eval_monoms = []
        for monom in monoms:
            eval_monom_temp = []
            for m_index, m in enumerate(monom):
                # continue if m is 0; The convention E[V^0] = 1 is adopted here
                if m == 0:
                    eval_monom_temp.append(1)
                    continue

                # check the feasibility of analytic expansion
                if (isinstance(gens[m_index], sympy.Pow) or m % 1 != 0) and self.dist.get(f'x{m_index}').translation != 0.0:
                    raise ValueError(
                        f'Error at evaluating moment of {list(self.dist.keys())[m_index]}. No known finite expression '
                        f'for this type of distribution '
                    )

                # E value of random variable in monomial
                eval_monom_temp.append(self.compute_eval(v=gens[m_index], m=m))

            # product of all element in list
            eval_monom = 1
            for ev in eval_monom_temp:
                eval_monom = eval_monom * ev

            eval_monoms.append(eval_monom)

        # element-wise multiplication
        moment = 0
        for co, ev in zip(coeffs, eval_monoms):
            moment = moment + co * ev

        return sympy.simplify(moment)

    @lru_cache
    def compute_eval(self, v, m):
        """Calculate E[V^m] based on tables 3.1 and 3.2 in thesis"""
        # get symbol and parameter of V
        v_params = self.dist[list(v.free_symbols)[0].name]
        v_symbol = self.__dict__[list(v.free_symbols)[0].name]

        # binomial expansion making v a random variable with standard distribution
        v_temp = sympy.poly(v_params.translation + v_symbol, v_symbol) ** m

        # get coefficients and monomials
        v_coeffs = v_temp.coeffs()
        v_monoms = v_temp.all_monoms()

        evms = []
        for v_monom in v_monoms:
            v_monom = v_monom[0]
            if v_params.distribution in ['uniform', 'uni']:
                evm_temp = (v_params.scale ** v_monom) / ((v_monom + 1) * 2)
            elif v_params.distribution in ['lognormal', 'logn']:
                evm_temp = sympy.exp(((v_monom ** 2) * (v_params.scale ** 2)) / 2)
            elif v_params.distribution in ['trapezoidal', 'tra']:
                evm_temp = (v_params.scale ** v_monom) / (v_monom ** 2 + 3 * v_monom + 2) * \
                           ((1 - (v_params.beta1 ** (v_monom + 2))) / (1 - (v_params.beta1 ** 2)))
            elif v_params.distribution in ['triangular', 'tri']:
                evm_temp = (v_params.scale ** v_monom) / (v_monom ** 2 + 3 * v_monom + 2)
            elif v_params.distribution in ['beta', 'bet']:
                evm_temp = (v_params.scale ** v_monom) / 2
                for ptm in range(v_monom):
                    evm_temp = evm_temp * (v_params.beta1 * (ptm + 1) - 1) / \
                               (v_params.beta1 + v_params.beta2 + (ptm + 1) - 1)
            elif v_params.distribution in ['normal', 'nor']:
                if v_monom % 2 == 0:
                    # when v_monom is even
                    evm_temp = (v_params.scale ** v_monom) * sympy.factorial2(v_monom - 1) / 2
                else:
                    # when v_monom is odd
                    evm_temp = (v_params.scale ** v_monom) * (2 ** ((v_monom / 2) - 1) * sympy.factorial((v_monom - 1) / 2)) \
                               / sympy.sqrt(sympy.pi)
            elif v_params.distribution in ['student', 'stu']:
                evm_temp = (v_params.scale ** v_monom) * \
                           (v_params.beta1 ** (v_monom / 2) * sympy.gamma((v_monom + 1) / 2) * sympy.gamma((v_params.beta1 - v_monom) / 2)) / \
                           (2 * sympy.sqrt(sympy.pi) * sympy.gamma(v_params.beta1 / 2))
            elif v_params.distribution in ['laplace', 'lap']:
                evm_temp = (v_params.scale ** v_monom) * sympy.factorial(v_monom) / 2
            elif v_params.distribution in ['gamma', 'gam']:
                evm_temp = (v_params.scale ** v_monom) / 2
                for ptm in range(v_monom):
                    evm_temp = evm_temp * (v_params.beta1 * (ptm + 1) - 1)
            elif v_params.distribution in ['weibull', 'wei']:
                evm_temp = (v_params.scale ** v_monom) * (v_params.beta1 * sympy.gamma((v_monom / v_params.beta1) + 1)) / 2
            elif v_params.distribution in ['rayleigh', 'ray']:
                evm_temp = (v_params.scale ** v_monom) * (2 ** ((v_monom / 2) - 1)) * sympy.gamma((2 + v_monom) / 2)
            elif v_params.distribution in ['maxwell', 'max']:
                if v_monom % 2 == 0:
                    # when v_monom is even
                    evm_temp = (v_params.scale ** v_monom) * sympy.factorial2(v_monom + 1)
                else:
                    # when v_monom is odd
                    evm_temp = (v_params.scale ** v_monom) * (2 ** ((v_monom / 2) + 1) / sympy.sqrt(sympy.pi)) * \
                               sympy.factorial((v_monom + 1) / 2)
            else:
                raise ValueError('Unknown distribution type')

            # adjust moment according to symmetry
            # TODO: Add support for asymmetry distribution
            if v_params.type == 'symmetrical':
                evm_temp = 2 * evm_temp if v_monom % 2 == 0 else 0
            elif v_params.type == 'one_sided_right':
                evm_temp = 2 * evm_temp
            elif v_params.type == 'one_sided_left':
                evm_temp = ((-1) ** evm_temp) * 2 * evm_temp
            else:
                raise ValueError('Unknown symmetry type')

            evms.append(evm_temp)

        # element-wise multiplication
        res = 0
        for evm, v_coeff in zip(evms, v_coeffs):
            res = res + evm * v_coeff

        return res


if __name__ == '__main__':
    polymoment = PolyMoment(
        poly='x0**(2)+x1**2',
        # x='x0,x1,x2',
        x='x0,x1',
        dist={
            'x0': {
                'distribution': 'normal',
                'type': 'symmetrical',
                'translation': 'm0',
                'scale': 's0',
            },
            'x1': {
                'distribution': 'normal',
                'type': 'symmetrical',
                'translation': 'm1',
                'scale': 's1',
            },
            # 'x2': {
            #     'distribution': 'normal',
            #     'type': 'symmetrical',
            #     'translation': 0,
            #     'scale': 0,
            # }
        }
    )

    print(polymoment.moment(order=2))
