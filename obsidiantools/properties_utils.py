import datetime
import re
from .md_utils import _get_all_wikilinks_from_source_text
from ._constants import (INLINE_PROPERTY_REGEX,
                         INLINE_PROPERTY_VALUE_ARRAY_REGEX)


def _clean_up_property_key(key: str) -> str:
    """Clean a property key by removing quotes and trailing colons.

    Args:
        key (str): The property key to clean

    Returns:
        str: The cleaned key
    """
    # Remove trailing colons first (but not embedded ones)
    key = key.rstrip(':')
    # Remove outer quotes if present
    key = key.strip()
    if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
        key = key[1:-1].strip()
    return key


def _process_values_for_properties_from_front_matter(
    front_matter_clean_key, front_matter_value, *, types_config):
    property_data_type = types_config.get(front_matter_clean_key, 'text')
    processed_value = front_matter_value

    # wrangle single-item property:
    if isinstance(front_matter_value, str) and property_data_type == 'date':
        try:
            processed_value = datetime.datetime.strptime(front_matter_value, '%Y-%m-%d').date()
        except ValueError:
            print(f"Failed to parse date for key '{front_matter_clean_key}' with value '{front_matter_value}' in frontmatter")
    elif isinstance(front_matter_value, str) and property_data_type == 'datetime':
        try:
            processed_value = datetime.datetime.strptime(front_matter_value, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            pass
    elif isinstance(front_matter_value, str) and front_matter_value.startswith("[[") and front_matter_value.endswith("]]"):
        # Handle single wikilink as a string
        processed_value = _get_all_wikilinks_from_source_text(front_matter_value, remove_aliases=True)[0]
    # wrangle "list of items" property:
    elif isinstance(front_matter_value, list):
        # Handle list of strings, checking for wikilinks
        new_list = []
        for item in front_matter_value:
            if (isinstance(item, str) and item.startswith("[[") and item.endswith("]]")):
                # Extract the wikilink
                new_list.extend(_get_all_wikilinks_from_source_text(
                    item, remove_aliases=True))
            else:
                new_list.append(item)
            processed_value = new_list
        if property_data_type == 'date' and all(isinstance(item, str) for item in front_matter_value):
            try:  # Convert to date objects if they match the pattern
                processed_value = datetime.datetime.strptime(front_matter_value, '%Y-%m-%d').date()
            except ValueError:
                pass
    else:
        pass
    return processed_value


def _get_inline_properties_from_md_content(
    content: str, property_key: str, *, types_config: dict) -> dict:
    """Extract inline properties from a md file's front matter.

    Looks for lines in the format 'property:: value' and parses them into a dictionary.
    Handles array values in the format '[value1, value2]'.
    Handles special characters and quoted property names.

    Args:
        filepath (pathlib Path): Path object representing the file from
            which info will be extracted.
    Returns:
        dict: Dictionary of inline properties
    """
    properties = {}

    property_data_type = types_config.get(property_key, 'text')

    for line in content.splitlines():
        match = re.match(INLINE_PROPERTY_REGEX, line.strip())
        if match:
            key = match.group(1).strip()
            value = match.group(2)

            # Handle array values
            array_match = re.match(INLINE_PROPERTY_VALUE_ARRAY_REGEX, value)
            if array_match:
                # Split array values and clean them up
                values = [v.strip(' "\'' ) for v in array_match.group(1).split(',')]
                properties[property_key(key)] = values
            else:
                # Single value
                # Remove quotes from beginning and end if present
                value = value.strip()
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1].strip()

                clean_key = _clean_up_property_key(key)
                # Handle date and time strings after cleaning quotes
                if property_data_type == 'date':
                    try:
                        value = datetime.datetime.strptime(value, '%Y-%m-%d').date()
                    except ValueError:
                        pass
                elif property_data_type == 'datetime':
                    try:
                        value = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
                    except ValueError:
                        pass

                properties[clean_key] = value

    return properties
