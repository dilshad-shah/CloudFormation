import json
import logging
import os
import re

import requests

log = logging.getLogger()
log.setLevel("INFO")

from utils.aws import get_dynamodb_item, get_ssm_param, put_dynamodb_item
from utils.slack_calls import get_username

jira_headers = {
    "Content-Type": "application/json",
    "Authorization": f'Basic {get_ssm_param(ssm_param_path=os.environ["JIRA_TKN"])}',
}


def upload_comment(user_id, timestamp, slack_event="", channel=""):
    """uploads comments from threads to corresponding jira tickets"""
    # get ticket for timestamp from dynamodb
    try:
        db_get_ticket_number = {"threadId": {"S": timestamp}}
        ticket = get_dynamodb_item(db_get_ticket_number)
        ticket = ticket["Item"]["ticketNumber"]["S"]
    except KeyError as error:
        log.error("No ticket found for this threadId : %s ; Message : %s" % (timestamp, error))

    url = f"https://jira.cvent.com/rest/api/2/issue/{ticket}/comment"
    if slack_event != "":
        user = get_username(user_id)
        # parse comment for attachments, formatting etc
        # temp. simple text comment.
        comment = slack_event["text"]
        user_tags = re.findall("<@(.*?)>", comment)
        if len(user_tags) != 0:
            for user_tag in user_tags:
                comment = comment.replace(f"<@{user_tag}>", f"[~{get_username(user_tag)}]")

        file = []
        if "files" in slack_event.keys():
            for files in slack_event["files"]:
                file.append(files["url_private"])

        if len(file) != 0:
            file_list = "\n".join(file)
            payload = json.dumps({"body": f"[~{user}] posted : {comment} \n\n Attachment(s): \n{file_list}"})
        else:
            payload = json.dumps({"body": f"[~{user}] posted : {comment}"})

    if channel != "":
        comment = f"[link to slack request|https://cvent.slack.com/archives/{channel}/p{timestamp.replace('.','')}]"
        payload = json.dumps({"body": comment})

    post_comment = requests.post(url=url, headers=jira_headers, data=payload)


def create_jira_ticket(ticket_payload, channel, timestamp, user_id):
    """creates jira tinf request and returns the ticket number"""
    url = "https://jira.cvent.com/rest/api/2/issue"
    log.info("CREATE_JIRA_TICKET! PAYLOAD: %s" % (ticket_payload))
    try:
        create_ticket = requests.post(url=url, headers=jira_headers, data=ticket_payload)
        ticket = json.loads(create_ticket.text)
        ticket = ticket["key"]

        db_push_values = {
            "threadId": {"S": timestamp},
            "ticketNumber": {"S": ticket},
        }
        put_dynamodb_item(db_push_values)
        upload_comment(user_id=user_id, timestamp=timestamp, channel=channel)
        return ticket
    except KeyError as error:
        log.error("Trouble creating Jira ticket : %s" % error)
        comment = f"> <@{user_id}>, I had trouble creating a ticket."
        return None
