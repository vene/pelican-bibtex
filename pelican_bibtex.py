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
logger = logging.getLogger(__name__)

from pelican import signals

__version__ = '0.2.1'


def add_publications(generator):
    """
    Populates context with a list of BibTeX publications.

    Configuration
    -------------
    generator.settings['PUBLICATIONS_SRC']:
        Local path to the BibTeX file to read.

    generator.settings['PUBLICATIONS_SPLIT_BY']:
        The name of the bibtex field used for splitting the publications.
        No splitting if title is not provided.

    generator.settings['PUBLICATIONS_UNTAGGED_TITLE']:
        The title of the header for all untagged entries.
        No such list if title is not provided.

    Output
    ------
    generator.context['publications_lists']:
        A map with keys retrieved from the field named in PUBLICATIONS_SPLIT_TAG.
        Values are lists of tuples (key, year, text, bibtex, pdf, slides, poster)
        See Readme.md for more details.

    generator.context['publications']:
        Contains all publications as a list of tuples
        (key, year, text, bibtex, pdf, slides, poster).
        See Readme.md for more details.
    """
    if 'PUBLICATIONS_SRC' not in generator.settings:
        return
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

    refs_file = generator.settings['PUBLICATIONS_SRC']
    try:
        bibdata_all = Parser().parse_file(refs_file)
    except PybtexError as e:
        logger.warn('`pelican_bibtex` failed to parse file %s: %s' % (
            refs_file,
            str(e)))
        return

    publications = []
    publications_lists = {}
    publications_untagged = []

    split_by = None
    untagged_title = None

    if 'PUBLICATIONS_SPLIT_BY' in generator.settings:
        split_by = generator.settings['PUBLICATIONS_SPLIT_BY']

    if 'PUBLICATIONS_UNTAGGED_TITLE' in generator.settings:
        untagged_title = generator.settings['PUBLICATIONS_UNTAGGED_TITLE']

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

        tags = []
        if split_by:
            tags = entry.fields.get(split_by, None)

            # parse to list, and trim each string
            if tags:
                tags = tags.split(",")
                tags = list(map(str.strip, tags))

            # create keys in publications_lists if at least one
            # tag is given
            for tag in tags:
                publications_lists[tag] = publications_lists.get(tag, [])


        #render the bibtex string for the entry
        bib_buf = StringIO()
        bibdata_this = BibliographyData(entries={key: entry})
        Writer().write_stream(bibdata_this, bib_buf)
        text = formatted_entry.text.render(html_backend)

        entry_tuple = (key, year, text, bib_buf.getvalue(),
                       pdf, slides, poster)

        publications.append(entry_tuple)

        for tag in tags:
            publications_lists[tag].append(entry_tuple)

        if not tags and untagged_title:
            publications_untagged.append(entry_tuple)

    # append untagged list if title is given
    if untagged_title and publications_untagged:
        publications_lists[untagged_title] = publications_untagged


    # output
    generator.context['publications'] = publications
    generator.context['publications_lists'] = publications_lists



def register():
    signals.generator_init.connect(add_publications)
