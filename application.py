import os

from flask import Flask, session, render_template, redirect, request
from flask_session import Session

from session_layer import SessionLayer
from user_layer import UserLayer
from spotify_api import SpotifyLayer
from authentication_layer import AuthenticationLayer
from dataclass_templates import UserObject, SessionObject


app = Flask(__name__, template_folder='templates/')
app.secret_key = os.urandom(24)

app.config['SESSION_TYPE'] = 'redis'
Session(app)

app.secret_key = os.urandom(24)
app.config.from_object(__name__)

sess = SessionLayer()
spot = SpotifyLayer()
auth = AuthenticationLayer()
user = UserLayer(spotify_lay=spot, auth_layer=auth)


# TODO Check bool/string incompatibility throughout.
@app.route('/')
def show_main_page():
    session['session_current_route'] = "index"
    user.setSessionStateId()

    logged_in, user_id = user.idAndLoginDeclaration()

    # IP Check
    if sess.verifyCorrectSessionIP(return_on_ip_assignment=True):
        print("Detected: Request IP and Session IP Match (or new IP set)")
        pass
    else:
        return render_template('error.html', error="An Unexpected IP Mismatch Error Occurred")

    # If the user id is not empty or the user_id cookie is not empty.
    if user_id is not None:
        return redirect('/login')
    elif user_id is None:
        return redirect('/link')
    else:
        return render_template('error.html', error="An Unexpected Routing Error Occurred")


@app.route('/login', methods=["GET", "POST"])
def show_login_page():
    if request.method == "GET":
        session['session_current_route'] = "login"
        user.setSessionStateId()

        logged_in, user_id = user.idAndLoginDeclaration()

        # IP Check
        if sess.verifyCorrectSessionIP(return_on_ip_assignment=True):
            print("Detected: Request IP and Session IP Match (or new IP set)")
            pass
        else:
            return render_template('error.html', error="An Unexpected IP Mismatch Error Occurred")

        if logged_in is True and user_id is not None:
            print("Detected: Session Logged In and Session User Id is not None")
            return redirect('/app')
        else:
            return render_template('login.html')

    # TODO fix the post method and add some verification, parse email or username, etc.
    elif request.method == "POST":
        session['session_current_route'] = "login_post"
        username = request.form.get("username")
        plaintext_password = request.form.get('password')


        user_id = ""

        if True:  # If login is successful go to app
            session['logged_in'] = "True"
            session['username'] = user_id
            return redirect('/app')
        else:
            return render_template('login.html', error="Username or Password Incorrect")


@app.route('/link')
def show_link_page():
    session['session_current_route'] = "link"
    state_id = user.setSessionStateId(return_state=True)

    logged_in, user_id = user.idAndLoginDeclaration()

    if logged_in == True and user_id is not None:
        if user.checkIfUserExists(user_id, error_response=False) is False:
            session['session_logged_in'] = "False"
            session["session_user_id"] = None
            return render_template("error.html", error="User ID is not valid.")

        print("Link - Detected: Session Logged In and Session User ID exists")
        return redirect('/app')

    return render_template("spotify.html", link_url=spot.generateAuthorizeUrl(state_id=state_id))


@app.route('/callback', methods=["GET", "POST"])
def handle_callback():
    if request.method == "GET":
        session['session_current_route'] = "callback"

        if session.get('session_state_id', None) is None:
            print("Callback - Detected: Session State ID is None")
            return render_template('error.html', error="An Unexpected State Mismatch Error Occurred")

        user_auth_code = request.args.get('code')
        return user.handleFirstTimeAuthFlow(user_auth_code)

    elif request.method == "POST":
        session['session_current_route'] = "callback_post"
        hashed_password = auth.hashPassword(request.form.get('password'))
        logged_in, user_id = user.idAndLoginDeclaration()

        if user.checkIfUserExists(user_id) is False:
            print("Detected: User ID does not exist")
            return render_template('error.html', error="No User With user_id Found")

        status = user.updateUserData(user_id, {'user_password_hash': hashed_password})

        if status is not True:
            print("Detected: Password not updated")
            return render_template('error.html', error="Password Update Failed")

        return redirect('/app')


# TODO Fix the route and add verification + music store id + etc, look above
@app.route('/app')
def applet():
    session['session_current_route'] = "app"

    if session.get('session_logged_in', None) != "True":
        print("App - Detected: Session not Logged In")
        user_login_token = request.cookies.get('user_login_token')
        if user_login_token is None:
            print("App - Detected: No User Login Token")
            return redirect('/index')

    if user.checkIfUserExists(session.get('session_user_id', None), error_response=False) is False:
        print("App - Detected: Session User ID not valid")

        session['session_user_id'] = None
        session['session_logged_in'] = "False"

        return render_template('error.html', error="User ID not valid")

    # TODO Actually work on the ui of the app.....
    return render_template('home.html')


if __name__ == "__main__":
    app.run(host='10.0.1.36', port=25565)

