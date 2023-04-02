# to launch:
# python3 tests/list_media.py

import resolve_helper

rh = resolve_helper.resolve_helper()

rh.list_media_in_pool(rh.activeproject)
