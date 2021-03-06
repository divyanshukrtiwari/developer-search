from urllib.error import HTTPError
import tldextract
from decouple import config
from rapidfuzz import fuzz
from googleapiclient.discovery import build
from urllib.parse import urlencode


def keyword_in_search(search_item, keywords=()):
    """ whether `keyword` is present in `search_item` """

    link = search_item['link']
    title = search_item['title']
    snippet = search_item['snippet']

    for information in (link, title, snippet):

        if any(
            # normal search
            keyword.lower() in information.lower() for keyword in keywords
        ):
            return True

        if any(
            # fuzzy search
            fuzz.WRatio(keyword, information, score_cutoff=90) for keyword in keywords
        ):

            return True

    return False


def domain_in_search(search_item, domains=()):
    """ whether `search_item` is a result from provided `domains`  """

    link = search_item['link']

    if len(domains) == 0:
        # if no domains are provid  ed then return True
        # i.e: Let it appear on search

        return True

    else:
        for domain in domains:
            required_domain = tldextract.extract(domain).domain
            search_result_domain = tldextract.extract(link).domain

            if required_domain == search_result_domain:
                return True


def classify_search(search_items, titles_and_details={}):
    """ gives a dict which contains list of `search_items` in their respective categories"""

    search_data = {
        'all': search_items,
    }

    for title, details in titles_and_details.items():

        keywords = details.get('keywords', ())
        domains = details.get('domains', ())

        def filter_domains(search_item):
            """ to filter all the `search_item`s which are from `domains` """

            return domain_in_search(search_item, domains)

        def filter_keywords(search_item):
            """ to filter all the `search_item`s which contains `keyword` """

            return keyword_in_search(search_item, keywords)

        # filtering all results which contains `keyword`
        keywords_filtered = list(
            filter(
                filter_keywords,
                search_items
            )
        )

        # filtering all results which are from `domain`

        domains_filtered = list(
            filter(
                filter_domains,
                search_items
            )
        )

        search_data[title] = domains_filtered + keywords_filtered

    return search_data


def theme_filter(theme):

    return {
        "light": "light",
        "dark": "dark",
    }.get(theme, "light")


def get_current_theme(request):
   return request.session.get("theme")


def get_requested_theme(request):

    return request.GET.get("theme", None)


def set_new_theme(request, theme):

    theme = theme_filter(theme)
    request.session["theme"] = theme
    request.session.set_expiry(43800)


def get_theme_url(request, query, theme):
    return request.path + "?" + urlencode({
        "q": query,
        "theme": theme
    })
    

def perform_search(search_query):
    """ calls the CSE engine api to perform search and then classifies the results into appropriate categories"""

    API_KEY = config('API_KEY')
    CSE_KEY = config('CSE_KEY')

    limit_reached = False
    result = {}

    if search_query:
        try:
            # calling api
            resource = build("customsearch", 'v1', developerKey=API_KEY).cse()
            result = resource.list(q=search_query, cx=CSE_KEY).execute()
        except:
            result = {}
            limit_reached = True

    original_search_data = result
    search_items = original_search_data.get('items', [])

    # all the categories and the keywords of that categories

    search_data = classify_search(search_items, {
        'youtube': {
            'keywords': ("youtube.com", "youtube",),
            'domains': ('youtube.com',)
        },
        'courses': {
            'keywords': ("courses", "course",),
            'domains': ('udemy.com', "udacity.com", "coursera.com")
        },
        'tutorials': {
            'keywords': ("tutorials", "tutorial", "get started", ),
            'domains': ("tutorialspoint.com")
        },
        'docs': {
            'keywords': ("docs", "documentation", "official documentation"),
            'domains': ()
        },
        'github': {
            'keywords': ("git", "github", "github link"),
            'domains': ("github.com", )
        },
    })

    return search_data, limit_reached
