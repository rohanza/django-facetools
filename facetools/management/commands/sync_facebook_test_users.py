from optparse import make_option
import json

from django.core.management.base import AppCommand, BaseCommand
from django.conf import settings
import requests

from facetools.test.common import _create_test_user, _friend_test_users, _create_test_user_on_facebook
from facetools.models import TestUser

class Command(AppCommand):
    help = 'Creates the facebook test users defined in each app in the project.'

    def handle_app(self, app, **options):
        app_name = '.'.join(app.__name__.split('.')[0:-1])

        test_users = _get_facetools_test_users(app_name)
        existing_facebook_test_users = _get_existing_facebook_test_users()
        existing_facetool_test_users = [u.name for u in TestUser.objects.all()]
        existing_test_users = set(existing_facebook_test_users.keys() + existing_facetool_test_users)

        # Create any test users on facebook their corresponding User models in facetools
        # that don't exist on facebook yet.
        for test_user in test_users:
            # Add user to facebook and local database
            if test_user['name'] not in existing_test_users:
                _create_test_user(
                    app_installed = test_user.get('installed', True),
                    name          = test_user['name'],
                    permissions   = test_user.get('permissions'),
                )

            # Add test user to facebook and sync with existing test user in the local database
            elif test_user['name'] not in existing_facebook_test_users:
                facebook_response_data = _create_test_user_on_facebook(
                    app_installed = test_user.get('installed', True),
                    name          = test_user['name'],
                    permissions   = test_user.get('permissions')
                )
                facetools_user = TestUser.objects.get(name=test_user['name'])
                facetools_user.facebook_id = facebook_response_data['id']
                facetools_user.access_token = facebook_response_data.get('access_token', "")
                facetools_user.save()

            # Add test user to the local database using the test user's data on facebook
            elif test_user['name'] not in existing_facetool_test_users:
                facebook_data = existing_facebook_test_users[test_user['name']]
                TestUser.objects.create(
                    name         = test_user['name'],
                    facebook_id  = facebook_data['id'],
                    access_token = facebook_data['access_token']
                )

        # Get a list of each friendship between test users, no duplicates
        friendships = [list(r) for r in _get_test_user_relationships(test_users)]
        for friendship in friendships:
            friendship = list(friendship)
            _friend_test_users(friendship[0], friendship[1])

def _get_facetools_test_users(app_name, test_user_module_name='facebook_test_users'):
    """Get the dictionary of facebook test users for the app, throwing an error if the app
    doesn't have any defined."""

    try:
        _temp = __import__(app_name, globals(), locals(), [test_user_module_name])
        facetools_test_users = _temp.facebook_test_users.facebook_test_users
        if callable(facetools_test_users):
            facetools_test_users = facetools_test_users()
    except ImportError:
        raise Exception("Error: %s doesn't have a module called %s" % (app_name, test_user_module_name))

    # Ensure no test users share the same name
    facetools_test_names = set([u['name'] for u in facetools_test_users])
    if len(facetools_test_names) != len(facetools_test_users):
        raise Exception("Error: Duplicate names found in %s for %s" % (test_user_module_name, app_name))

    return facetools_test_users

def _get_existing_facebook_test_users(app_id=settings.FACEBOOK_APPLICATION_ID, app_secret=settings.FACEBOOK_APPLICATION_SECRET_KEY):
    """
    Get the facebook data for each test user defined for the app.
    """
    existing_facebook_test_users = {}
    app_access_token = '%s|%s' % (app_id, app_secret)
    test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (app_id, app_access_token)
    users_response_data = json.loads(requests.get(test_users_url).content)
    if 'error' in users_response_data:
        raise Exception("Error retrieving facebook app's test users: %s" % users_response_data['error']['message'])
    else:
        test_user_url = "https://graph.facebook.com/%s?access_token=%s"
        for test_user in users_response_data['data']:
            user_response_data = json.loads(requests.get(test_user_url % (test_user['id'], app_access_token)).content)
            if user_response_data == False:
                # skip invalid users defined on facebook
                continue
            if 'error' in user_response_data:
                raise Exception("Error retrieving data for %s: %s" % (test_user['id'], user_response_data['error']['message']))
            elif 'name' in user_response_data:
                user_response_data['access_token'] = test_user['access_token']
                existing_facebook_test_users[user_response_data['name']] = user_response_data

    return existing_facebook_test_users

def _get_test_user_relationships(test_users):
    """
    Takes a facebook_test_users dict and returns a list of relationships, with
    each item being a set of 2 names that should be friends.
    """
    relationships = []
    for test_user in test_users:
        if 'friends' in test_user:
            for friend in test_user['friends']:
                relationships.append(set([test_user['name'], friend]))
    no_dupes = []
    for relationship in relationships:
        if relationship not in no_dupes:
            no_dupes.append(relationship)
    return no_dupes
