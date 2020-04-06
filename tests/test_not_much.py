from pandemic.model import triple

def test_not_much():
    assert abs(triple(3)-9) < 1e-8


if __name__=="__main__":
    test_not_much()