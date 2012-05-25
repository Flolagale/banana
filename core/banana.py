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
from crawler import Crawler
from index import Index
import logging
from searcher import Searcher


class Banana(object):
    """
    Singleton allowing the high level manipulation of the Banana search project.
    Mainly, it allows crawling and searching the web.
    """
    class __Banana(object):
        """Private nested class containing the Banana implementation."""
        def __init__(self):
            """
            In this constructor, mainly set up the logging facility for all the
            Banana modules.
            """
            # Set up logging for the crawler. Log both to the console and a file.
            logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='banana.log',
                    filemode='w')
            # Define a Handler which writes INFO messages or higher to the sys.stderr
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            # Set a format which is simpler for console use
            formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
            # formatter = logging.Formatter('%(message)s')
            # Tell the handler to use this format
            console.setFormatter(formatter)
            # Add the handler to the root logger
            logging.getLogger('').addHandler(console)
            # Get the logger.
            self._logger = logging.getLogger(__name__)

            # Member to cache the index. This member is at first None and will
            # be allocated in the search method.
            # TODO Note this is alittle bit hacky, this is a temporary fix to
            # improve speed by avoiding loading the index at each search query
            # when using the web interface. This should no more be necessary
            # when we will move to a real database.
            self._index = None

        def crawl(self, restart, seed=None):
            """
            Crawl the web starting from the seed url and using a potentially already
            dumped list of urls to crawl.

            A seed url is optional when restarting a crawl session, however, when
            setting up a new crawling session (restart being False), a seed url is
            mandatory.
            """
            # Build a Crawler that will start crawling from the seed.
            crawler = Crawler(restart, seed)

            # Build an Index. If restart is True, this will append data to the
            # existing index in the current directory.
            index = Index(restart)
            try:
                for i in xrange(1000): # ================================
                    page = crawler.crawl()
                    index.add_entry(page)
            except StopIteration:
                pass

        def search(self, query):
            """
            Search in the index for answer to query and return a list of relevant
            urls.
            """
            self._logger.info('query: ' + query)

            # If not already allocated, build an index here, restarting from a
            # previously dumped one.
            if self._index is None:
                restart = True
                self._index = Index(restart)

            # Build a searcher using this index.
            searcher = Searcher(self._index)
            return searcher.query(query)

    # The instance reference.
    __instance = None

    def __init__(self):
        """Create the singleton instance."""
        # Create the instance if it does not already exists.
        if not Banana.__instance:
            Banana.__instance = Banana.__Banana()

    def __getattr__(self, attr):
        """Delegate access to the __Banana implementation."""
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """Delegate access to the __Banana implementation."""
        return setattr(self.__instance, attr, value)


class Version(object):
    """
    Object representing the current version of the Banana project.
    """
    major = 0
    minor = 1
    micro = 0

    @staticmethod
    def to_string():
        return (str(Version.major) + '.' + str(Version.minor) + '.' +
                str(Version.micro))

