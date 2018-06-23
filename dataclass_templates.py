from dataclasses import dataclass, field


@dataclass
class UserObject:
    """Object describing all user level data available in the database."""
    user_id: str or None = None  # The User's ID As Well As The DynamoDB Database Key
    user_music_key_id: str or None = None  # The User's Music Key ID
    user_created: int or None = None  # The Epoch Time That The User Was Created
    user_session_ids: list = field(default_factory=list)  # The Current Sessions Associated With The User
    user_known_ips: list = field(default_factory=list)  # The Known IP's The User Has Logged In From

    user_access_token: str or None = None  # The Access Token For Accessing The Spotify API
    user_access_token_expires: int or None = None  # The Epoch Time That The Access Token Expires
    user_refresh_token: str or None = None  # The User's Refresh Token For Requesting A New Spotify Access Token

    user_spotify_associated: bool = False  # If Spotify Has Been Successfully Linked
    user_spotify_id: str or None = None  # The User's Spotify User ID
    user_email: str or None = None  # The User's Spotify Email Address
    user_first_name: str or None = None  # The User's First Name

    user_password_hash: str or None = None  # The User's Hashed And Salted Password


@dataclass
class SessionObject:
    """Object describing all the session level data available in the other session object."""
    session_id: str or None = None  # Id of the session

    session_current_route: str or None = None
    session_ip: str or None = None  # Ip of Session (unreliable)

    session_logged_in: bool or None = False
    session_user_id: str or None = None
    session_state_id: str or None = None

    session_expiration_epoch: int or None = None  # Epoch time of expire: maybe????/
