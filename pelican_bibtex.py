"""
Pelican BibTeX
==============

A Pelican plugin that populates the context with a list of formatted
citations, loaded from a BibTeX file at a configurable path.

The use case for now is to generate a ``Publications'' page for academic
websites.
"""
# Author: Vlad Niculae <vlad@vene.ro>
# Unlicense (see UNLICENSE for details)

import logging
import collections
logger = logging.getLogger(__name__)

from pelican import signals

__version__ = '0.2.1'


def add_publications(generator):
    """
    Populates context with a list of BibTeX publications.

    Configuration
    -------------
    generator.settings['PUBLICATIONS']:
        Dictionary containing BibTeX files to read as values and their names as keys.

    Output
    ------
    generator.context['publications']:
        Dictionary containing the name of the publication list a a key, bibliography entries as a value.
        A bibliography entry contains of a list of tuples (key, year, text, bibtex, pdf, slides, poster).
        See Readme.md for more details.
    """
    if 'PUBLICATIONS' not in generator.settings:
        return
    if 'PUBLICATIONS_HEADER' not in generator.settings:
        generator.context['PUBLICATIONS_HEADER'] = True

    if 'PUBLICATIONS_HIGHLIGHTS' in generator.settings:
        highlights = generator.settings['PUBLICATIONS_HIGHLIGHTS']
    else:
        highlights = []
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO
    try:
        from pybtex.database.input.bibtex import Parser
        from pybtex.database.output.bibtex import Writer
        from pybtex.database import BibliographyData, PybtexError
        from pybtex.backends import html
        from pybtex.style.formatting import plain
    except ImportError:
        logger.warn('`pelican_bibtex` failed to load dependency `pybtex`')
        return

    refs = generator.settings['PUBLICATIONS']
    generator.context['publications'] = collections.OrderedDict()

    for refs_name, refs_file in refs.items():
        try:
            bibdata_all = Parser().parse_file(refs_file)
        except PybtexError as e:
            logger.warn('`pelican_bibtex` failed to parse file %s: %s' % (
                refs_file,
                str(e)))
            return

        publications = []

        # format entries
        plain_style = plain.Style()
        html_backend = html.Backend()
        formatted_entries = plain_style.format_entries(bibdata_all.entries.values())

        for formatted_entry in formatted_entries:
            key = formatted_entry.key
            entry = bibdata_all.entries[key]
            year = entry.fields.get('year')

            # This shouldn't really stay in the field dict
            # but new versions of pybtex don't support pop
            pdf = entry.fields.get('pdf', None)
            slides = entry.fields.get('slides', None)
            poster = entry.fields.get('poster', None)

            #render the bibtex string for the entry
            bib_buf = StringIO()
            bibdata_this = BibliographyData(entries={key: entry})
            Writer().write_stream(bibdata_this, bib_buf)
            text = formatted_entry.text.render(html_backend)
            for replace in highlights:
              text = text.replace(replace, '<strong>' + replace + '</strong>')

            publications.append((key,
                                year,
                                text,
                                bib_buf.getvalue(),
                                pdf,
                                slides,
                                poster))

        generator.context['publications'][refs_name] = sorted(publications, key=lambda pub: pub[1], reverse=True)


def register():
    signals.generator_init.connect(add_publications)
