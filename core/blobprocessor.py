#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2012 Florent Galland
#
# This file is part of Banana Search.
#
# Banana Search is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
# Banana Search is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Banana Search. If not, see <http://www.gnu.org/licenses/>.
import re


"""
Module providing Utilies to process blobs of text in text indexing/searching context.
"""


STOP_WORDS = set([
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by',
        'for', 'if', 'in', 'into', 'is', 'it',
        'no', 'not', 'of', 'on', 'or', 's', 'such',
        't', 'that', 'the', 'their', 'then', 'there', 'these',
        'they', 'this', 'to', 'was', 'will', 'with',
        'le', 'la', 'les', 'est', 'et', 'a', 'à', 'un', 'une',
        'des', 'pour', 'par', 'l'
        ])
PUNCTUATION_PATTERN = re.compile(r'[-~`!@#$%^&*()+={}\[\]|\\:;"\',<.>/?]')
VALID_WORD_PATTERN = re.compile(r'^[a-zA-Z]+$')
MULTIPLE_SPACES_PATTERN = re.compile(r'\s{2,}')
MEANINGLESS_CHARS_PATTERN = re.compile(r'[\t\n\r\f\v]')


def make_tokens_and_position(blob):
    """
    From a given Unicode blob of text, return the corresponding list of
    tuples containing the preprocessed tokens and their position in the
    original blob.

    To do that, lower case the blob, strip punctuation, split by words, get
    rid of stop words, validate that each obtained word matches the
    Indexer.VALID_WORD_PATTERN regular expression.
    """
    tokens = []
    for position, word in enumerate(blob.lower().split()):
        # Remove punctuation. Handle the typical case: "l'avoir" as "l avoir",
        # which are 2 tokens!
        punctuation_free_word = PUNCTUATION_PATTERN.sub(' ', word)
        for token in punctuation_free_word.split():
            if not token.strip() in STOP_WORDS:
                tokens.append((token.strip(), position))
    return tokens


def make_tokens(blob):
    """
    From a given Unicode blob of text, return the corresponding list of tokens.

    To do that, lower case the blob, strip punctuation, split by words, get
    rid of stop words, validate that each obtained word matches the
    Indexer.VALID_WORD_PATTERN regular expression.
    """
    return zip(*make_tokens_and_position(blob))[0]


def remove_meaningless_chars(blob):
    """
    Remove the meaningless spaces (such as \\n, \\t) of
    the given blob. Use as (remember strings are immutable):
    blob = remove_markup(blob)
    """
    blob = MEANINGLESS_CHARS_PATTERN.sub(' ', blob)
    return MULTIPLE_SPACES_PATTERN.sub(' ', blob)

