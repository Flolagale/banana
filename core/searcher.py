#!/usr/bin/python
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
import blobprocessor
from index import Index
import logging
import math
import os
import sys


class Searcher(object):
    """
    Allows to search within an inverted index Index object from the index
    module.
    """
    def __init__(self, index=None, index_filename='index.json'):
        """
        Build a Searcher object.

        Parameters:
        index -- index.Index object. If given, attach this index to this
        searcher.
        index_filename -- If given, load the inverted index from the
        corresponding file. Default name to 'index.json'.

        """
        # Get a logger assuming that the logging facility has been set up by the
        # banana module.
        self._logger = logging.getLogger(__name__)

        # Set up other members.
        if index is not None:
            self._index = index
        else:
            if not os.path.exists(index_filename):
                self._logger.info('Unable to build the Searcher, '
                        'no index file %s in the current directory.' % index_filename)
                sys.exit(0)
            self._index = Index(index_filename)

    def query(self, query):
        # Make sure this is not an empty query.
        if not query:
            raise Exception('Invalid query \"%s\" in Searcher.query().' % query)
        #TODO add weights for the title and full text scores.
        tokenized_query = blobprocessor.make_tokens(query)
        self._logger.info('Tokenized query: %s' % ' '.join(tokenized_query))

        # Compute title relevance score.
        # Get urls with title matching query.
        matching_urls = set([])
        title_index = self._index.get_title_index()
        for token in tokenized_query:
            for url in title_index.get_matching_urls(token):
                self._logger.debug(self._index.get_title(url))
                matching_urls.add(url)

        urls_and_score = {}
        for url in matching_urls:
            score = self.compute_bm25_relevance(url, tokenized_query, title_index)
            self._logger.debug('Title score for url %s: %f' % (url, score))
            urls_and_score[url] = score

        # Compute full text relevance score.
        # Get urls with full text matching query.
        matching_urls = set([])
        full_text_index = self._index.get_full_text_index()
        for token in tokenized_query:
            for url in full_text_index.get_matching_urls(token):
                matching_urls.add(url)

        for url in matching_urls:
            score = self.compute_bm25_relevance(url, tokenized_query,
                                                full_text_index)
            self._logger.debug('Full text score for url %s: %f' % (url, score))
            if url in urls_and_score:
                urls_and_score[url] += score
            else:
                urls_and_score[url] = score

        # Sort the ranked urls.
        score_sorted_urls = sorted(urls_and_score.items(),
                                key=lambda (k,v):(v,k), reverse=True)
        self._logger.debug(score_sorted_urls)

        # Build the Answer objects that will be returned.
        answers = []
        context_before = 5
        context_after = 8
        max_match_count = 5
        for url_and_score in score_sorted_urls:
            url = url_and_score[0]
            score = url_and_score[1]

            title = self._index.get_title(url)
            title_highlights = self._find_highlights(tokenized_query, title)

            snippet = self._index.make_snippet(url, tokenized_query,
                                            context_before, context_after,
                                            max_match_count)
            snippet_highlights = self._find_highlights(tokenized_query, snippet)

            # Add an Answer object to the answers collection.
            answers.append(Answer(url, score, title, title_highlights, snippet,
                                    snippet_highlights))
        return answers

    def _find_highlights(self, tokens, snippet):
        """
        Build the highlights positions by parsing the given snippet.

        The parsing is case insensitive. These positions are useful for instance
        to highlight the matching words in the snippet.
        """
        highlights = []
        for token in tokens:
            for position, word in enumerate(snippet.split()):
                if token.lower() in word.lower():
                    highlights.append(position)
        return highlights

    def compute_bm25_relevance(self, url, query_tokens, index):
        """
        Compute the BM25 relevance score for a given url with respect to the
        tokens in query_tokens and the documents indexed in the InvertedIndex
        index.
        """
        # Some tweakable constants.
        k1 = 1.2
        BM25 = 0

        for token in query_tokens:
            n = index.get_matching_urls_count(token)
            N = index.get_entry_count()
            TF = index.get_match_count_in_url(url, token) # term frequency
            self._logger.debug('n: ' + str(n))
            self._logger.debug('N: ' + str(N))
            self._logger.debug('TF: ' + str(TF))

            # Compute the relevance only of the token can be found in the url text.
            if TF > 0:
                IDF = math.log((N - n + 1.0) / n) / math.log(1.0 + N) # inverse document frequency
                BM25 = BM25 + TF * IDF / (TF + k1)

        BM25 = 0.5 + BM25 / (2.0 * len(query_tokens))
        return BM25


class Answer(object):
    """
    Answer from a search query.

    Contains a relevant url, the relevance score, the page title, a list of
    integers containing which words to highlight in the title, a snippet of
    matching text and finally a list of integers containing which words to
    highlight in the snippet.
    """
    def __init__(self, url, score, title, title_highlights, snippet,
                snippet_highlights):
        self.url = url
        self.score = score
        self.title = title
        self.title_highlights = title_highlights
        self.snippet = snippet
        self.snippet_highlights = snippet_highlights

