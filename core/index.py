#!/usr/bin/python
# Copyright 2012 Florent Galland
#
# This file is part of banana.
#
# banana is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
# banana is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with banana.  If not, see <http://www.gnu.org/licenses/>.
#-*- coding: utf-8 -*-
import blobprocessor
import json
import logging
import re
import time
import unicodedata
import unittest


class Index(object):
    """
    Represents an inverted index which can be searched, modified, saved and read
    back.
    """
    # Filename of the file to which the index will be dumped.
    FILENAME = 'index.json'

    def __init__(self, restart):
        """
        Make an empty index unless 'restart' is True, in that case load a
        previously dumped index from Index.FILENAME.
        """
        # Get a logger assuming that the logging facility has been set up by the
        # banana module.
        self._logger = logging.getLogger(__name__)

        # Indexed urls and their associated information such as id, length of
        # title and full text and the full text of the page itself.
        self._urls = {}

        self._title_index = InvertedIndex()
        self._full_text_index = InvertedIndex()

        # Index statistics.
        self._average_title_length = 0
        self._average_full_text_length = 0

        # Counter to periodically dump the index when entries are added. The
        # _dump_interval_counter is incremented at each time that an entry is added.
        self._dump_interval = 20
        self._dump_interval_counter = 0

        # Load the previously saved index if necessary.
        if restart:
            self.load(Index.FILENAME)

    def __del__(self):
        self._logger.debug('Deleting Index, dumping the index content.')
        self.dump(Index.FILENAME)

    def get_title_index(self):
        return self._title_index

    def get_full_text_index(self):
        return self._full_text_index

    def get_indexed_url_count(self):
        return len(self._urls)

    def get_title(self, url):
        """Get the title of the page associated with url."""
        return self._urls[url]['title']

    def make_snippet(self, url, tokens, context_before, context_after,
                    max_match_count):
        """
        Return a snippet of the full text of the url relevant with respect to
        the tokens.

        context_before and context_after are the number of tokens before and
        after the matching token that will be included in the snippet.
        max_match_count is the chosen maximum of matches that will be used to
        make the snippet. This is useful to avoid huge snippets when a token is
        matched several times in the full_text.
        The returned value is the snippet as a single string.
        """
        # Get the matching positions in the url full text.
        positions = []
        for token in tokens:
            positions += self._full_text_index.get_match_positions_in_url(url, token)

        # Extract snippets of the full text around the matching positions.
        snippet = []
        url_info = self._urls[url]
        for position in positions[0:max_match_count - 1]:
            # Compute the lower and upper bound of the snippet to extract from
            # the full_text. Pay attention to limit cases when position is close
            # to the start or end of the full_text.
            lower_bound = position - context_before
            if lower_bound < 0:
                lower_bound = 0
            upper_bound = position + context_after
            if upper_bound >= len(url_info['full_text']):
                upper_bound = len(url_info['full_text']) - 1
            # Append a slice of the full_text followed by an ellipsis to the snippet.
            # u'\u2026' is the unicode value of an ellipsis.
            snippet += url_info['full_text'].split()[lower_bound:upper_bound]
            snippet += u'\u2026'

        # Finally return the composed snippet as a single string.
        return ' '.join(snippet)

    def dump(self, filename, prettify=False):
        """
        Dumps the inverted index in a json format to 'filename'. The usual
        filename used is 'index.json'. If 'prettify' is True, the json is dumped
        in a more human readable format.
        """
        self._logger.info('Dumping the inverted index to \'%s\'.' % filename)
        self._logger.info('The index to dump contains %d entries.' % self._full_text_index.get_entry_count())
        self._logger.info('A total of %d urls are indexed.' % self.get_indexed_url_count())
        # Dump the attributes of the class in json. In the future, pickle or
        # shelve will be used, but for now json provides human readable data
        # nice for debugging.
        with open(filename, 'w') as fp:
            # Make a json serializable object representing the Index.
            json_to_dump = {'_urls': self._urls,
                    '_title_index': self._title_index.to_json(),
                    '_full_text_index': self._full_text_index.to_json(),
                    '_average_title_length': self._average_title_length,
                    '_average_full_text_length': self._average_full_text_length}
            if prettify:
                json.dump(json_to_dump, fp, sort_keys=True, indent=4)
            else:
                json.dump(json_to_dump, fp)

    def load(self, filename):
        """
        Load the index properly written by self.dump_index() in file
        corresponding to 'filename'. The usual filname used is 'index.json'.
        """
        self._logger.info('Loading the inverted index from \'%s\'.' % filename)
        with open(filename) as fp:
            loaded_json = json.load(fp)
            self._urls = loaded_json['_urls']
            self._title_index = InvertedIndex(loaded_json['_title_index'])
            self._full_text_index = InvertedIndex(loaded_json['_full_text_index'])
            self._average_title_length = loaded_json['_average_title_length']
            self._average_full_text_length = loaded_json['_average_full_text_length']
        self._logger.info('The loaded index contains %d entries.' % self._full_text_index.get_entry_count())
        self._logger.info('A total of %d urls are indexed.' % self.get_indexed_url_count())

    def add_entry(self, page):
        """
        Index a page represented by an htmlutils.HTMLPage object.
        """
        # self._logger.debug('Adding entry in index for url %s' % url)
        # If the url is already indexed, print when it was done and remove its
        # data from the indexes.
        if page.url in self._urls:
            delta_days = (time.time() - self._urls[page.url]['date']) / 86400
            self._logger.info('The url %s was already indexed %d days ago.' % (page.url, delta_days))
            self._title_index.remove_entry(page.url)
            self._full_text_index.remove_entry(page.url)

        # Index the title of the page in the _title_index.
        title_length = 0
        tokenized_title = []
        if page.title:
            title_length = len(page.title.split())
            tokenized_title = blobprocessor.make_tokens_and_position(page.title)
            for token_and_position in tokenized_title:
                self._title_index.add_entry(page.url, token_and_position[0],
                        token_and_position[1])
        else:
            self._logger.warning('Unable to get title from url \'%s\'' % page.url)

        # Index the full text of the page in the _full_text_index.
        # Try to get the text of the page, prepare it removing as much markup as
        # possible and tokenize it.
        blob = blobprocessor.remove_meaningless_chars(page.text)

        blob_length = 0
        tokens = []
        if blob:
            blob_length = len(blob.split())
            tokenized_blob = blobprocessor.make_tokens_and_position(blob)
            for token_and_position in tokenized_blob:
                self._full_text_index.add_entry(page.url, token_and_position[0],
                        token_and_position[1])
        else:
            self._logger.warning('Unable to get text from url \'%s\'' % page.url)

        # Save page info.
        url_info = self._urls.setdefault(page.url, {})
        # Url id. Notice that we've just inserted the entry corresponding to url
        # in _urls so its length has just been incremented.
        url_info['id'] = len(self._urls)
        # Indexing date in second since epoch.
        url_info['date'] = time.time()
        # Main title of the page.
        url_info['title'] = page.title
        # Number of tokens in the title of the page.
        url_info['title_length'] = title_length
        # Full text of the page in a string.
        # url_info['full_text'] = ' '.join((token for token in tokens))
        url_info['full_text'] = blob
        # Number of tokens in the whole page.
        url_info['full_text_length'] = blob_length

        # Update index statistics.
        self._average_title_length = (self._average_title_length +
                url_info['title_length'] / url_info['id'])
        self._average_full_text_length = (self._average_full_text_length +
                url_info['full_text_length'] / url_info['id'])

        # Now that the entry is added, increment the added entry count and dump
        # the index if necessary.
        self._dump_interval_counter += 1
        if self._dump_interval_counter >= self._dump_interval:
            self._dump_interval_counter = 0
            self.dump(Index.FILENAME)


