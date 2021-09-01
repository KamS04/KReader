from typing import List

from .. import thread_sys

ALL_HANDLERS: List[thread_sys.Handler] = None
PAGES_RENDERER: thread_sys.Handler = None
COVERS_RENDERER: thread_sys.Handler = None
METADATA: thread_sys.Handler = None
PROCESSING: thread_sys.Handler = None

# Creates and initializes the handlers listed above so they can be used globally
async def initialize_handlers(debug=False):
    global ALL_HANDLERS
    handler_items = await thread_sys.init_handlers( ['pages_renderer', 'covers_renderer', 'metadata', 'processing'], debug=debug)

    ALL_HANDLERS = [ item.handler for item in handler_items ]

    for handler in ALL_HANDLERS:
        if debug:
            print(handler.name, handler.loop)
        globals()[handler.name.upper()] = handler
