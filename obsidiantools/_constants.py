# WIKILINKS AND EMBEDDED FILES: regex that includes any aliases
# group 0 captures embedded link; group 1 is everything inside [[]]
WIKILINK_REGEX = r'(!)?\[{2}([^\]\]]+)\]{2}'

# TAGS
TAG_INCLUDE_NESTED_REGEX = r'(?<!\()(?<!\\)#{1}([A-z]+[0-9_\-]*[A-Z0-9]?[^\s]+(?![^\[\[]*\]\]))\/?'
TAG_MAIN_ONLY_REGEX = r'(?<!\()#{1}([A-z]+[0-9_\-]*[A-Z0-9]?)\/?'

# md links: catch URLs or paths
INLINE_LINK_AFTER_HTML_PROC_REGEX = r'\[([^\]]+)\]\(<([^)]+)>\)'
INLINE_LINK_VIA_MD_ONLY_REGEX = r'\[([^\]]+)\]\(([^)]+)\)'

# helpers:
WIKILINK_AS_STRING_REGEX = r'\[[^\]]+\]\([^)]+\)'
EMBEDDED_FILE_LINK_AS_STRING_REGEX = r'!?\[{2}([^\]\]]+)\]{2}'
