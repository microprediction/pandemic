import pymorton, math

# We use a different z-order embedding for parameters as we need more than two dimensions

def morton_scale(dim):
    return 2 ** 10

def morton_large(dim):
    SCALE = morton_scale(dim=dim)
    return pymorton.interleave(*[SCALE - 1 for _ in range(dim)])

def to_zcurve(prctls):
    """ A mapping from R^n -> R based on the Morton z-curve """
    dim = len(prctls)
    SCALE = morton_scale(dim)
    int_prctls = [int(math.floor(p * SCALE)) for p in prctls]
    m1 = pymorton.interleave(*int_prctls)
    int_prctls_back = pymorton.deinterleave2(m1) if dim == 2 else pymorton.deinterleave3(m1)
    assert all(i1 == i2 for i1, i2 in zip(int_prctls, int_prctls_back))
    m2 = pymorton.interleave(*[SCALE - 1 for _ in range(dim)])
    return m1 / m2

def from_zcurve(zpercentile, dim):
    SCALE = morton_scale(dim)
    zmorton = int(morton_large(dim) * zpercentile + 0.5)
    if dim == 2:
        values = pymorton.deinterleave2(zmorton)
    elif dim == 3:
        values = pymorton.deinterleave3(zmorton)
    prtcls = [v / SCALE for v in values]
    return prtcls



def norminv(self,p):
    f = _norminv_function()
    return f(p)

def to_zscores(prctls):
    norminv = _norminv_function()
    return [ norminv(p) for p in prctls ]

def _norminv_function():
    try:
        from statistics import NormalDist
        return NormalDist(mu=0, sigma=1.0).inv_cdf
    except ImportError:
        from scipy.stats import norm
        return norm.ppf