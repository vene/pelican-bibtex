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

import os.path

import re

__version__ = '0.2.1'


def add_publications(generator):
    """
    Populates context with a list of BibTeX publications.

    Configuration
    -------------
    generator.settings['PUBLICATIONS']:
        Dictionary that contains bibliographies:
          The key denotes the bibliographies name to use in headers
          The values describe the BibTeX files to read
        Mandatory for this plugin.
    generator.settings['PUBLICATIONS_NAVBAR']:
        Bool denoting whether a navigation bar containing links to each bibliography should be produced.
        Defaults to 'True'.
    generator.settings['PUBLICATIONS_HEADER']:
        Bool denoting whether a header (h2) should be produced for each bibliography.
        Defaults to 'True'.
    generator.settings['PUBLICATIONS_SPLIT']:
        Bool denoting whether bibliographies should be split by year (h3).
        Defaults to 'True'.
    generator.settings['PUBLICATIONS_HIGHLIGHTs']:
        String, e.g., a name, that will be entailed in a <strong> tag to highlight.
        Default: empty

    Output
    ------
    generator.context['publications']:
        Dictionary containing the name of the publication list a a key, bibliography entries as a value.
        A bibliography entry contains of a list of tuples (key, year, text, bibtex, pdf, slides, poster).
        See Readme.md for more details.
    """

    if 'PUBLICATIONS' not in generator.settings:
        return
    if 'PUBLICATIONS_NAVBAR' not in generator.settings:
        generator.context['PUBLICATIONS_NAVBAR'] = True

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

    for rid in refs:
        ref = refs[rid]
        bibfile = os.path.join(generator.settings['PATH'], ref['file'])
        try:
            bibdata_all = Parser().parse_file(bibfile)
        except PybtexError as e:
            logger.warn('`pelican_bibtex` failed to parse file %s: %s' % (
                bibfile,
                str(e)))
            return

        if 'title' in ref:
            title = ref['title']
        else:
            title = rid

        if 'header' in ref:
            header = ref['header']
        else:
            header = True

        if 'split' in ref:
            split = ref['split']
        else:
            split = True

        if 'split_link' in ref:
            split_link = ref['split_link']
        else:
            split_link = True

        if 'bottom_link' in ref:
            bottom_link = ref['bottom_link']
        else:
            bottom_link = True

        if 'all_bibtex' in ref:
            all_bibtex = ref['all_bibtex']
        else:
            all_bibtex = False

        if 'highlight' in ref:
            highlights = ref['highlight']
        else:
            highlights = []

        if 'group_type' in ref:
            group_type = ref['group_type']
        else:
            group_type = False

        publications = []

        # format entries
        plain_style = plain.Style()
        html_backend = html.Backend()
        formatted_entries = plain_style.format_entries(bibdata_all.entries.values())

        for formatted_entry in formatted_entries:
            key = formatted_entry.key
            entry = bibdata_all.entries[key]
            year = entry.fields.get('year')
            typee = entry.type

            if entry.fields.get('tags'):
              tags = [tag.strip() for tag in entry.fields.get('tags').split(';')]
            else:
              tags = []

            if entry.fields.get('supplements'):
              supplements = [tag.strip() for tag in entry.fields.get('supplements').split(';')]
            else:
              supplements = []

            display_tags = [x for x in tags if x != "doi-open" and x != "url-open"]

            # This shouldn't really stay in the field dict
            # but new versions of pybtex don't support pop
            pdf = entry.fields.get('pdf', None)
            slides = entry.fields.get('slides', None)
            poster = entry.fields.get('poster', None)
            doi = entry.fields.get('doi', None)
            url = entry.fields.get('url', None)


            #clean fields from appearing in bibtex and on website
            entry_tmp = entry
            for to_del in ['pdf', 'slides', 'poster', 'tags', 'supplements']:
              entry_tmp.fields.pop(to_del, None)

            #render the bibtex string for the entry
            bib_buf = StringIO()
            bibdata_this = BibliographyData(entries={key: entry_tmp})
            Writer().write_stream(bibdata_this, bib_buf)

            #clean more fields from appearing on website
            for to_del in ['doi', 'url']:
              entry_tmp.fields.pop(to_del, None)

            entry_clean = next(plain_style.format_entries(bibdata_this.entries.values()), None)

            # apply highlight (strong)
            text = entry_clean.text.render(html_backend)
            for replace in highlights:
              text = text.replace(replace, '<strong>' + replace + '</strong>')

            publications.append((key,
                                typee,
                                year,
                                text,
                                tags,
                                display_tags,
                                supplements,
                                bib_buf.getvalue(),
                                pdf,
                                slides,
                                poster,
                                doi,
                                url))

        generator.context['publications'][rid] = {}
        generator.context['publications'][rid]['title'] = title
        generator.context['publications'][rid]['path'] = os.path.basename(bibfile)
        generator.context['publications'][rid]['header'] = header
        generator.context['publications'][rid]['split'] = split
        generator.context['publications'][rid]['bottom_link'] = bottom_link
        generator.context['publications'][rid]['split_link'] = split_link
        generator.context['publications'][rid]['all_bibtex'] = all_bibtex
        generator.context['publications'][rid]['data'] = collections.OrderedDict()
        if group_type:
          generator.context['publications'][rid]['data'] = sorted(publications,
                                                                  key=lambda pub: (
                                                                      -int(
                                                                          pub[2].
                                                                          replace("in press", "9900").
                                                                          replace("under review", "9901")
                                                                      ),
                                                                      pub[1]))
        else:
          generator.context['publications'][rid]['data'] = sorted(publications,
                                                                  key=lambda pub: 
                                                                      -int(
                                                                          pub[2].
                                                                          replace("in press", "9900").
                                                                          replace("under review", "9901")
                                                                        ))

def register():
    signals.generator_init.connect(add_publications)
