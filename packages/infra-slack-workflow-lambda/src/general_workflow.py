# import datetime
import ipaddress
import json
import logging
import re

# import requests

log = logging.getLogger()
log.setLevel("INFO")

from data.jira_codes import priority_map, region_map, service_map
from utils.jira import create_jira_ticket
from utils.pagerduty import get_oncall, page_oncall, paging_hours
from utils.slack_calls import get_userid_by_email, get_username, post_thread_message


def _host_lookup(host):
    # function will check if value of host is a Validating IP address
    # if host is not IP address, function will check if the input value
    # is a hyperlink  in the form : <https://www.cvent.com|cvent.com> and
    # extract just then name i.e. cvent.com from the value.

    try:
        # validating IP address
        destination = ipaddress.ip_address(host)
    except ValueError:
        try:
            # checking for hyperlink
            destination = re.search("\|(.*)>", host).group(1)
        except AttributeError:
            destination = host
        except TypeError:
            destination = ""
    return str(destination)


def general_request(event_text, channel, timestamp):
    """parses General Walkup Request workflow payload , creates jira ticket and posts ticket back to user"""

    # parse info from the payload
    requester_id = (re.search("submission from <@(.*?)> \*Summary", event_text).group(1)).strip()
    requester = get_username(requester_id)
    summary = (re.search("\*Summary \*(.+?)\*Impacted Service Component", event_text).group(1)).strip()
    impacted_service = (
        re.search("\*Impacted Service Component \*(.+?)\*Expected Response Time \*", event_text).group(1)
    ).strip()
    priority = (re.search("\*Expected Response Time \*(.+?)\*Description of Issue \*", event_text).group(1)).strip()
    description = (re.search("\*Description of Issue \*(.+?)\*Impacted Host / Device", event_text).group(1)).strip()
    host = (re.search("\*Impacted Host / Device \*(.+?)\*AWS Account \*", event_text).group(1)).strip()
    account = (re.search("\*AWS Account \*(.+?)\*AWS Region \*", event_text).group(1)).strip()
    region = (re.search("\*AWS Region \*(.+?) ", event_text).group(1)).strip()

    # coverting to jira values
    try:
        if service_map[impacted_service]:
            component, service, pillar = service_map[impacted_service]
    except KeyError:
        comment = "Impacted service component not found in service_map"
        log.error(comment)
        post_thread_message(channel=channel, text=comment, thread_ts=timestamp)
        return

    if host == "_left blank_":
        host = " "
    host = _host_lookup(host)

    if account == "_left blank_":
        account = " "

    primary, secondary = get_oncall()

    if region == "_left":
        # jira call without region field
        ticket_payload = (
            '{"fields": {"project":{"id": "20505"}, "issuetype": {"id": "29"},"summary": "%s", "customfield_27801": {"id": "38605"}, "customfield_27500": {"id": "%s"}, "customfield_27501": {"id": "%s"}, "customfield_27502": {"id": "%s"}, "priority": {"id": "%s"}, "description": "%s", "customfield_27503": "%s", "customfield_27504": "%s", "assignee":{"name":"%s"}, "customfield_28400":{"name":"%s"}}}'
            % (
                summary,
                component,
                service,
                pillar,
                priority_map[priority],
                description,
                host,
                account,
                primary,
                requester,
            )
        )
    else:
        # jira call with all fields
        ticket_payload = (
            '{"fields": {"project":{"id": "20505"}, "issuetype": {"id": "29"},"summary": "%s", "customfield_27801": {"id": "38605"}, "customfield_27500": {"id": "%s"}, "customfield_27501": {"id": "%s"}, "customfield_27502": {"id": "%s"}, "priority": {"id": "%s"}, "description": "%s", "customfield_27503": "%s", "customfield_27504": "%s", "customfield_27505": {"id": "%s"}, "assignee":{"name":"%s"}, "customfield_28400":{"name":"%s"}}}'
            % (
                summary,
                component,
                service,
                pillar,
                priority_map[priority],
                description,
                host,
                account,
                region_map[region],
                primary,
                requester,
            )
        )

    ticket_payload = json.dumps(json.loads(ticket_payload))
    tag_user = get_userid_by_email(email=f"{primary}@cvent.com")
    ticket = create_jira_ticket(ticket_payload, channel, timestamp, requester_id)

    comment = f"> <@{requester_id}>, <@{tag_user}> will get in touch with you shortly regarding this request."
    if ticket is not None:
        comment = f"> <@{requester_id}>, <@{tag_user}> will get in touch with you shortly regarding this request. <https://jira.cvent.com/browse/{ticket}|{ticket}>"

    if paging_hours():
        if priority_map[priority] == 1:
            page_oncall(ticket)
        else:
            try:
                assert ticket is not None
                comment = f"> <@{requester_id}>, due to this being an off-hours request, a cloud-infra engineer will reach out within 24hrs regarding this request. <https://jira.cvent.com/browse/{ticket}|{ticket}>"
            except:
                comment = f"> <@{requester_id}>, due to this being an off-hours request, a cloud-infra engineer will reach out within 24hrs regarding this request."
    comment += "\n*Discussions on this thread will automatically get added to the ticket.*"
    post_thread_message(channel=channel, text=comment, thread_ts=timestamp)
