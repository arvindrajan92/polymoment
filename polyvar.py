from pydantic import BaseModel, validator
    
    
class PolyVar(BaseModel):
    distribution: str
    type: str
    translation: float
    scale: float
    beta1: float = None
    beta2: float = None

    @validator('distribution')
    def distribution_must_be_supported(cls, v):
        if v.lower() not in [
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
        ]:
            raise ValueError(f'Distribution {v} is not supported')
        return v

    @validator('type')
    def distribution_type_must_be_supported(cls, v):
        if v.lower() not in [
            'symmetrical',
            'one_sided_right',
            'one_sided_left',
            'asymmetrical'
        ]:
            raise ValueError(f'Distribution type {v} is not supported')
        return v
