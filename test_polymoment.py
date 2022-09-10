from polymoment import PolyMoment


def test_gaussian_distribution():
    """Test Gaussian distribution"""
    polymoment = PolyMoment(
        poly='x0',
        x='x0',
        dist={
            'x0': {
                'distribution': 'normal',
                'type': 'symmetrical',
                'translation': 'm0',
                'scale': 's0'
            }
        }
    )

    # mean, var, skew, kurt
    assert polymoment.mean().__str__() == 'm0'
    assert polymoment.var().__str__() == 's0**2'
    assert polymoment.skew().__str__() == '0'
    assert polymoment.kurt().__str__() == '3'


def test_laplace_distribution():
    """Test Laplace distribution"""
    polymoment = PolyMoment(
        poly='x0',
        x='x0',
        dist={
            'x0': {
                'distribution': 'laplace',
                'type': 'symmetrical',
                'translation': 'm0',
                'scale': 's0'
            }
        }
    )

    # mean, var, skew, kurt
    assert polymoment.mean().__str__() == 'm0'
    assert polymoment.var().__str__() == '2*s0**2'
    assert polymoment.skew().__str__() == '0'
    assert polymoment.kurt().__str__() == '6'


def test_weibull_distribution():
    """Test Weibull distribution"""
    polymoment = PolyMoment(
        poly='x0',
        x='x0',
        dist={
            'x0': {
                'distribution': 'weibull',
                'type': 'one_sided_right',
                'translation': 'm0',
                'scale': 's0',
                'beta1': 'b0',
            }
        }
    )

    # mean, var, skew, kurt
    assert polymoment.mean().__str__() == 'm0 + s0*gamma(1 + 1/b0)'
    assert polymoment.var().__str__() == 's0**2*(-gamma(1 + 1/b0)**2 + gamma(1 + 2/b0))'
    assert polymoment.skew().__str__() == '-s0*(2*gamma(1 + 1/b0)**3 - 3*gamma(1 + 1/b0)*gamma(1 + 2/b0) + gamma(1 + ' \
                                          '3/b0))/(sqrt(-s0**2*(gamma(1 + 1/b0)**2 - gamma(1 + 2/b0)))*(gamma(1 + ' \
                                          '1/b0)**2 - gamma(1 + 2/b0)))'
    assert polymoment.kurt().__str__() == '(-3*gamma(1 + 1/b0)**4 + 6*gamma(1 + 1/b0)**2*gamma(1 + 2/b0) - 4*gamma(1 ' \
                                          '+ 1/b0)*gamma(1 + 3/b0) + gamma(1 + 4/b0))/(gamma(1 + 1/b0)**2 - gamma(1 +' \
                                          ' 2/b0))**2'


def test_uniform_distribution():
    """Test uniform distribution"""
    polymoment = PolyMoment(
        poly='x0',
        x='x0',
        dist={
            'x0': {
                'distribution': 'uniform',
                'type': 'one_sided_right',
                'translation': 'm0',
                'scale': 's0'
            }
        }
    )

    # mean, var, skew, kurt
    assert polymoment.mean().__str__() == 'm0 + s0/2'
    assert polymoment.var().__str__() == 's0**2/12'
    assert polymoment.skew().__str__() == '0'
    assert polymoment.kurt().__str__() == '9/5'


def test_gamma_distribution():
    """Test gamma distribution"""
    polymoment = PolyMoment(
        poly='x0',
        x='x0',
        dist={
            'x0': {
                'distribution': 'gamma',
                'type': 'one_sided_right',
                'translation': 'm0',
                'scale': 's0',
                'beta1': 'b0'
            }
        }
    )

    # mean, var, skew, kurt
    assert polymoment.mean().__str__() == 'b0*s0 + m0'
    assert polymoment.var().__str__() == 'b0*s0**2'
    assert polymoment.skew().__str__() == '2*s0/sqrt(b0*s0**2)'
    assert polymoment.kurt().__str__() == '3 + 6/b0'
