import datetime
import json
import logging
import os

import requests
from pytz import timezone

from utils.aws import get_ssm_param

log = logging.getLogger()
# FORMAT = "[%(filename)s:%(lineno)s - %(funcName)5s() ] %(message)s"
# logging.basicConfig(format=FORMAT , level=logging.INFO)
log.setLevel("INFO")

# For internal testing
# os.environ["PD_TKN"] = "/infra-slack-workflow-testing/pd-token"
# os.environ["PD_SRV_ID"] = "/infra-slack-workflow-testing/pd-srv-id"


def get_oncall():
    """pagerduty call for oncall escalation schedule \n
    returns user_name:list of primary and secondary oncall engineer"""
    policy_code = ["PD70OIX", "PV9J4RF"]
    pagerduty_header = {
        "Accept": "application/vnd.pagerduty+json;version=2",
        "Authorization": f'Token token={get_ssm_param(os.environ["PD_TKN"])}',
    }

    oncall_users = []
    for code in policy_code:
        params = (
            ("time_zone", "UTC"),
            ("include[]", "schedules"),
            ("schedule_ids[]", code),
        )

        # getting oncall schedule
        url = "https://api.pagerduty.com/oncalls"
        out_data = requests.get(url, headers=pagerduty_header, params=params, verify=False)
        json_obj = json.loads(out_data.content)
        oncall_user_id = json_obj["oncalls"][0]["user"]["id"]

        # get email id for primary oncall
        url2 = f"https://api.pagerduty.com/users/{oncall_user_id}"
        user_email = requests.get(url2, headers=pagerduty_header, verify=False)
        user_email = json.loads(user_email.content)
        user_name = (user_email["user"]["email"]).replace("@cvent.com", "")
        oncall_users.append(user_name)
    return oncall_users


def page_oncall(ticket_id):
    """pages primary oncall engineer for critical/urgent issues"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.pagerduty+json;version=2",
        "From": "dmansfield@cvent.com",
        "Authorization": f'Token token={get_ssm_param(os.environ["PD_TKN"])}',
    }

    url = "https://api.pagerduty.com/incidents"
    payload = {
        "incident": {
            "type": "incident",
            "title": f"Cloud Infra Walk Up Request - {ticket_id}",
            "service": {
                ## Cloud-Infrastructure-Nonpaging: https://cvent.pagerduty.com/service-directory/PNFEXB7
                ## Cloud-Infrastructure-Paging: https://cvent.pagerduty.com/service-directory/P3X5W9U
                "id": f'{get_ssm_param(os.environ["PD_SRV_ID"])}',
                "type": "service_reference",
            },
        },
        "urgency": "critical",
        "escalation_policy": {"id": "PD70OIX", "type": "escalation_policy_reference"},
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    return log.info(response.text)


def paging_hours():
    """Returns boolean if event occurs during off hours or weekends
    Standard hours 10am to 6pm EST and
    12:30am to 8:30am EST (10am to 6pm IST)
    """
    zone = timezone("US/Eastern")
    now = datetime.datetime.now(zone)

    # check for weekends
    if now.weekday() in [5, 6]:
        return True

    midnight = now.replace(hour=0, minute=0, second=0)
    if midnight <= now <= (midnight + datetime.timedelta(minutes=30)):
        return True

    gap1_start = now.replace(hour=8, minute=30, second=0)
    gap1_end = now.replace(hour=10, minute=0, second=0)
    if gap1_start <= now <= gap1_end:
        return True

    gap2_start = now.replace(hour=18, minute=0, second=0)
    gap2_end = now.replace(hour=23, minute=59, second=59)
    if gap2_start <= now <= gap2_end:
        return True

    return False
