Pelican BibTeX
==============

Organize your scientific publications with BibTeX in Pelican. Original author is Vlad Niculae (http://vene.ro).
This project is forked from https://github.com/vene and provides support for multiple BibTeX files and slightly
more advanced sorting and displaying options.

*Note*: This code is unlicensed. It was not submitted to the `pelican-plugins`
official repository because of the license constraint imposed there.


Requirements
============

`pelican_bibtex` requires `pybtex`.

```bash
pip install pybtex
```

How to Use
==========

This plugin reads a user-specified BibTeX file and populates the context with
a list of publications, ready to be used in your Jinja2 template.

The plugin is configured as follows in ```pelicanconf.py```:

```python
PUBLICATIONS = {
  'pubs': { 'file': 'content/publications.bib' }
}
```

You will be able to find a `publications` variable in all templates. If the given
```file``` is present and readable, dictionary entries will also be accessible in the template.
Instead of a ```file``` entry, it will contain a ```data``` field containing the following tuple:

```
(key, year, text, bibtex, pdf, slides, poster)
```

1. `key` is the BibTeX key (identifier) of the entry.
2. `year` is the year when the entry was published.  Useful for grouping by year in templates using Jinja's `groupby`
3. `text` is the HTML formatted entry, generated by `pybtex`.
4. `bibtex` is a string containing BibTeX code for the entry, useful to make it
available to people who want to cite your work.
5. `pdf`, `slides`, `poster`: in your BibTeX file, you can add these special fields,
for example:
```
@article{
   foo13
   ...
   pdf = {/papers/foo13.pdf},
   slides = {/slides/foo13.html}
}
```
This plugin will take all defined fields and make them available in the template.
If a field is not defined, the tuple field will be `None`.  Furthermore, the
fields are stripped from the generated BibTeX (found in the `bibtex` field).

Advanced Configuration
======================

The configuration allows for multiple files and control over several appearance features like this:

```python
PUBLICATIONS = {
  'simple-example': { 'file': 'content/all.bib' },
  'modified-defaults': {
    'file': 'content/all.bib',
    'title': 'Different Appearance',
    'header': False,
    'split': False,
    'split_link': False,
    'bottom_link': False,
    'highlight': ['Patrick Holthaus'] }
}

PUBLICATIONS_NAVBAR = True
```

The following optional fields can be specified for each bibliography in the ```PUBLICATIONS``` variable:

* ```title```: Title for this bibliography (h2), if empty, the bibliographies key is used instead.
* ```header```: Bool denoting whether a header (h2) should be produced for this bibliography.
* ```split```: Bool denoting whether bibliographies should be split by year (h3).
* ```split_link```: Bool denoting whether to generate a "link to top" after each year's section.
* ```bottom_link```: Bool denoting whether to generate a "link to top" after this bibliography.
* ```highlight```: String, e.g., a name, that will be entailed in a \<strong\> tag to highlight.

The ```PUBLICATIONS_NAVBAR``` variable can be used to specify whether or not to produce a line that contains
links to each bibliography section.

Template Example
================

You probably want to define a 'publications.html' direct template.  Don't forget
to add it to the `DIRECT\_TEMPLATES` configuration key.  Note that we are escaping
the BibTeX string twice in order to properly display it.  This can be achieved
using `forceescape`.

```python
{% extends "base.html" %}
{% block title %}Publications{% endblock %}
{% block content %}

<script type="text/javascript">
    function disp(s) {
        var win;
        var doc;
        win = window.open("", "WINDOWID");
        doc = win.document;
        doc.open("text/plain");
        doc.write("<pre>" + s + "</pre>");
        doc.close();
    }
</script>
<section id="content" class="body">
    <h1 class="entry-title">Publications</h1>
    <ul>
    {% for key, year, text, bibtex, pdf, slides, poster in publications %}
    <li id="{{ key }}">{{ text }}
    [&nbsp;<a href="javascript:disp('{{ bibtex|replace('\n', '\\n')|escape|forceescape }}');">Bibtex</a>&nbsp;]
    {% for label, target in [('PDF', pdf), ('Slides', slides), ('Poster', poster)] %}
    {{ "[&nbsp;<a href=\"%s\">%s</a>&nbsp;]" % (target, label) if target }}
    {% endfor %}
    </li>
    {% endfor %}
    </ul>
</section>
{% endblock %}
```

Extending this plugin
=====================

A relatively simple but possibly useful extension is to make it possible to
write internal links in Pelican pages and blog posts that would point to the
corresponding paper in the Publications page.

A slightly more complicated idea is to support general referencing in articles
and pages, by having some BibTeX entries local to the page, and rendering the
bibliography at the end of the article, with anchor links pointing to the right
place.
