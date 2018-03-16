'''Unit tests for `conll.py`.'''
import textwrap

import pytest

from scorch import conll  # noqa


@pytest.fixture()
def block():
    return [
        'test1	0	0	a1	(0',
        'test1	0	1	a2	0)',
        'test1	0	2	junk	-',
        'test1	0	3	b1	(1',
        'test1	0	4	b2	-',
        'test1	0	5	b3	-',
        'test1	0	6	b4	1)',
        'test1	0	7	jnk	-',
        'test1	0	8	.	-',
    ]



def test_parse_block(block):
    expected_entities = {'0': [('0', '1')],
                         '1': [('3', '6')]}
    entities = conll.parse_block(block)
    assert entities == expected_entities
