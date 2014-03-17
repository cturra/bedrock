"""
We need this command because some pages have Markdown-derived privacy notices.
For a better performance, we convert Markdown content to final HTML files during
deployment, and serve the cached static HTML files if possible.
"""

import os

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.test.client import Client, RequestFactory
from lib.l10n_utils.dotlang import get_lang_path, get_translations


CACHE_DIR = os.path.join(settings.ROOT, 'bedrock', 'privacy', 'caches')
TEMPLATES = {
    '/privacy/': 'privacy/index.html',
    '/privacy/facebook/': 'privacy/notices/facebook.html',
    '/privacy/firefox-os/': 'privacy/notices/firefox-os.html',
    '/privacy/firefox/': 'privacy/notices/firefox.html',
    '/privacy/websites/': 'privacy/notices/websites.html',
}


class Command(NoArgsCommand):
    help = 'Generate static HTML files for privacy notices.'

    def handle_noargs(self, **options):
        client = Client()
        request = RequestFactory().get('/')
        request.locale = settings.LANGUAGE_CODE

        for url, template in TEMPLATES.iteritems():
            # List the supported locales of the page
            locales = get_translations(get_lang_path(template))

            for locale in locales.iterkeys():
                cache_path = os.path.join(CACHE_DIR, locale, template)
                cache_dir = os.path.dirname(cache_path)

                # Create the destination directory first
                if not os.path.exists(cache_dir):
                    os.makedirs(cache_dir)

                # Save the rendered HTML as a static file
                try:
                    f = open(cache_path, 'w')
                    f.write(client.get('/' + locale + url + '?cache=0').content)
                    f.close()
                except IOError:
                    pass
