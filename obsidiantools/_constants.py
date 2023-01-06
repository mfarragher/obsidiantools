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

# Sets of extensions via https://help.obsidian.md/How+to/Embed+files :
# NB: file.ext and file.EXT can exist in same folder
IMG_EXT_SET = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg',
               '.PNG', '.JPG', '.JPEG', '.GIF', '.BMP', '.SVG'}
AUDIO_EXT_SET = {'.mp3', '.webm', '.wav', '.m4a', '.ogg', '.3gp', '.flac',
                 '.MP3', '.WEBM', '.WAV', '.M4A', '.OGG', '.3GP', '.FLAC'}
VIDEO_EXT_SET = {'.mp4', '.webm', '.ogv', '.mov', '.mkv',
                 '.MP4', '.WEBM', '.OGV', '.MOV', '.MKV'}
PDF_EXT_SET = {'.pdf',
               '.PDF'}
# canvas files:
CANVAS_EXT_SET = {'.canvas',
                  '.CANVAS'}

# metadata df cols order:
METADATA_DF_COLS_GENERIC_TYPE = [
    'rel_filepath', 'abs_filepath',
    'file_exists',
    'n_backlinks', 'n_wikilinks', 'n_tags', 'n_embedded_files',
    'modified_time']
