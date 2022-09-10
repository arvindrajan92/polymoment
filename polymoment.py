import sympy

from functools import lru_cache
from typing import Dict
from polyvar import PolyVar


class PolyMoment:
    def __init__(self, poly: str, dist: Dict):
        for key in dist.keys():
            self.__dict__[key] = sympy.symbols(key)
        self.poly = sympy.poly(eval(poly.replace('x', 'self.x')))
        self.dist = {k: PolyVar(**v) for k, v in dist.items()}

    def __call__(self, *args, **kwargs):
        return self.moment(*args, **kwargs)

    def std(self):
        """Calculates standard deviation of self.poly"""
        std = sympy.sqrt(self.var())
        return sympy.simplify(std)

    def var(self):
        """Calculates variance of self.poly"""
        var = self.moment(order=2) - (self.moment(order=1) ** 2)
        return sympy.simplify(var)

    def skew(self):
        """Calculates skewness of self.poly"""
        mean = self.mean()
        var = self.var()
        skew = (self.moment(order=3) - (3 * mean * var) - (mean ** 3)) / (sympy.sqrt(var) ** 3)
        return sympy.simplify(skew)

    def kurt(self):
        """Calculates kurtosis (excess kurtosis + 3) of self.poly"""
        e1, e2, e3, e4 = self.moment(order=1), self.moment(order=2), self.moment(order=3), self.moment(order=4)
        c_mom4 = -3 * e1 ** 4 + 6 * e1 ** 2 * e2 - 4 * e1 * e3 + e4
        kurt = c_mom4 / ((e2 - (e1 ** 2)) ** 2)
        return sympy.simplify(kurt)

    def mean(self):
        """Calculates mean of self.poly"""
        mu = self.moment(order=1)
        return sympy.simplify(mu)

    def moment(self, order: int):
        """Calculates the expectation of self.poly raised to the power of order"""
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

        if not isinstance(v, sympy.Pow):
            # check the feasibility of analytic expansion
            if m % 1 != 0:
                raise ValueError(
                    f'Error at evaluating moment of {list(v.free_symbols)[0].name}. No known finite expression for '
                    f'this type of distribution '
                )

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
                    evm_temp = (v_params.scale ** v_monom) / (v_monom ** 2 + (3 * v_monom) + 2) * \
                               ((1 - (v_params.beta1 ** (v_monom + 2))) / (1 - (v_params.beta1 ** 2)))
                elif v_params.distribution in ['triangular', 'tri']:
                    evm_temp = (v_params.scale ** v_monom) / (v_monom ** 2 + (3 * v_monom) + 2)
                elif v_params.distribution in ['beta', 'bet']:
                    evm_temp = (v_params.scale ** v_monom) / 2
                    for ptm in range(v_monom):
                        evm_temp = evm_temp * (v_params.beta1 + (ptm + 1) - 1) / \
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
                        evm_temp = evm_temp * (v_params.beta1 + (ptm + 1) - 1)
                elif v_params.distribution in ['weibull', 'wei']:
                    evm_temp = (v_params.scale ** v_monom) * (sympy.gamma((v_monom / v_params.beta1) + 1)) / 2
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
                # TODO: Add support for asymmetrical distribution
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
        else:
            m, mu, scale = m * v.exp, v_params.translation, v_params.scale
            if v_params.distribution in ['uniform', 'uni']:
                if m == -1:
                    return sympy.log((mu + scale) / (mu - scale)) / (2 * scale)
                else:
                    return ((mu + scale) ** (m + 1) - (mu - scale) ** (m + 1)) / (2 * scale * (m + 1))
            elif v_params.distribution in ['lognormal', 'logn']:
                return sympy.exp((mu * m) + (m ** 2 * scale ** 2 / 2))
            else:
                raise ValueError('Unknown distribution type')
