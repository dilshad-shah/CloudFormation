import logging
import time

from aws_lambda_typing import context as context_, events

from utils.jira import is_jira_ticket_closed
from utils.aws import delete_dynamodb_item, scan_dynamodb_items

log = logging.getLogger()
log.setLevel("INFO")

def handler(
    event: events.EventBridgeEvent,
    context: context_.Context,  # pylint: disable=unused-argument
):
    log.info(f"Lambda is Working")
    log.info(f"EVENT : {event}")

    try:
        now = time.time()
        one_month_ago = now - 60*60*24*30
        five_minutes_ago = now - 60*5
        old_items = scan_dynamodb_items(five_minutes_ago)
        log.info(f"old_items : {old_items}")

        for x in old_items:
            log.info(f"item : {x}")
            # if is_jira_ticket_closed(x) is True:
            #     delete_dynamodb_item(x)

    except:
        log.error("an error occurred")
        pass

    return