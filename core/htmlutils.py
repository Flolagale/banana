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
from HTMLParser import HTMLParser
import logging
import urllib2
import urlparse


class HTMLPage(object):
    """
    Represent an HTML page, with the relevant information for banana easily available.

    The text is provided as is, this means that you might need to remove spaces
    and line breaks.
    """
    def __init__(self, url, html):
        """
        Build an html page representation from its url and its html code
        converted to unicode.
        """
        # Run the parser on the page and get the relevant info.
        parser = BananaHTMLParser()
        parser.parse(html)

        # Fill the members with the retrieved data.
        # The url of the page.
        self.url = url

        # Get all the external links.
        self.links = set([])
        parsed_url = urlparse.urlparse(url)
        for link in parser.links:
            if link.startswith('#'):
                # Do not save internal links.
                continue
            if link.startswith('/'):
                self.links.add('http://' + parsed_url[1] + link)
            elif not link.startswith('http'):
                self.links.add('http://' + parsed_url[1] + '/' + link)

        # The title of the page.
        self.title = parser.title

        # The full text of the page.
        self.text = parser.text


class MalformedHTMLException(Exception):
    pass


class BananaHTMLParser(HTMLParser):
    """
    Parse an html document under the form of a string and extract information
    relevant for Banana from it.

    The stored in formation contains the raw links as they are found in the html
    (so you might need to build their full url by prepending the domain name to
    them), the title of the page and the full text of the page.
    Usage:
    parser = BananaHTMLParser()
    parser.parse(myHTMLString)
    parser.links()
    TODO Add support for meta tags keywords and description.
    """
    LINK_TAG = 'a'
    TITLE_TAG = 'title'
    TEXT_TAGS = set(['p', 'h1', 'h2', 'h3', 'h4', 'h5'])

    def __init__(self):
        HTMLParser.__init__(self)

        # Get a logger assuming that the logging facility has been set up by the
        # banana module.
        self._logger = logging.getLogger(__name__)

        self._tags_stack = []
        self._current_tag = None
        # Flag use to detect titles that contain only a link, like the following
        # pattern: <h1><a href='/about'>about</a></h1>
        # So _is_first_chunk_of_text_data is set to False by the first handled data
        # of the current tag.
        self._is_first_chunk_of_text_data = True

        # Public page information.
        # TODO set this as properties to avoid external modifications.
        self.links = []
        self.title = ''
        self.text = ''

    def parse(self, html):
        """
        Use this method rather than the feed() method. html is the html code to
        parse, converted to unicode. The relevant information of the page is
        available through the public members.
        """
        # First re-initialize the object data.
        self.links = []
        self.title = ''
        self.text = ''

        # Tricky undocumented method of HTMLParser to keep the html entities
        # characters.
        html =  self.unescape(html)
        # Parse the html code.
        try:
            self.feed(html)
        except HTMLParser.HTMLParseError as e:
            raise MalformedHTMLException(e)

    def handle_starttag(self, tag, attrs):
        self._current_tag = tag
        self._tags_stack.append(tag)
        # Handle the links.
        if tag == BananaHTMLParser.LINK_TAG:
            # Find the href attribute.
            for attr in attrs:
                if attr[0] == 'href':
                    # Store the link.
                    self.links.append(attr[1])
                    break
        # If the opened flag is a text flag, update the first text data flag
        # accordingly.
        if tag in BananaHTMLParser.TEXT_TAGS:
            self._is_first_chunk_of_text_data = True

    def handle_endtag(self, tag):
        # Check the the end tag matches the current tag. If not, the html is
        # malformed. In this case, try to close the open tag corresponding to
        # the end tag that is the nearest in the tags stack. If it is not
        # possible, then raise an exception.
        if tag != self._current_tag:
            self._logger.debug('The end tag %s does not match the current tag %s. '
                'Try to find a corresponding open tag.' % (tag, self._current_tag))
            self._logger.debug('Current html context:\n' + str(self._tags_stack))
            # Iterate on the tags stack in reverse order. Use an enumerate()
            # trick to also know the current index in the original list. Then if
            # found, save the index at which the first open tag matching the
            # closing tag is found.
            matching_index = None
            for index, open_tag in reversed(list(enumerate(self._tags_stack))):
                if open_tag == tag:
                    self._logger.debug('Found a matching open tag at index %d' % index)
                    matching_index = index
                    break
            if matching_index is not None:
                # A matching open tag was found, update the tag stack.
                self._tags_stack = self._tags_stack[:matching_index]
                self._logger.debug('Updated html context:\n' + str(self._tags_stack))
            else:
                self._logger.debug('No matching open tag was found. Try to continue.')
                # raise MalformedHTMLException('The end tag %s does not match '
                                # 'the current tag %s' % (tag, self._current_tag))
        else:
            self._tags_stack.pop()
        # Update the current tag.
        if self._tags_stack:
            self._current_tag = self._tags_stack[-1]
        else:
            self._current_tag = None

    def handle_data(self, data):
        # Handle the title.
        if self._current_tag == BananaHTMLParser.TITLE_TAG:
            # There must be only one title in the page, so make sure this is the
            # first time we find a title tag.
            if self.title:
                self._logger.error('Several \'title\' tags on the page:')
                self._logger.error(self.title)
                self._logger.error(data)
                self._logger.error(self._tags_stack)
                raise MalformedHTMLException('Several \'title\' tags on the page.')
            self.title = data

        # Handle the text. If the current context is a text context, the current
        # data is some text, so store it.
        elif self._is_text_context():
            # Also verify that this is not a single link in a title pattern with
            # _is_first_chunk_of_text_data.
           if not (self._current_tag == BananaHTMLParser.LINK_TAG and self._is_first_chunk_of_text_data):
                # Add a space separator at the end of data.
                self.text += data + u' '
                # We handled some text data, so update the flag accordingly.
                self._is_first_chunk_of_text_data = False

    def _is_text_context(self):
        """
        A text context means that a TEXT_TAGS can be found in the curent tags stack.
        """
        return bool(set(self._tags_stack) & BananaHTMLParser.TEXT_TAGS)


def main():
    """Method used for testing."""
    # url = 'http://www.liberation.fr'
    url = 'http://www.python.org'
    html =('<html><head><title>Test</title></head>' +
        '<body><h1>Parse me!</h1><img src="toto" />' +
        '<form id="titi"><input type="text" /></body></html>')
    # html = urllib2.urlopen(url).read().decode('utf-8')
    page = HTMLPage(url, html)

    print(page.title)
    print(page.text)
    print(page.links)

if __name__ == '__main__':
    main()

