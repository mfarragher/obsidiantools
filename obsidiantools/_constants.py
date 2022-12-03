# wikilink & embedded file regex: regex that includes any aliases
# group 0 captures embedded link; group 1 is everything inside [[]]
WIKILINK_REGEX = r'(!)?\[{2}([^\]\]]+)\]{2}'

# md links regex: catch URLs or paths
INLINE_LINK_AFTER_HTML_PROC_REGEX = r'\[([^\]]+)\]\(<([^)]+)>\)'
INLINE_LINK_VIA_MD_ONLY_REGEX = r'\[([^\]]+)\]\(([^)]+)\)'

TAG_REGEX = r'(?<!\()#{1}([A-z]+[0-9_\-]*[A-Z0-9]?)\/?'
