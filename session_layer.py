from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session

from dataclass_templates import SessionObject
from authentication_layer import str_to_bool


class SessionLayer(object):

    @staticmethod
    def verifyCorrectSessionIP(compare_ip=None, return_on_ip_assignment=None):
        if compare_ip is None:
            compare_ip = request.remote_addr

        server_state = session.get('session_ip', None)
        if server_state is None:  # If no ip var assigned.
            session['session_ip'] = compare_ip
            return return_on_ip_assignment  # Signifies a new ip was just assigned.
        elif server_state is not None:  # If ip var assigned.
            if server_state != compare_ip:  # If server ip does not match compare ip.
                return False  # Signifies the server ip and client ip do not match.
            else:  # If server up matches compare ip.
                return True  # Signifies ip verification passed.

    @staticmethod
    def checkIfSessionIsLoggedIn(if_none_set_state_to: bool or None = None, return_client_state=False):
        server_state = session.get('session_logged_in', None)
        client_state = request.cookies.get("session_logged_in")
        if client_state is not None:
            client_state = str_to_bool(client_state)
        if server_state is not None:
            server_state = str_to_bool(server_state)

        if server_state is None:
            if if_none_set_state_to is not None:
                session['session_logged_in'] = str(if_none_set_state_to)
                print("Make sure to set the client cookie state as well!")
            if return_client_state:
                return if_none_set_state_to, client_state
            return if_none_set_state_to
        elif server_state is not None:
            if server_state:
                if return_client_state:
                    return True, client_state
                return True
            else:
                if return_client_state:
                    return False, client_state
                return False

    # TODO check bool/str incompatibility here.
    @staticmethod
    def getSessionData(return_type: object or dict = dict):

        if return_type is object:
            sess = SessionObject()
            sess.session_id = SessionLayer.getSessionID()
            sess.session_current_route = session.get("session_current_route", None)
            sess.session_ip = session.get("session_ip", None)
            sess.session_logged_in = SessionLayer.checkIfSessionIsLoggedIn()  # TODO Check if works 1
            sess.session_user_id = session.get("session_user_id", None)
            sess.session_state_id = session.get("session_state_id", None)
            sess.session_expiration_epoch = session.get("session_expiration_epoch", None)

            return sess
        elif return_type is dict:
            sess = {'session_id': request.cookies.get("session"),
                    'session_current_route': session.get("session_current_route", None),
                    'session_ip': session.get("session_ip", None),
                    'session_logged_in': SessionLayer.checkIfSessionIsLoggedIn(None),  # TODO Check if works 2
                    'session_user_id': session.get("session_user_id", None),
                    'session_state_id': session.get("session_state_id", None),
                    'session_expiration_epoch': session.get("session_expiration_epoch", None)}

            return sess

    @staticmethod
    def getSessionID(if_none_return=None):
        sess_id = request.cookies.get("session")
        if sess_id is None:
            return if_none_return
        else:
            return sess_id
