# -*- coding: utf-8 -*-

"""Project version info."""

__version__ = '{{ cookiecutter.version }}'
__version_info__ = (
    [
        int(num) if num.isdigit() else num
        for num in __version__.replace('-', '.', 1).split('.')
    ],
)
