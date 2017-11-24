# `pylint-shortcodes`

* [GH Pages Index](https://wizardsoftheweb.github.io/pylint-shortcodes/)
* [Raw `--list-msgs`](/raw)
* [HTML Output](/dist/html)

## Overview

I got really tired of constantly Googling `pylint` codes. `pylint --list-msgs | grep` wasn't much faster. All I wanted to do was find a quick, easily searchable reference with all the error codes and their more descriptive names.

Using the modules for `virtualenv` and `pip`, I programmatically installed every possible version of `pylint`. I then ran `pylint --list-msgs` and parsed the output, sending it to templates via `jinja2`. The pages are formatted via jQuery and DataTables. I included a link to PyLint Messages, the website I used the most trying to find a quick reference.

I slapped this together in a couple of hours. Calling the source a train wreck is an insult to trains everywhere. I might touch this later, but I might not. There's probably a better way to do this natively in Python, and there's most definitely a more elegant way to do it.

## Useful links

    * [`virtualenv`](https://github.com/pypa/virtualenv)
    * [`pip`](https://github.com/pypa/pip)
    * [`jinja2`](https://github.com/pallets/jinja)
    * [jQuery](https://github.com/jquery/jquery)
    * [DataTables](https://github.com/DataTables/DataTables)
    * [PyLint Messages](https://pylint-messages.wikidot.com/start)
