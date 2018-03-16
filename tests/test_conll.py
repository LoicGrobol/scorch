'''Unit tests for `conll.py`.'''
import pytest

from scorch import conll  # noqa


@pytest.fixture()
def block():
    return [
        'test1	0	0	a1	(0',
        'test1	0	1	a2	0)',
        'test1	0	2	jnk	-',
        'test1	0	3	b1	(1',
        'test1	0	4	b2	-',
        'test1	0	5	b3	-',
        'test1	0	6	b4	1)',
        'test1	0	7	jnk	-',
        'test1	0	8	.	-',
        'test1	0	9	jun	(0)',
    ]


@pytest.fixture()
def document():
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
        'test1	0	9	jun	(0)',
        '',
        'test2	0	0	c	(1)',
        'test2	0	1	jnk	-',
        'test2	0	2	d1	(2',
        'test2	0	3	d2	2)',
        'test2	0	4	jnk	-',
        'test2	0	5	e	(2)',
        'test2	0	6	jnk	-',
        'test2	0	7	f1	(2',
        'test2	0	8	f2	-',
        'test2	0	9	f3	2)',
        'test2	0	10	.	-',
    ]


@pytest.fixture()
def conll_file():
    return [
        '#begin document (Testcase1);',
        'test1	0	0	a1	(0',
        'test1	0	1	a2	0)',
        'test1	0	2	junk	-',
        'test1	0	3	b1	(1',
        'test1	0	4	b2	-',
        'test1	0	5	b3	-',
        'test1	0	6	b4	1)',
        'test1	0	7	jnk	-',
        'test1	0	8	.	-',
        'test1	0	9	jun	(0)',
        '',
        'test2	0	0	c	(1)',
        'test2	0	1	jnk	-',
        'test2	0	2	d1	(2',
        'test2	0	3	d2	2)',
        'test2	0	4	jnk	-',
        'test2	0	5	e	(2)',
        'test2	0	6	jnk	-',
        'test2	0	7	f1	(2',
        'test2	0	8	f2	-',
        'test2	0	9	f3	2)',
        'test2	0	10	.	-',
        '#end document',
        '#begin document (Testcase2); part 000',
        'test1	0	0	a1	(0',
        'test1	0	1	a2	0)',
        'test1	0	2	jnk	-',
        'test1	0	3	b1	(1',
        'test1	0	4	b2	-',
        'test1	0	5	b3	-',
        'test1	0	6	b4	1)',
        'test1	0	7	jnk	-',
        'test1	0	8	.	-',
        'test1	0	9	jun	(0)',
        '# end document',
    ]


def test_parse_block(block):
    expected_entities = {'0': [('0', '1'), ('9', '9')],
                         '1': [('3', '6')]}
    entities = conll.parse_block(block)
    assert entities == expected_entities


def test_parse_document(document):
    expected_entities = {
        '0': [(0, '0', '1'), (0, '9', '9')],
        '1': [
            (0, '3', '6'),
            (1, '0', '0'),
        ],
        '2': [
            (1, '2', '3'),
            (1, '5', '5'),
            (1, '7', '9'),
        ]
    }
    entities = conll.parse_document(document)
    assert entities == expected_entities


def test_parse_file(conll_file):
    expected_documents = [
        (
            'Testcase1',
            {
                '0': [(0, '0', '1'), (0, '9', '9')],
                '1': [
                    (0, '3', '6'),
                    (1, '0', '0'),
                ],
                '2': [
                    (1, '2', '3'),
                    (1, '5', '5'),
                    (1, '7', '9'),
                ],
            }
        ),
        (
            'Testcase2-000',
            {'0': [(0, '0', '1'), (0, '9', '9')],
             '1': [(0, '3', '6')]}
        ),
    ]
    documents = conll.parse_file(conll_file)
    assert list(documents) == expected_documents
