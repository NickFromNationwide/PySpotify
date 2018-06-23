import time

from flask import request, render_template, redirect, session

import database_layer
import authentication_layer
import spotify_api
import session_layer


# TODO Add more Auth flows and add more specialized methods.
class UserLayer(object):
    def __init__(self, auth_layer=authentication_layer.AuthenticationLayer(), spotify_lay=spotify_api.SpotifyLayer()):
        self.auth_layer = auth_layer
        self.spotify_layer = spotify_lay
        self.session_layer = session_layer.SessionLayer()
        self.table_name = 'user_store'
        self.key_name = "user_id"
        self.user_database = database_layer.GenericDatabaseLayer(table_name=self.table_name, key_name=self.key_name)

    def getUserData(self, user_id, no_user_response=None, error_response=None):
        response, data = self.checkIfUserExists(user_id, return_user_data=True)

        if response is True:
            return data
        if response is False:
            return no_user_response
        elif response is None:
            return error_response

    def checkIfUserExists(self, user_creds=None, check_method='user_id', return_user_data=False,
                          error_response=None):
        if check_method is 'user_id':
            exists = self.user_database.readFromDatabase(user_creds, except_return=False, no_key_return=None)
            if exists is None:
                if return_user_data:
                    return False, None
                return False
            elif exists:
                if return_user_data:
                    return True, exists
                return True
            elif not exists:
                if return_user_data:
                    return error_response, None
                return error_response
        elif check_method is 'user_email' or 'user_spotify_id':
            data_object = self.user_database.scanFromDatabase(scan_attr=check_method, attr_value=user_creds,
                                                              except_return=error_response, no_key_return=False)

            if data_object is False or data_object is error_response:
                if return_user_data:
                    return data_object, None
                return data_object

            if return_user_data:
                return True, data_object
            return True

    def createNewUser(self, user_known_ip=None, user_session_id=None, user_spotify_associated=False, hashed_pass=None,
                      return_user_object=False):
        user_id = self.auth_layer.generateUserId()
        user_dict = {'user_music_id': self.auth_layer.generateUserMusicKeyId(),
                     'user_created': str(int(time.time())),
                     'user_spotify_associated': str(user_spotify_associated)}

        if user_known_ip is not None:
            user_dict['user_known_ips'] = str([user_known_ip])

        if user_session_id is not None:
            user_dict['user_session_ids'] = str([user_session_id])

        if hashed_pass is not None:
            user_dict['user_password_hash'] = hashed_pass

        success = self.user_database.appendToDatabase(user_id, parameter_dict=user_dict, except_return=False)
        if success:
            pass
        else:
            return False

        if return_user_object:
            return user_id, user_dict
        return user_id

    def updateSecondPartNewUserData(self, user_id, user_access_token=None, user_access_token_expires=None,
                                    user_refresh_token=None, user_spotify_associated=None, user_spotify_id=None,
                                    user_email=None, user_first_name=None, hashed_pass=None, return_user_object=False):

        user_dict = {'user_access_token': str(user_access_token),
                     'user_access_token_expires': str(user_access_token_expires),
                     'user_refresh_token': str(user_refresh_token),
                     'user_spotify_id': str(user_spotify_id)}

        if user_spotify_associated is not None:
            user_dict['user_spotify_associated'] = str(user_spotify_associated)

        if user_spotify_id is not None:
            user_dict['user_spotify_id'] = user_spotify_id

        if user_email is not None:
            user_dict['user_email'] = user_email

        if user_first_name is not None:
            user_dict['user_first_name'] = user_first_name

        if hashed_pass is not None:
            user_dict['user_password_hash'] = hashed_pass

        success = self.user_database.updateToDatabase(user_id, user_dict, except_return=False)
        if success:
            pass
        else:
            if return_user_object:
                return False, None
            return False
        if return_user_object:
            return True, user_dict
        return True

    def updateUserData(self, user_id, new_data_dict):
        exists = self.checkIfUserExists(user_id, )  # TODO See wtf this is about lol
        if exists:
            success = self.user_database.updateToDatabase(user_id, new_data_dict, except_return=False)
            if success:
                return True
            else:
                return False
        else:
            return False

    def setSessionStateId(self, return_state=False):
        if session.get('session_state_id', None) is None:

            # TODO Check if state id is a valid state_id
            print("Setting: Session State ID")

            state = self.auth_layer.generateSessionStateId()
            session['session_state_id'] = str(state)

            if return_state:
                return state

        return session.get('session_state_id', None)

    @staticmethod
    def idAndLoginDeclaration(logged_in=None, user_id=None):
        if logged_in is None:
            logged_in = session.get('session_logged_in', None)
        if user_id is None:
            user_id = session.get('session_user_id', None)

        if logged_in == "True":
            logged_in = True
        elif logged_in == "False":
            logged_in = False

        if user_id == "True":
            user_id = True
        elif user_id == "False":
            user_id = False

        return logged_in, user_id

    def handleFirstTimeAuthFlow(self, spotify_auth_code, except_return=False):
        session_data = self.session_layer.getSessionData()

        # If the session data says the user is logged in.
        if authentication_layer.str_to_bool(session_data['session_logged_in']):
            print("User Logged In")
            # If the user_id is not empty.
            if session_data['session_user_id'] is not None:
                exists = self.checkIfUserExists(user_creds=session_data['session_user_id'], error_response=False)

                # If the user exists in the db.
                if exists:
                    return redirect('/app')
                else:
                    return render_template("error.html", error="No User Matching User ID Found")
            else:
                session['session_logged_in'] = 'False'

        access_data, access_data_expiration_time = self.spotify_layer.requestAccessData(spotify_auth_code)

        try:
            access_token = access_data['access_token']
            refresh_token = access_data['refresh_token']
        except TypeError as t:
            print(t)
            return except_return

        try:
            spotify_user_data = self.spotify_layer.requestUserData(access_token)
            display_name = spotify_user_data['display_name']
            spotify_email = spotify_user_data['email']
            spotify_id = spotify_user_data['id']
        except Exception as e:
            print(e)
            return except_return

        email_exists, existing_user_data = self.checkIfUserExists(user_creds=spotify_email, check_method='user_email',
                                                                  return_user_data=True)

        # If the email exists in the db.
        if email_exists:
            # If the user data is a list.
            if type(existing_user_data) is list:
                existing_user_data = existing_user_data[0]

            try:
                hash_pass = existing_user_data['user_password_hash']
            except KeyError:
                hash_pass = None
            except TypeError:
                hash_pass = None

            session['session_logged_in'] = 'True'
            session['session_user_id'] = existing_user_data['user_id']

            result = self.updateUserData(user_id=existing_user_data['user_id'],
                                         new_data_dict={"user_access_token": access_token,
                                                        "user_access_token_expires": access_data_expiration_time,
                                                        "user_refresh_token": refresh_token})
            # TODO Handle session and IP DB additions/checks.

            if hash_pass is None:
                return render_template('set_password.html')

            # If the user data update was successful.
            if result:
                return redirect('/app')
            else:
                return except_return
        elif email_exists is False:
            pass
        else:
            return except_return

        user_id = self.createNewUser(user_known_ip=request.remote_addr, user_session_id=session_data['session_id'],
                                     user_spotify_associated=True)

        updated, user_object = self.updateSecondPartNewUserData(user_id, user_access_token=access_token,
                                                                user_access_token_expires=access_data_expiration_time,
                                                                user_refresh_token=refresh_token,
                                                                user_spotify_associated=True,
                                                                user_spotify_id=spotify_id,
                                                                user_email=spotify_email,
                                                                user_first_name=display_name,
                                                                return_user_object=True)

        if not updated:
            return except_return

        if user_object['user_spotify_associated'] != "True":
            print("Detected: User ID does not have Spotify Associated")
            return render_template('error.html', error="An Unexpected State Mismatch Error Occurred")

        session['session_logged_in'] = "True"
        session['session_user_id'] = user_id

        return render_template('set_password.html', user_id=user_id)

    # TODO fix the method
    @staticmethod
    def handleLogin():
        print("login Handle")