class InvertedIndex(object):
    """
    An inverted index is a data set which links a term/word/token to all the
    urls which contains that term/word/token and in which position in the text.

    In practice, the inverted index is a dictionnary in which the keys are
    the terms. The values are the url and the position of the terms in the
    blob of text corresponding to the url:
    self._index = {
            'token': {
                'url': [first_position, second_position],
            },
            ...
        }
    """
    def __init__(self, json=None):
        """
        Build an empty InvertedIndex or initialize it from the optional json argument.

        Notice that no security check is done to make sure that json is valid.
        """
        self._index = {}
        if json:
            self._index = json

    def add_entry(self, url, token, position):
        """
        Add an entry in the InvertedIndex.

        position is an integer, position of the token in the blob of text
        corresponding to the url.
        """
        if not token in self._index:
            self._index[token] = {url: [position]}
        elif not url in self._index[token]:
            self._index[token][url] = [position]
        else:
            self._index[token][url].append(position)

    def remove_entry(self, url):
        """Remove the data associated with an url."""
        for urls in self._index.itervalues():
            if url in urls:
                del urls[url]

    def get_entry_count(self):
        return len(self._index)

    def get_urls_and_occurrences_for_token(self, token):
        """"
        Get the list of urls corresponding to token and the number of
        occurrences of the token in the page. If token is not present in the
        index, the returned list is empty
        """
        urls_and_occurrences = []
        if token in self._index:
            for url in self._index[token].keys():
                urls_and_occurrences.append(url, len(self._index[token][url]))
        return urls_and_occurrences

    def get_matching_urls(self, token):
        urls = set([])
        if token in self._index:
            for url in self._index[token].keys():
                urls.add(url)
        return urls

    def get_matching_urls_count(self, token):
        if token in self._index:
            return len(self._index[token])
        else:
            return 0

    def get_match_count_in_url(self, url, token):
        count = 0
        if token in self._index:
            if url in self._index[token]:
                count = len(self._index[token][url])
        return count

    def get_match_positions_in_url(self, url, token):
        """
        Return the list of matching positions of token in url.
        """
        match_positions = []
        if token in self._index:
            if url in self._index[token]:
                match_positions = self._index[token][url]
        return match_positions

    def to_json(self):
        return self._index

    def __str__(self):
        return str(self._index)

    def __repr__(self):
        return str(self.__dict__)

