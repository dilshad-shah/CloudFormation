import json
import logging
import re

log = logging.getLogger()
log.setLevel("INFO")

from data.jira_codes import priority_map
from utils.jira import create_jira_ticket
from utils.pagerduty import get_oncall, page_oncall, paging_hours
from utils.slack_calls import get_userid_by_email, get_username, post_thread_message


def iam_request(event_text, channel, timestamp):
    """parses AD workflow payload, creates Jira Ticket and posts ticket back to thread"""
    requester_id = (re.search("submission from <@(.*?)> \*Summary", event_text).group(1)).strip()
    requester = get_username(requester_id)
    summary = (re.search("\*Summary \*(.+?)\*Domain", event_text).group(1)).strip()
    domain = (re.search("\*Domain \*(.+?)\*Request Type", event_text).group(1)).strip()
    request_type = (re.search("\*Request Type \*(.+?)\*Request for", event_text).group(1)).strip()
    try:
        request_for_id = (re.search("\*Request for \* <@(.*?)>   \*Map permission to", event_text).group(1)).strip()
        request_for = get_username(request_for_id)
    except AttributeError:
        request_for = "not specified"

    try:
        map_permission_user_id = (
            re.search("Map permission to \* <@(.*?)>   \*Expected Response Time", event_text).group(1)
        ).strip()
        map_permission_user = get_username(map_permission_user_id)
    except AttributeError:
        map_permission_user = "not specified"

    priority = (re.search("\*Expected Response Time \* (.+?)   \*Description", event_text).group(1)).strip()
    description = (re.search("\*Description \*(.+) ", event_text).group(1)).strip()

    log.error("IAM REQUEST TRIGGERED! summary: %s ; domain : %s" % (summary, domain))
    log.info(requester_id)
    log.info(requester)
    log.info(summary)
    log.info(domain)
    log.info(request_type)
    # log.info(request_for_id)
    log.info(request_for)
    # log.info(map_permission_user_id)
    log.info(map_permission_user)
    log.info(priority)
    log.info(description)

    if request_type in ["Account Disabled", "Account Locked Out"]:
        comment = f"> <@{requester_id}> Please reach out to <#CCNCHDQ68> regarding this request."
        post_thread_message(channel=channel, text=comment, thread_ts=timestamp)
        return

    service = 38342
    pillar = 38356
    if "core.cvent.org" in domain:
        component = 38316
    else:
        component = 38317

    primary, secondary = get_oncall()
    ticket_payload = (
        '{"fields": {"project":{"id": "20505"}, "issuetype": {"id": "29"},"summary": "%s", "customfield_27801": {"id": "38605"}, "customfield_27500": {"id": "%s"}, "customfield_27501": {"id": "%s"}, "customfield_27502": {"id": "%s"}, "priority": {"id": "%s"}, "description": "%s\n\nDomain: %s\nRequest Type: %s\nRequested For: %s\nMap Access From: %s\n", "assignee":{"name":"%s"}, "customfield_28400":{"name":"%s"}}}'
        % (
            summary,
            component,
            service,
            pillar,
            priority_map[priority],
            description,
            domain,
            request_type,
            request_for,
            map_permission_user,
            primary,
            requester,
        )
    )
    ticket_payload = json.dumps(json.loads(ticket_payload, strict=False))
    tag_user = get_userid_by_email(email=f"{primary}@cvent.com")
    ticket = create_jira_ticket(ticket_payload, channel, timestamp, requester_id)

    comment = f"> <@{requester_id}>, <@{tag_user}> will get in touch with you shortly regarding this request."
    if ticket is not None:
        comment = f"> <@{requester_id}>, please have your manager approve this IAM Request - <https://jira.cvent.com/browse/{ticket}|{ticket}>."
        comment += f" <@{tag_user}> will get in touch with you shortly regarding this request."

    if paging_hours():
        if priority_map[priority] == 1:
            page_oncall(ticket)
        else:
            try:
                assert ticket is not None
                comment = f"> <@{requester_id}>, please have your manager approve this IAM Request <https://jira.cvent.com/browse/{ticket}|{ticket}>."
                comment += " Due to this being an off-hours request, a cloud-infra engineer will reach out within 24hrs regarding this request."
            except:
                comment = f"> <@{requester_id}>, due to this being an off-hours request, a cloud-infra engineer will reach out within 24hrs regarding this request."
    else:
        pass
    comment += "\n*Discussions on this thread will automatically get added to the ticket.*"
    post_thread_message(channel=channel, text=comment, thread_ts=timestamp)
