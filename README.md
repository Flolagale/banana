##Banana search
Banana search, or more concisely Banana is an intent of a pure [Python] search engine, released under the terms of the [GNU Affero General Public License].
The aim is to provide a cross platform stand alone package that will allow anybody to run its own search engine right from its computer.
The implementation tries to be as concise and simple as possible, following the [KISS principle].
The Banana project provides a crawler (the Bananabot), an indexer, some scorers, and a searcher. It also comes with a command line interface and a web interface.
*It is now in a pretty rough pre-alpha state.*
###Why? Aren't the existing web search engines good enough?
Of course they are, but the aim of Banana is to avoid any logging, tracking or bubbling that the commercial web search engines can use. The other reason is because we have a lot of fun developing Banana.
###In what Banana is different from the existing open source search engines?
Banana is different because it comes as an installable stand-alone package. Some very good open source projects exist (for instance [Lucene]), allowing you to _develop_ your own search engine, based on their technology. The Banana project is meant to allow you to _easily install_ you engine, and it should work _out of the box_.
###Can I try it?
As soon as it will be sufficiently robust, a living instance of Banana search will be available.
###Why the GNU Affero General Public License?
The GNU [AGPLv3] licence is fully compatible with the GNU [GPLv3] license, adding a clause to fill a hole in the GPL for the software as a service utilisation. Indeed, the GPL does not ensures the copyleft if someone runs a modified GPL software on a server, without redistributing it. The AGPL makes mandatory to provide a link for downloading the source code from the web service page. See the dedicated page at the [Free Software Foundation] or on [Wikipedia] for additional information.
###Dependencies
Banana uses [Python 2.7], [Bottle 0.10.9] as lightweight web framework for the web interface and we plan to use [MongoDB] with the [PyMongo] driver for the index.
###Installation
Soon...

[Python]:http://www.python.org
[GNU Affero General Public License]:http://www.gnu.org/licenses/agpl.html
[KISS principle]:https://en.wikipedia.org/wiki/KISS_principle
[Lucene]:http://lucene.apache.org/
[AGPLv3]:http://www.gnu.org/licenses/agpl.html
[GPLv3]:http://www.gnu.org/licenses/gpl.html
[Free Software Foundation]:http://www.gnu.org/licenses/why-affero-gpl.html
[Wikipedia]:http://en.wikipedia.org/wiki/Affero_General_Public_License
[Python 2.7]:http://www.python.org
[Bottle 0.10.9]:http://bottlepy.org/docs/dev/
[MongoDB]:http://www.mongodb.org/
[PyMongo]:http://www.mongodb.org/display/DOCS/Python+Language+Center
