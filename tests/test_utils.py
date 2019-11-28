import pytest

from cachish import utils


@pytest.mark.parametrize('input1,input2,expected', [
    ({'a': 1}, {'b': 2}, {'a': 1, 'b': 2}),
    ({'a': 1}, {'a': 2}, {'a': 2}),
    ({'a': {'b': 1}}, {'a': {'c': 2}}, {'a': {'b': 1, 'c': 2}}),
])
def test_merge_dicts(input1, input2, expected):
    utils.merge_dicts(input1, input2)
    assert input1 == expected
