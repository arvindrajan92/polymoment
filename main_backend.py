import ray
from ray import serve
from fastapi import FastAPI

from polymoment import PolyMoment
from datamodel import RequestModel, ResponseModel


app = FastAPI(
    title='PolyMoment',
    description='A REST API for calculating high-order moments of multivariate polynomials',
    version='1.0.0'
)

polymoment_handle = None


@serve.deployment(num_replicas=4)
class PolymomentDeployment:
    async def __call__(self, request: dict, method: str) -> dict:
        polymoment = PolyMoment(poly=request.get('poly'), dist=request.get('dist'))
        if method == 'moment':
            return {'result': polymoment.moment(order=request.get('order')).__str__()}
        elif method == 'mean':
            return {'result': polymoment.mean().__str__()}
        elif method == 'std':
            return {'result': polymoment.std().__str__()}
        elif method == 'var':
            return {'result': polymoment.var().__str__()}
        elif method == 'skew':
            return {'result': polymoment.skew().__str__()}
        elif method == 'kurt':
            return {'result': polymoment.kurt().__str__()}
        else:
            raise NotImplementedError(f"Method {method} is not implemented")


@app.on_event("startup")
async def startup_event():
    ray.init(include_dashboard=False)
    _ = serve.start(http_options=None)

    global polymoment_handle
    polymoment_handle = serve.run(PolymomentDeployment.bind())


@app.post("/moment/", response_model=ResponseModel)
async def get_moment(request: RequestModel):
    return await polymoment_handle.remote(request=request.dict(), method='moment')


@app.post("/mean/", response_model=ResponseModel)
async def get_moment(request: RequestModel):
    return await polymoment_handle.remote(request=request.dict(), method='mean')


@app.post("/std/", response_model=ResponseModel)
async def get_moment(request: RequestModel):
    return await polymoment_handle.remote(request=request.dict(), method='std')


@app.post("/var/", response_model=ResponseModel)
async def get_moment(request: RequestModel):
    return await polymoment_handle.remote(request=request.dict(), method='var')


@app.post("/skew/", response_model=ResponseModel)
async def get_moment(request: RequestModel):
    return await polymoment_handle.remote(request=request.dict(), method='skew')


@app.post("/kurt/", response_model=ResponseModel)
async def get_moment(request: RequestModel):
    return await polymoment_handle.remote(request=request.dict(), method='kurt')
