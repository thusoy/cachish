import pytest

from cachish import utils as uut

_MERGE_DICT_TESTS = (
    ({'a': 1}, {'b': 2}, {'a': 1, 'b': 2}),
    ({'a': 1}, {'a': 2}, {'a': 2}),
    ({'a': {'b': 1}}, {'a': {'c': 2}}, {'a': {'b': 1, 'c': 2}}),
)


@pytest.fixture(params=_MERGE_DICT_TESTS)
def merge_dicts(request):
    yield request.param


def test_merge_dicts(merge_dicts):
    a, b = merge_dicts[0], merge_dicts[1]
    uut.merge_dicts(a, b)
    assert a == merge_dicts[2]
