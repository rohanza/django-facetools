from django.test.testcases import TestCase
from django.conf import settings
from facetools.models import TestUser
from facetools.common import _create_signed_request

# TODO: Add class that subclasses TransactionTestCase as well

class FacebookTestCase(TestCase):
    """
    TestCase which makes it possible to test views when the FacebookMiddleware
    and SyncFacebookUser middlewares are activated.  Must use the Client
    attached to this object (i.e. self.client).
    """
    facebook_test_user = None
    facebook_stop_sync_middleware = True

    def _pre_setup(self):
        super(FacebookTestCase, self)._pre_setup()

        # Don't change anything if a faebook user wasn't specified
        if self.facebook_test_user:
            facebook_user = TestUser.objects.get(name=self.facebook_test_user)
            self.client.cookies['signed_request'] = _create_signed_request(
                settings.FACEBOOK_APPLICATION_SECRET_KEY,
                facebook_user.facebook_id,
                oauth_token=facebook_user.access_token
            )
