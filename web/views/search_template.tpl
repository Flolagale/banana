<!doctype html>
<!--[if lt IE 7]> <html class="no-js lt-ie9 lt-ie8 lt-ie7" lang="en"> <![endif]-->
<!--[if IE 7]>    <html class="no-js lt-ie9 lt-ie8" lang="en"> <![endif]-->
<!--[if IE 8]>    <html class="no-js lt-ie9" lang="en"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js" lang="en"> <!--<![endif]-->
<head>
  <meta charset="utf-8">

  <title>Banana search &mdash; the GPL search engine</title>
  <meta name="description" content="Banana search is a pure python GPl search engine">

  <!-- Mobile viewport optimized: h5bp.com/viewport -->
  <meta name="viewport" content="width=device-width">

  <!-- Place favicon.ico and apple-touch-icon.png in the root directory: mathiasbynens.be/notes/touch-icons -->

  <link rel="stylesheet" href="static/css/search.css">

  <!-- More ideas for your <head> here: h5bp.com/d/head-Tips -->

</head>

<body id="index" class="home">
    <header id="searcher" class="body">
    <h1><em>Banana search</em></h1>
    <form action="/" method="GET">
        <input type="text" size="80" maxlength="80" name="query">
        <input type="submit" name="search" value="Search">
    </form> 
    </header><!-- /#banner -->

    <section id="content" class="body">
    <ol id="results-list" class="results-list">
%if answers:
    %for answer in answers:
        <li><article class="result">
        <header>
        <h3 class="result-title">
            <a href="{{answer.url}}" rel="result-link" title="Link to the result url">
            %for position, word in enumerate(answer.title.split()):
                %if position in answer.title_highlights:
                    <em>{{word}}</em>
                %else:
                    {{word}}
                %end
            %end
            </a>
        </h3>
        </header>

        <footer class="result-info">
        <h5 class="result-url">{{answer.url}}</h5>
        <h5 class="result-score">score: {{answer.score}}</h5>
        </footer><!-- /.result-info -->

        <div class="result-snippet">
        <p>
        %for position, word in enumerate(answer.snippet.split()):
            %if position in answer.snippet_highlights:
                <strong>{{word}}</strong>
            %else:
                {{word}}
            %end
        %end
        </p>
        </div><!-- /.result-snippet -->
        </article></li>
    %end
%end
    </ol><!-- /#results-list -->
    </section><!-- /#content -->

    <footer id="contentinfo" class="body">
    <address id="about" class="about-body">
        <span class="banana-description">
            Banana is a pure python web search solution released under the GNU General Public License. It includes a crawler, an indexer and a searcher. It can be used both from its command line and web interfaces. Finally, it is meant to be distributed as a standalone package.
            </span>
        </address><!-- /#about-body -->
        <p> caoutchoux 2012 </p>
        </footer><!-- /#contentinfo -->

    <!-- JavaScript at the bottom for fast page loading -->

</body>
</html>
