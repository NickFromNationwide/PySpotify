import string
import os, os.path
import secrets
import base64
import random
import time
import pickle
from typing import Type, List, Optional, Any

import requests
from requests.auth import HTTPBasicAuth

import bcrypt
from getpass import getpass
from requests import Request, Session
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session
import crayons


class UserSystem(object):

    def __init__(self):
        self.path = os.getcwd()

    def appendUser(self, user_object: User, update_time_created=True):
        user_id = generateUserId()

        if not self.checkUserExists(user_id):
            new_user_object = user_object

            if update_time_created:
                new_user_object.user_created = getCurrentTime()

            self.user_store[user_id] = new_user_object

            print("User Appended:", user_id)
            return user_id

        else:
            print("User ID Exists:", user_id)
            print("Trying Again...")
            self.appendUser(user_object, update_time_created)

    def checkUserExists(self, user_id):
        if user_id in self.user_store:
            print("User Exists:", user_id)
            return True
        else:
            print("User Not Found:", user_id)
            return False

    def deleteUser(self, user_id):
        """

        :rtype: bool
        """
        if self.checkUserExists(user_id):
            try:
                del self.session_store[user_id]
                print("User Deleted:", user_id)
                return True
            except:  # TODO Fix
                return False

        else:
            return None

    def getUserData(self, user_id):
        if self.checkUserExists():
            user_data: User = self.user_store[user_id]
            print("User Retrieved:", user_id)
            return user_data
        else:
            return False

    def updateUserData(self, user_id, new_user_data: User):
        if self.checkUserExists():
            self.user_store[user_id]: User = new_user_data
            print("User Updated:", user_id)
            return True
        else:
            return False

    def checkUserLoginToken(self, user_id, user_token, delete_token_on_match=False):
        if self.checkUserExists(user_id):
            user_object = self.getUserData(user_id)
            for saved_token in user_object.user_login_tokens:
                if saved_token == user_token:
                    print("User Token Matched:", user_token)
                    if delete_token_on_match:
                        print("Deleting User Token:", saved_token)
                        new_token_list = [x for x in user_object.user_login_tokens if x != saved_token]
                        user_object.user_login_tokens = new_token_list
                        self.updateUserData(user_id, user_object)
                    return True
            print("No User Token Matched:", user_token)
            return False

        else:
            return False

    def generateUserLoginToken(self, user_id, add_token_to_user=True):
        if self.checkUserExists(user_id):
            user_data_object = self.getUserData(user_id)
            token = generateLoginToken()
            user_data_object.user_login_tokens.append(token)
            if add_token_to_user is False:
                return token
            elif add_token_to_user:
                self.updateUserData(user_id, user_data_object)
                print("User Token Added:", token)
                return token

        else:
            return False

    def verifyUserLoginIp(self, user_id, check_ip, add_user_ip=False):
        if self.checkUserExists(user_id):
            user_data: User = self.getUserData(user_id)
            for saved_ip in user_data.user_known_ips:
                if check_ip == saved_ip:
                    print("User IP Matched:", saved_ip)
                    return True

            print("No User IP Matched:", check_ip)
            if add_user_ip:
                user_data.user_known_ips.append(check_ip)
                self.updateUserData(user_id, user_data)
                print("User IP Appended:", check_ip)
            else:
                return False

        else:
            return False

    def matchUserEmail(self, user_email):
        for user_id in self.user_store:
            saved_email = self.user_store[user_id]
            if saved_email == user_email:
                print("User Email Matched:", saved_email)
                return user_id
        return False

    def verifyPasswordLoginAttempt(self, user_email, password_attempt, user_id=None):
        if user_id is not None:
            if self.checkUserExists(user_id):
                return self.verifyUserPassword(user_id, password_attempt)
            else:
                return False

        elif user_id is None:
            flow_match = self.matchUserEmail(user_email)
            if flow_match is not False:
                return self.verifyUserPassword(flow_match, password_attempt)
            else:
                return False
        else:
            return False
