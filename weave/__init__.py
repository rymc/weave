from . import context_state as _context

_loading_builtins_token = _context.set_loading_built_ins()

from . import weave_types as types
from . import (
    make_type as _make_type,
)  # this patches the `Type` class to enable the make method - needed due to circular references
from . import ops
from . import panels
from .graph import Node  # used as a type in op definitions
from .show import show
from .api import *

# Note: we don't want to treat ecosystem as builtins, but this makes things
# easier at the moment.
# TODO: fix
from .ecosystem import ecosystem

from .vectorize import _make_vectorized_constructor_ops

_make_vectorized_constructor_ops()
_context.clear_loading_built_ins(_loading_builtins_token)

# Wow, this works! you can do just "weave" in a notebook and render
# something. Maybe render ecosystem panel?
# def _ipython_display_():
#     return show(ecosystem())
