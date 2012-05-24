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
from htmlutils import HTMLPage
import json
import logging
import unicodedata
import urllib2


class Crawler(object):
    """Follow the links on the current page and extract the text."""
    # Allowed and prohibited fragments in the urls to crawl.
    ALLOWED_EXTENSIONS = ['.com', '.fr', '.org', '.net', '.co.uk']
    PROHIBITED_FRAGMENTS = ['.png', '.jpg', '.JPG', '.exe', '.pdf', '.doc',
                            '.js', '.zip', '.tar', '.gz', '.msi', '.txt',
                            '.css', '.tiff', '.mp2', '.mp3', '.mp4', '.wav',
                            '.avi', '.mov', '.mpeg', '.ram', '.wmv', '.swf',
                            '.rar', '.aspx']
    BLACKLISTED_WORDS = ['shareit.com', 'sybase.com', 'gravatar', 'facebook',
                        'theme.wordpress.com', 'youtube.com', 'porn', 'sex',
                        'avventura', 'debtag', '.debian.org',
                        'launchpad.net', 'logon']
    # Filename of the file to which the url to crawl will be dumped at the end
    # of the crawling session and read from at the next restart session.
    FILENAME = 'crawler.json'

    def __init__(self, restart, seed=None):
        """
        Build a Crawler that will start crawling the web from the seed url and
        using a potentially already dumped list of urls to crawl.

        A seed url is optionnal when restarting a crawl session, however, when
        setting up a new crawling session (restart being False), a seed url is
        mandatory.
        """
        # Get a logger assuming that the logging facility has been set up by the
        # banana module.
        self._logger = logging.getLogger(__name__)

        if not seed and not restart:
            raise Exception('When building a Crawler for a new session (restart '
                            'being False), a seed url must be given.')

        # Set up the members.
        self._seed = None
        self._tocrawl = set([])
        self._crawled = set([])

        if seed:
            if not self.is_url_valid(seed):
                raise Exception('The given seed url is not valid in the '
                                'constructor of the Crawler.')
            self._seed = seed
        if restart:
            with open(Crawler.FILENAME) as fp:
                urls_to_crawl = json.load(fp)
                for url in urls_to_crawl:
                    self._tocrawl.add(url)
            self._logger.debug('Urls to crawl:\n' + str(self._tocrawl))

    def __del__(self):
        self._logger.debug('Deleting Crawler, dumping the urls to crawl.')
        self.dump(Crawler.FILENAME)

    def dump(self, filename):
        self._logger.info('Dumping the urls to crawl to \'%s\'.' % filename)
        try:
            self._logger.info('There are %d urls to crawl.' % len(self._tocrawl))
            with open(filename, 'w') as fp:
                json.dump(list(self._tocrawl), fp)
        except Exception as e:
            self._logger.warning(e)
            self._logger.warning('The Crawler seems to be malformed. '
                                'Nothing has been dumped.')

    def start(self, max_links=10):
        """
        Start the crawling. max_links is the maximum number of links to crawl.
        Default to 10 urls. This method is mainly for testing purpose.
        """
        crawl_counter = 0
        while crawl_counter < max_links:
            self.crawl()
            crawl_counter += 1

        # End of crawling, log crawled urls.
        with open('crawled','w') as fp:
            for url in self._crawled:
                fp.write(url + '\n')
        with open('tocrawl','w') as fp:
            for url in self._tocrawl:
                fp.write(url + '\n')

    def crawl(self):
        """
        Crawl the next link in the links to crawl stack and return an
        htmlutils.HTMLPage object.
        """
        try:
            # If this is the first link to crawl of the session and if a seed
            # url is present, use the seed url.
            crawling = None
            if not self._crawled and self._seed:
                crawling = self._seed
            else:
                crawling = self._tocrawl.pop()

            # DEBUG security check.
            if crawling in self._crawled:
                raise Exception("The crawling url %s was already crawled during this session!" % crawling)

            self._logger.info(crawling)
            if not self.is_url_valid(crawling):
                # Call recursively this method to crawl the next available url.
                self._logger.info('skipping url %s' % crawling)
                return self.crawl()

            # Read the page to a byte string, convert it to unicode and retrieve
            # the relevant information of the web page.
            html = urllib2.urlopen(crawling).read().decode('utf-8')
            page = HTMLPage(crawling, html)

            if page.title:
                self._logger.info(page.title)

            # Add the current url to the already crawled url's list.
            self._crawled.add(crawling)

            # Retrieve the external links on the page and add them
            # to the urls to crawl if they weren't already crawled.
            for link in page.links:
                if not link in self._crawled and self.is_url_valid(link):
                    self._tocrawl.add(link)

            return page

        except urllib2.HTTPError as e:
            self._logger.warning('HTTPError %d at url:%s' % (e.code, crawling))
            # Call recursively this method to crawl the next available url.
            return self.crawl()
        except urllib2.URLError as e:
            self._logger.warning('URLError at url: %s\n%s' % (crawling, e))
            # Call recursively this method to crawl the next available url.
            return self.crawl()
        except KeyError:
            self._logger.info('Reached the end of the web.')
            self._logger.debug(self._tocrawl)
            raise StopIteration
        except Exception as e:
            self._logger.error(e.message)
            # Call recursively this method to crawl the next available url.
            raise
            return self.crawl()

    def is_url_valid(self, url):
        """
        Check if the given url string does not contains prohibited fragments.
        """
        for word in Crawler.BLACKLISTED_WORDS:
            if word in url:
                self._logger.debug('Invalid url %s because of %s.' % (url, word))
                return False
        for fragment in Crawler.PROHIBITED_FRAGMENTS:
            if fragment in url:
                self._logger.debug('Invalid url %s because of %s.' % (url, fragment))
                return False
        is_valid = False
        for extension in Crawler.ALLOWED_EXTENSIONS:
            if extension in url:
                is_valid = True
        if not is_valid:
            self._logger.debug('Invalid url %s because none of the allowed extensions was found in it.' % url)
        return is_valid

