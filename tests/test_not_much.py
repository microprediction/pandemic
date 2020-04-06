from pandemic.model import triple

def test_not_much():
    assert abs(triple(3)-0) < 1e-8