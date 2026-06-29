from __future__ import annotations

from bias_core.extensions import FormatterExtender


def tag_mentions_extenders():
    from bias_ext_mentions.backend.tag_mentions import render_tag_mentions_html

    return [
        FormatterExtender().render(render_tag_mentions_html),
    ]
