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
import argparse
from core.banana import Banana, Version
import web.bananaweb


def _search(args):
    """
    Internal module level method directly called by the argparse argument parse.
    """
    if not args.query:
        raise Exception('Unable to perform a search for an empty query.')

    # Build the full query concatenating the query terms.
    full_query = ' '.join(args.query).strip()

    # Get the answer of the searcher to this query.
    banana = Banana()
    answers = banana.search(full_query)

    # Print the answer to the user.
    print('\nBanana searched!\n\"%s\"?' % full_query)
    for answer in answers:
        print('\n' + answer.title + '\n' +
            'Scored ' + str(answer.score) + '\n' +
            answer.url + '\n' +
            answer.snippet)


def _crawl(args):
    """
    Internal module level method directly called by the argparse argument parse.
    """
    banana = Banana()
    banana.crawl(args.restart, args.seed)


def _web_start(args):
    """
    Internal module level method directly called by the argparse argument parse.
    """
    web.bananaweb.run_webapp()


def main():
    # Create the top level parser and the subparsers container for the subparsers
    # dedicated to the 'crawl' and 'search' commands.
    parser = argparse.ArgumentParser(description='A Banana web crawler, indexer and searcher.')
    parser.add_argument('--version', action='version',
                        version='This is %(prog)s version ' + Version.to_string())
    subparsers = parser.add_subparsers(help='banana sub-commands.')

    # Create the parser for the 'crawl' command.
    parser_crawl = subparsers.add_parser('crawl', help='Crawl the web.')
    parser_crawl.set_defaults(function=_crawl)
    parser_crawl.add_argument('-r', '--restart', action='store_true',
            help='Restart a crawling session from a previously dumped one in the '
            'current directory.')
    parser_crawl.add_argument('-s', '--seed', type=str,
            help='The url from which the crawler will start, '
            'for instance http://myseedurl.org.')

    # Create the parser for the 'search' command.
    parser_search = subparsers.add_parser('search', help='Search the web.')
    parser_search.set_defaults(function=_search)
    parser_search.add_argument('query', nargs='+', type=str, help='The search query.')

    # Create the parser for the 'webstart' comand.
    parser_web = subparsers.add_parser('webstart', help='Start the web interface of Banana, serving on localhost:8000.')
    parser_web.set_defaults(function=_web_start)

    # Really parse the script arguments.
    args = parser.parse_args()

    # Call the function defined by set_defaults.
    args.function(args)


if __name__ == '__main__':
    main()

