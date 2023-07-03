import json
import re

from utils.jira import create_jira_ticket
from utils.pagerduty import get_oncall, page_oncall
from utils.slack_calls import (
    get_channel_name,
    get_userid_by_email,
    get_username,
    post_thread_message,
)


def critical_request(event_text, channel, timestamp):
    """for 911 support"""
    summary = (re.search("\*Summary \*(.+?)\*Description of Issue", event_text).group(1)).strip()
    description = (re.search("\*Description of Issue \*(.+?)\*Slack 911 Channel", event_text).group(1)).strip()
    try:
        incident_channel = (re.search("\*Slack 911 Channel \* <#(.+?)>", event_text).group(1)).strip()
        incident_channel = get_channel_name(incident_channel)
        description += f"\nIncident Channel - {incident_channel}"
    except AttributeError:
        pass

    primary, secondary = get_oncall()
    user_id = (re.search("submission from <@(.*?)> \*Summary", event_text).group(1)).strip()
    requester = get_username(user_id)
    ticket_payload = (
        '{"fields": {"project":{"id": "20505"}, "issuetype": {"id": "29"},"summary": "%s", "customfield_27801": {"id": "38605"}, "customfield_27500": {"id": "39307"}, "customfield_27501": {"id": "39312"}, "customfield_27502": {"id": "39313"}, "priority": {"id": "10100"}, "description": "%s", "assignee":{"name":"%s"}, "customfield_28400":{"name":"%s"}}}'
        % (summary, description, primary, requester)
    )

    ticket_payload = json.dumps(json.loads(ticket_payload, strict=False))
    primary = get_userid_by_email(email=f"{primary}@cvent.com")
    secondary = get_userid_by_email(email=f"{secondary}@cvent.com")
    ticket = create_jira_ticket(ticket_payload, channel, timestamp, user_id)

    comment = f"> <@{user_id}>, <@{primary}> will get in touch with you regarding this request. cc: <@{secondary}>"
    if ticket is not None:
        comment = f"> <@{user_id}>, <@{primary}> will get in touch with you regarding this request : <https://jira.cvent.com/browse/{ticket}|{ticket}>."
        comment += f" cc: <@{secondary}> ."

    comment += "\n*Discussions on this thread will automatically get added to the ticket.*"
    post_thread_message(channel=channel, text=comment, thread_ts=timestamp)

    page_oncall(ticket)
