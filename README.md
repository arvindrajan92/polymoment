# PolyMoment: High-order Moments of Multivariate Polynomials

This is the implementation of the thesis: [Moment-Based Uncertainty Propagation Using Multivariate Polynomials: Advances in Probabilistic Engineering Design](https://bridges.monash.edu/articles/thesis/Moment-Based_Uncertainty_Propagation_Using_Multivariate_Polynomials_Advances_in_Probabilistic_Engineering_Design/6998936).

## Usage

The example below demonstrates how `PolyMoment` can be used to compute the high-order moment, mean, variance, standard deviation, skewness, or kurtosis of polynomial `x0^2+x1^2` with random variables `x0` and `x1` following normal distribution with means `m0` and `m1`, respectively, and standard deviations `s0` and `s1`, respectively.

The supported distributions and their respective probability density functions can be found in [this file](ProbabilityDensityFunction.pdf).

```python
from polymoment import PolyMoment

pm = PolyMoment(
    poly='x0**2+x1**2',
    x='x0,x1',
    dist={
        'x0': {
            'distribution': 'normal',	# str
            'type': 'symmetrical',      # str
            'translation': 'm0',        # str | float
            'scale': 's0',              # str | float
            'beta1': None,              # str | float
            'beta2': None,              # str | float
        },
        'x1': {
            'distribution': 'normal',   # str
            'type': 'symmetrical',      # str
            'translation': 'm1',        # str | float
            'scale': 's1',              # str | float
            'beta1': None,              # str | float
            'beta2': None,              # str | float
        }
    }
)

# mean
print(pm.mean())

# variance
print(pm.var())

# standard deviation
print(pm.std())

# skewness
print(pm.skew())

# kurtosis (excess kurtosis + 3)
print(pm.kurt())

# n-th order moment of poly
print(pm.moment(order=1))
```

## Supported Distribution Types

```python
'symmetrical',
'one_sided_right',
'one_sided_left'
```

## Supported Distributions

Further information on the probability density functions listed below can be found in [this file](https://github.com/arvindrajan92/polymoment/blob/master/ProbabilityDensityFunction.pdf).

```python
'uniform',
'trapezoidal',
'triangular',
'beta',
'normal',
'student',
'laplace',
'gamma',
'weibull',
'maxwell'
```