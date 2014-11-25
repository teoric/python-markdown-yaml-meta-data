"""
# YAML Meta Data Extension for [Python-Markdown](https://github.com/waylan/Python-Markdown)

This extension adds YAML meta data handling to markdown.

As in the original, meta data is parsed but not used in processing.

(YAML meta data is used e.g. by [pandoc](http://johnmacfarlane.net/pandoc/))

Dependencies: [PyYAML](http://pyyaml.org/)


Basic Usage:

    >>> import markdown
    >>> text = '''---
    ... Title: Test Doc.
    ... Author: Waylan Limberg
    ... Blank_Data:
    ... ...
    ...
    ... The body. This is paragraph one.
    ... '''
    >>> md = markdown.Markdown(['meta_yaml'])
    >>> print(md.convert(text))
    <p>The body. This is paragraph one.</p>
    >>> print(md.Meta) # doctest: +SKIP
    {'blank_data': [''], 'author': ['Waylan Limberg'], 'title': ['Test Doc.']}

Make sure text without Meta Data still works (markdown < 1.6b returns a <p>).

    >>> text = '    Some Code - not extra lines of meta data.'
    >>> md = markdown.Markdown(['meta_yaml'])
    >>> print(md.convert(text))
    <pre><code>Some Code - not extra lines of meta data.
    </code></pre>
    >>> md.Meta
    {}


Copyright 2014 Bernhard Fisseni

Based on the meta data extension included with Python-Markdown,
Copyright 2007-2008 [Waylan Limberg](http://achinghead.com).

License: BSD (see LICENSE.md for details)

"""

from __future__ import absolute_import
from __future__ import unicode_literals
from markdown import Extension
from markdown.preprocessors import Preprocessor
import re
import yaml
try:
    from yaml import CSafeLoader as Loader
except ImportError:
    from yaml import Loader


class MetaYamlExtension (Extension):

    """Extension for parsing YAML-Metadata with Python-Markdown."""

    def extendMarkdown(self, md, md_globals):
        """Add MetaYamlPreprocessor to Markdown instance."""
        md.preprocessors.add("meta_yaml", MetaYamlPreprocessor(md), ">meta")


class MetaYamlPreprocessor(Preprocessor):

    """
    Get Meta-Data.

    A YAML block is delimited by
    - a line '---' at the start
    - and a '...' or '---' line
    at the end.
    """

    def run(self, lines):
        """ Parse Meta-Data and store in Markdown.Meta. """
        yaml_block = []
        line = lines.pop(0)
        if re.match(r'-{3}', line):
            while lines:
                line = lines.pop(0)
                if re.match(r'(\.{3}|-{3})', line):
                    break
                yaml_block.append(line)
        else:
            lines.insert(0, line)
        if yaml_block:
            meta = yaml.load("\n".join(yaml_block), Loader)
            # case-insensitize meta data keys:
            meta = {
                k.lower(): meta[k] for k in meta
            }
            # PyMarkdown's Meta compat: ensure everything's a list
            meta = {
                k: v if isinstance(v, list) else [v] for k, v in meta.items()
            }
            self.markdown.Meta = meta
        return lines


def makeExtension(configs={}):
    """set up extension."""
    return MetaYamlExtension(configs=configs)
