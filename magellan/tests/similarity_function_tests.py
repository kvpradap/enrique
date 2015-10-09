from nose.tools import *
from magellan.feature.simfunctions import *
from magellan.feature.tokenizers import *

a1 = 'Databases'
a2 = 'Datascience'
b1 = 'Psychology'
s1 = 'Database management'
s2 = 'Datascience management'
r1 = 'Theory of evolution'

def test_lev():
    assert(lev(a1, a2) > lev(a1, b1))

def test_mel():
    assert(monge_elkan(a1, a2) > monge_elkan(a1, b1))

def test_nmn():
    assert(needleman_wunsch(a1, a2) > needleman_wunsch(a1, b1))

def test_swg():
    assert(smith_waterman_gotoh(a1, a2) > smith_waterman_gotoh(a1, b1))

def test_swn():
    assert(smith_waterman(a1, a2) > smith_waterman(a1, b1))

def test_jaro():
    assert(jaro(a1, a2) > jaro(a1, b1))

def test_jwk():
    assert(jaro_winkler(a1, a2) > jaro_winkler(a1, b1))

def test_sdx():
    assert(soundex(a1, a2) > soundex(a1, b1))

def test_exm():
    assert(exact_match(a1, a1) == 1)
    assert(exact_match(a1, b1) == 0)

def test_rdf():
    a = 100
    b = 101
    c = 102
    assert(rel_diff(a, b) > rel_diff(a, c))

def test_anm():
    a = 100
    b = 101
    c = 102
    assert(abs_norm(a, b) > abs_norm(a, c))

def test_jac():
    v1 = tok_qgram(s1, 3)
    v2 = tok_qgram(s2, 3)
    v3 = tok_qgram(r1, 3)
    assert(jaccard(v1, v2) > jaccard(v1, v3))

def test_cos():
    v1 = tok_qgram(s1, 3)
    v2 = tok_qgram(s2, 3)
    v3 = tok_qgram(r1, 3)
    assert(cosine(v1, v2) > cosine(v1, v3))
