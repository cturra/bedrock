# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from lib import l10n_utils
import jingo
import os

from commonware.response.decorators import xframe_allow

from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse

from forms import PrivacyContactForm


CACHE_DIR = os.path.join(os.path.dirname(__file__), 'caches')


def get_response(request, template, context=None):
    """
    Some pages have Markdown-derived privacy notices. For a better performance,
    we convert Markdown content to final HTML files during deployment, and serve
    the cached static HTML files if possible.
    """
    if request.method == 'GET' and request.GET.get('cache', '1') == '1':
        try:
            locale = l10n_utils.get_locale(request)
            content = open(os.path.join(CACHE_DIR, locale, template)).read()
        except IOError:
            content = None

        if content:
            return HttpResponse(content)

    return l10n_utils.render(request, template, context)


def firefox_notices(request):
    return get_response(request, 'privacy/notices/firefox.html')


def firefox_os_notices(request):
    return get_response(request, 'privacy/notices/firefox-os.html')


def websites_notices(request):
    return get_response(request, 'privacy/notices/websites.html')


@xframe_allow
def facebook_notices(request):
    return get_response(request, 'privacy/notices/facebook.html')


def submit_form(request, form):
    form_submitted = False

    if form.is_valid():
        form_submitted = True
        form_error = False

        honeypot = form.cleaned_data.pop('superpriority')

        if honeypot:
            form_error = True
        else:
            subject = 'Message sent from Privacy Hub'
            sender = form.cleaned_data['sender']
            to = ['yourprivacyis#1@mozilla.com']
            msg = jingo.render_to_string(request, 'privacy/includes/email-info.txt', form.cleaned_data)
            headers = {'Reply-To': sender}

            email = EmailMessage(subject, msg, sender, to, headers=headers)
            email.send()
    else:
        form_error = True

    return {'form_submitted': form_submitted, 'form_error': form_error}


@csrf_protect
def privacy(request):
    form = PrivacyContactForm()

    form_submitted = False
    form_error = False

    if request.method == 'POST':
        form = PrivacyContactForm(request.POST)
        form_results = submit_form(request, form)

        form_submitted = form_results['form_submitted']
        form_error = form_results['form_error']

    template_vars = {
        'form': form,
        'form_submitted': form_submitted,
        'form_error': form_error,
    }

    return get_response(request, 'privacy/index.html', template_vars)
