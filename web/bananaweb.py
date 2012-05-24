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
from core.banana import Banana
from bottle import run, debug, request, route, view, static_file
import logging


def run_webapp():

    @route('/', method='GET')
    @view('search_template')
    def search_page():
        """Main search page."""
        query = request.GET.get('query', '').strip()
        # Convert query to unicode.
        query = query.decode('utf-8')
        log.info('Web query: ' + query)
        answers = []
        if query:
            banana = Banana()
            answers = banana.search(query)
        return dict(answers=answers)

    @route('/static/<filepath:path>')
    def server_static(filepath):
        """Serve static files (css for instance)."""
        log.info(filepath)
        return static_file(filepath, root='./static')

    log = logging.getLogger(__name__)
    debug(True)
    run(host='localhost', port=8000, reloader=True)
    # run(host='localhost', port=8000)

