import pytest
from pathlib import Path
import datetime
from obsidiantools.md_utils import get_properties, get_property
from obsidiantools.api import Vault

# Test fixtures
@pytest.fixture
def property_test_files():
    return {
        'basic': Path('.') / 'tests/general/property-tests/basic_properties.md',
        'frontmatter': Path('.') / 'tests/general/property-tests/frontmatter_style.md',
        'nested': Path('.') / 'tests/general/property-tests/nested_properties.md',
        'types': Path('.') / 'tests/general/property-tests/property_types.md',
        'inline': Path('.') / 'tests/general/property-tests/inline_properties.md',
        'overriding': Path('.') / 'tests/general/property-tests/property_overriding.md',
        'special': Path('.') / 'tests/general/property-tests/property_special_chars.md',
        'whitespace': Path('.') / 'tests/general/property-tests/property_whitespace.md'
    }

@pytest.fixture
def test_vault(tmp_path):
    return Vault(Path('.') / 'tests/general/property-tests').connect()

# Test md_utils property functions
def test_get_basic_properties(property_test_files):
    props = get_properties(property_test_files['basic'])
    assert props == {
        'prop1': 'value1',
        'prop2': 'value2',
        'prop3': ['item1', 'item2', 'item3']
    }

def test_get_frontmatter_style_properties(property_test_files):
    props = get_properties(property_test_files['frontmatter'])
    
    # Check date property separately since it's a datetime object
    assert isinstance(props['date'], datetime.date)
    assert props['date'].isoformat() == '2025-07-17'
    
    # Test the rest of the properties
    date_removed = props.copy()
    del date_removed['date']
    assert date_removed == {
        'tags': ['tag1', 'tag2'],
        'aliases': ['alias1', 'alias2'],
        'cssclass': 'my-class',
        'status': 'In Progress',
        'priority': 'High'
    }

def test_get_nested_properties(property_test_files):
    props = get_properties(property_test_files['nested'])
    assert props == {
        'nested': {
            'prop1': 'value1',
            'prop2': {
                'subprop1': 'val1',
                'subprop2': 'val2'
            },
            'prop3': ['item1', 'item2', 'item3']
        }
    }

def test_get_property_types(property_test_files):
    props = get_properties(property_test_files['types'])
    
    # Convert datetime objects to expected values for comparison
    assert isinstance(props['date'], datetime.date)
    assert isinstance(props['time'], datetime.datetime)
    assert props['date'].isoformat() == '2020-08-21'
    assert props['time'].isoformat() == '2020-08-21T10:30:00'
    
    # Test the rest of the properties
    date_time_removed = props.copy()
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

def test_get_inline_properties(property_test_files):
    props = get_properties(property_test_files['inline'])
    
    # Check date property separately since it's a datetime object
    assert isinstance(props['due'], datetime.date)
    assert props['due'].isoformat() == '2025-07-17'
    
    # Test the rest of the properties
    date_removed = props.copy()
    del date_removed['due']
    assert date_removed == {
        'prop': 'value with inline property',
        'tags': ['tag1', 'tag2', 'tag3'],
        'status': 'In Progress'
    }

def test_get_specific_property(property_test_files):
    prop = get_property(property_test_files['basic'], 'prop1')
    assert prop == 'value1'
    
    prop = get_property(property_test_files['basic'], 'prop3')
    assert prop == ['item1', 'item2', 'item3']
    
    prop = get_property(property_test_files['basic'], 'nonexistent')
    assert prop is None

# Test Vault class property methods
def test_vault_get_properties(test_vault):
    props = test_vault.get_properties('basic_properties')
    assert props == {
        'prop1': 'value1',
        'prop2': 'value2',
        'prop3': ['item1', 'item2', 'item3']
    }

def test_vault_get_property(test_vault):
    prop = test_vault.get_property('basic_properties', 'prop1')
    assert prop == 'value1'
    
    prop = test_vault.get_property('nonexistent_note', 'prop1')
    assert prop is None

def test_vault_get_properties_index(test_vault):
    index = test_vault.get_properties_index()
    assert 'basic_properties' in index
    assert 'frontmatter_style' in index
    assert len(index) == 9  # All our test files should have properties
    assert index['basic_properties']['prop1'] == 'value1'
    assert index['frontmatter_style']['status'] == 'In Progress'
    assert index['inline_properties']['tags'] == ['tag1', 'tag2', 'tag3']

def test_property_overriding(property_test_files):
    props = get_properties(property_test_files['overriding'])
    assert props == {
        'prop1': 'value1',
        'prop2': 'overridden value2',  # inline should override frontmatter
        'prop3': 'value3'
    }

def test_property_special_chars(property_test_files):
    props = get_properties(property_test_files['special'])
    assert props == {
        'prop with spaces': 'value1',
        'prop:with:colons': 'value2',
        'prop-with-quotes': 'value3',
        'property with spaces': 'value4',
        'property:with:colons': 'value5',
        'property-with-quotes': 'value6'
    }

def test_property_whitespace_handling(property_test_files):
    props = get_properties(property_test_files['whitespace'])
    assert props == {
        'prop1': 'value with spaces',  # extra spaces trimmed
        'prop2': 'value without spaces',
        'prop3': 'value with spaces before and after',  # extra spaces trimmed
        'prop4': '',  # empty value
        'prop5': ['tag1', 'tag2', 'tag3']  # spaces in array should be trimmed
    }
