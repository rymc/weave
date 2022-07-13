from .. import panel
from .. import panel_util
from .. import ops


class Html(panel.Panel):
    id = "html-file"

    def __init__(self, input_node, **config):
        # Convert input_node here
        # TODO: Type adaptation should be done by render, not
        #     construction (ie the Panel should handle Markdown and File<Markdown>
        #     types)
        input_node = panel_util.make_node(input_node)
        if isinstance(input_node.type, ops.HtmlType):
            input_node = ops.html_file(input_node)
        super().__init__(input_node)

    @property
    def config(self):
        return {}