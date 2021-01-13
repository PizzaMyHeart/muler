#!/usr/bin/python3
"""Regex to remove [] tags in strings returned from queries

Note that Pharm.pd for DB00065 contains an extraneous '[' that
needs to be removed by manually updating via sqlite3. 


"""

import re


def drop_tags(original):
    '''
    Remove [] tags in returned strings and leading whitespace 
    before periods.
    '''
    brackets = re.compile('\[.*?\]')
    period = re.compile(' \.')

    original = brackets.sub('', original)
    original = period.sub('.', original)

    return original
