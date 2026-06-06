import pytest
from pathlib import Path
import datetime
from obsidiantools.api import Vault
TESTS_DIR = Path('.') / 'tests/properties-vault'


@pytest.fixture
def test_vault():
    return Vault(TESTS_DIR).connect()
# Test md_utils property functions


def test_get_basic_properties(test_vault):
    actual_props = test_vault.properties_index['basic_properties']
    expected_props = {
        'prop1': 'value1',
        'prop2': 'value2',
        'prop3': ['item1', 'item2', 'item3']
    }

    assert actual_props.keys() == expected_props.keys()
    # compare values individually:
    for k in actual_props.keys():
        assert actual_props[k] == expected_props[k]


def test_get_frontmatter_style_properties(test_vault):
    actual_props = test_vault.properties_index['frontmatter_style']

    # Check date property separately since it's a datetime object
    assert isinstance(actual_props['date'], datetime.date)
    assert actual_props['date'].isoformat() == '2025-07-17'

    # Test the rest of the properties
    date_removed = actual_props.copy()
    del date_removed['date']
    assert date_removed == {
        'tags': ['tag1', 'tag2'],
        'aliases': ['alias1', 'alias2'],
        'cssclass': 'my-class',
        'status': 'In Progress',
        'priority': 'High'
    }


def test_get_nested_properties(test_vault):
    actual_props = test_vault.properties_index['nested_properties']

    expected_props = {
        'nested': {
            'prop1': 'value1',
            'prop2': {
                'subprop1': 'val1',
                'subprop2': 'val2'
            },
            'prop3': ['item1', 'item2', 'item3']
        }
    }

    assert actual_props.keys() == expected_props.keys()
    # compare values individually:
    for k in actual_props.keys():
        assert actual_props[k] == expected_props[k]


def test_get_property_types(test_vault):
    actual_props = test_vault.properties_index['property_types']

    # Convert datetime objects to expected values for comparison
    assert isinstance(actual_props['date'], datetime.date)
    assert isinstance(actual_props['time'], datetime.datetime)
    assert actual_props['date'].isoformat() == '2020-08-21'
    assert actual_props['time'].isoformat() == '2020-08-21T10:30:00'

    # Test the rest of the properties
    date_time_removed = actual_props.copy()
    del date_time_removed['date']
    del date_time_removed['time']
    assert date_time_removed == {
        'number': 42,
        'float': 3.14,
        'boolean': True,
        'null_value': None,
        'array': [1, 2, 3],
        'empty': ''
    }


def test_get_inline_properties(test_vault):
    actual_props = test_vault.properties_index['inline_properties']

    # Check date property separately since it's a datetime object
    assert isinstance(actual_props['due'], datetime.date)
    assert actual_props['due'].isoformat() == '2025-07-17'

    # Test the rest of the properties
    date_removed = actual_props.copy()
    del date_removed['due']
    assert date_removed == {
        'prop': 'value with inline property',
        'tags': ['tag1', 'tag2', 'tag3'],
        'status': 'In Progress'
    }


def test_all_files_have_properties_indexed(test_vault):
    index = test_vault.properties_index
    assert 'basic_properties' in index
    assert 'frontmatter_style' in index
    assert len(index) == 10


def test_property_overriding(test_vault):
    actual_props = test_vault.properties_index['property_overriding']

    expected_props = {
        'prop1': 'value1',
        'prop2': 'overridden value2',  # inline should override frontmatter
        'prop3': 'value3'
    }

    assert actual_props.keys() == expected_props.keys()
    # compare values individually:
    for k in actual_props.keys():
        assert actual_props[k] == expected_props[k]


def test_property_special_chars(test_vault):
    actual_props = test_vault.properties_index['property_special_chars']

    expected_props = {
        'prop with spaces': 'value1',
        'prop:with:colons': 'value2',
        'prop-with-quotes': 'value3',
        'property with spaces': 'value4',
        'property:with:colons': 'value5',
        'property-with-quotes': 'value6'
    }

    assert actual_props.keys() == expected_props.keys()
    # compare values individually:
    for k in actual_props.keys():
        assert actual_props[k] == expected_props[k]


def test_property_whitespace_handling(test_vault):
    actual_props = test_vault.properties_index['property_whitespace']

    expected_props = {
        'prop1': 'value with spaces',  # extra spaces trimmed
        'prop2': 'value without spaces',
        'prop3': 'value with spaces before and after',  # extra spaces trimmed
        'prop4': '',  # empty value
        'prop5': ['tag1', 'tag2', 'tag3']  # spaces in array should be trimmed
    }

    assert actual_props.keys() == expected_props.keys()

    # compare values individually:
    for k in actual_props.keys():
        assert actual_props[k] == expected_props[k]


def test_property_link_handling(test_vault):
    actual_props = test_vault.properties_index['property_links']

    expected_props = {
        'link': 'Link',
        'linklist': ['Link', 'Link2']
    }

    assert actual_props.keys() == expected_props.keys()

    # compare values individually:
    for k in actual_props.keys():
        assert actual_props[k] == expected_props[k]


def test_querying_properties_within_index(test_vault):
    actual_prop = test_vault.properties_index['basic_properties']['prop1']
    assert actual_prop == 'value1'

    with pytest.raises(KeyError):
        actual_prop = test_vault.properties_index['nonexistent_note']['prop1']
