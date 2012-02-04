import urlparse

from django.test import TestCase
from django.conf import settings
from django.http import HttpResponseRedirect, HttpRequest

from facetools.middleware import FacebookRedirectMiddleware, GET_REDIRECT_PARAM

class FacebookRedirectMiddlewareTests(TestCase):

    def test_response_and_request(self):
        expected_results = [
            ("/canvas/view", "/view"),
            ("/canvas/view#fragment", "/view#fragment"),
            ("/canvas/view/", "/view/"),
            ("/canvas/view/#fragment", "/view/#fragment"),
            ("/canvas/view/?hi=hey", "/view/?hi=hey"),
            ("/canvas/view/?hi=hey#fragment", "/view/?hi=hey#fragment"),
            ("/canvas/view/?hi=hey&pow=1", "/view/?hi=hey&pow=1"),
            ("/canvas/view/?hi=hey&pow=1#fragment", "/view/?hi=hey&pow=1#fragment"),
            ("/canvas/view?hi=hey", "/view?hi=hey"),
            ("/canvas/view?hi=hey#fragment", "/view?hi=hey#fragment"),
            ("/canvas/view?hi=hey&pow=1", "/view?hi=hey&pow=1"),
            ("/canvas/view?hi=hey&pow=1#fragment", "/view?hi=hey&pow=1#fragment"),
            ("http://google.com", None),
            ("http://www.google.com", None),
            ("https://www.google.com", None),
            ("https://www.google.com/whateves", None),
            ("https://www.google.com/whateves/", None),
            ("https://google.com/whateves", None),
            ("https://google.com/whateves/", None),
            ("www.google.com", None),
            ("www.google.com/hey", None),
            ("google.com/yo", None),
            ("google.com/loud/noises/", None),
            ("/not_canvas/view", None),
            ("/not_canvas/view#fragment", None),
            ("/not_canvas/view/", None),
            ("/not_canvas/view/#fragment", None),
            ("/not_canvas/view/?hi=hey", None),
            ("/not_canvas/view/?hi=hey#fragment", None),
            ("/not_canvas/view/?hi=hey&pow=1", None),
            ("/not_canvas/view/?hi=hey&pow=1#fragment", None),
            ("/not_canvas/view?hi=hey", None),
            ("/not_canvas/view?hi=hey#fragment", None),
            ("/not_canvas/view?hi=hey&pow=1", None),
            ("/not_canvas/view?hi=hey&pow=1#fragment", None),
        ]

        middleware = FacebookRedirectMiddleware()
        for original_redirect,new_redirect in expected_results:
            mock_response = HttpResponseRedirect(original_redirect)
            new_response = middleware.process_response(None, mock_response)
            if new_redirect is None:
                self.assertEquals(original_redirect, new_response['Location'])
            else:
                new_redirect = settings.FACEBOOK_CANVAS_PAGE + new_redirect
                self.assertTrue("?" in new_response['Location'])
                query = urlparse.parse_qs(urlparse.urlparse(new_response['Location']).query)
                self.assertEquals(new_redirect, query[GET_REDIRECT_PARAM][0])

                # Now test the request handler
                mock_request = HttpRequest()
                mock_request.GET[GET_REDIRECT_PARAM] = query[GET_REDIRECT_PARAM][0]
                response = middleware.process_request(mock_request)
                self.assertIn('top.location.href="%s"' % query[GET_REDIRECT_PARAM][0], response.content)