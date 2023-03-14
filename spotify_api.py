import time

import requests


# TODO Expand with more API endpoints for more data, update scopes as well.
class SpotifyLayer(object):
    def __init__(self):
        # noinspection SpellCheckingInspection
        self.client_id = 'N/A'
        self.client_secret = 'N/A'

        self.auth_endpoint = "https://accounts.spotify.com/authorize"
        self.token_endpoint = "https://accounts.spotify.com/api/token"

        self.scopes = "user-read-private%20user-read-email%20user-library-read%20playlist-read-private%20user-read" \
                      "-currently-playing%20user-read-playback-state "

        self.redirect_uri = 'http://10.0.1.36:25565/callback'

    def generateAuthorizeUrl(self, state_id=None, response_type="code"):
        if state_id is None:
            authorize_url = self.auth_endpoint + \
                            "?response_type=" + response_type + \
                            "&client_id=" + self.client_id + \
                            "&scope=" + self.scopes + \
                            "&redirect_uri=" + self.redirect_uri
        else:
            authorize_url = self.auth_endpoint + \
                            "?response_type=" + response_type + \
                            "&client_id=" + self.client_id + \
                            "&scope=" + self.scopes + \
                            "&redirect_uri=" + self.redirect_uri + \
                            "&state=" + state_id
        return authorize_url

    def requestAccessData(self, auth_code, return_expires_at=True, error_response=None):

        parameters = {"grant_type": "authorization_code",
                      "code": auth_code,
                      "redirect_uri": self.redirect_uri,
                      "client_id": self.client_id,
                      "client_secret": self.client_secret
                      }

        r = requests.post(self.token_endpoint, data=parameters)

        if r.status_code == 200 and r.reason == "OK":
            data = r.json()
            if return_expires_at:
                expires_in = int(data["expires_in"])
                expires_at = int(time.time()) + expires_in
                return data, expires_at
            else:
                return data
        else:
            if return_expires_at:
                return error_response, None
            return error_response

    def requestRefreshData(self, refresh_token, return_expires_at=True):
        parameters = {"grant_type": "refresh_token",
                      "refresh_token": refresh_token,
                      "client_id": self.client_id,
                      "client_secret": self.client_secret
                      }

        r = requests.post(self.token_endpoint, data=parameters)

        if r.status_code == 200 and r.reason == "OK":
            data = r.json()
            if return_expires_at:
                expires_in = int(data["expires_in"])
                expires_at = int(time.time()) + expires_in
                return data, expires_at
            else:
                return data
        else:
            if return_expires_at:
                return None, None
            return None

    @staticmethod
    def requestUserData(access_token):
        me_endpoint = "https://api.spotify.com/v1/me"
        auth_string = "Bearer " + access_token
        headers = {'Authorization': auth_string}

        r = requests.get(me_endpoint, headers=headers)

        return r.json()

    @staticmethod
    def requestCurrentlyPlaying(access_token):
        currently_playing_endpoint = 'https://api.spotify.com/v1/me/player'
        auth_string = "Bearer " + access_token
        headers = {'Authorization': auth_string}

        r = requests.get(currently_playing_endpoint, headers=headers)

        return r.json()
