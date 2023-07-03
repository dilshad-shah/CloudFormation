import logging
import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

log = logging.getLogger()
log.setLevel("INFO")

from utils.aws import get_ssm_param

slack_token = get_ssm_param(os.environ["SLACK_TKN"])
client = WebClient(token=slack_token)


def get_username(user_id):
    """returns username for slack user_id"""
    try:
        username = client.users_info(user=user_id)
        assert username["ok"]
        return username["user"]["name"]
    except:
        log.error("Couldn't find user details for %s" % user_id)
        return user_id


def get_userid_by_email(email):
    """returns user_id for a cvent email address"""
    try:
        user_id = client.users_lookupByEmail(email=email)
        assert user_id["ok"]
        return user_id["user"]["id"]
    except SlackApiError as error:
        log.error(error.response["error"])
        return None


def post_thread_message(channel, text, thread_ts):
    """posts a thread message"""

    try:
        comment_post = client.chat_postMessage(channel=channel, text=text, thread_ts=thread_ts)
        assert comment_post["ok"]
    except SlackApiError as error:
        log.error(error.response["error"])


def get_channel_name(channel):
    """returns the name of the public channel"""
    try:
        channel_name = client.conversations_info(channel=channel)
        assert channel_name["ok"]
        return channel_name["channel"]["name"]
    except SlackApiError as error:
        log.error(error.response["error"])
        return "Unknown Error"
