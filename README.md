# Web Maker

Static site generator.


# Installation

Simply run:

    $ pip install -e .


# Usage

To use it:

    $ web-maker --help


# Template Functions

## `url`

`url_lookup(file_location: str) -> str`

Given a path to a file in the project directory, return the equivalent URL path in the generated site's file.

```jinja
* [Home]({{ url('content/index.md') }})
* [Test]({{ url('content/test.md') }})
```

The above outputs hyperlinks.

```html
<ul>
  <li>
    <a href="http://example.com/index.html">Home</a>
  </li>
  <li>
    <a href="http://example.com/test.html">Test</a>
  </li>
</ul>
```

## `list_pages`

`list_pages(glob_pathname: str) -> Generator[dict, None, None]`

Iterates over content page files contained in the content directory.

```jinja
{% for page in list_pages('**/*.md') %}
* {{ page.meta.title }} - {{ url(page.file_path) }}
{% endfor %}
```
