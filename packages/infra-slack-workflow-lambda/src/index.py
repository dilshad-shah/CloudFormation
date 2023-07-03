"""
Lambda
"""
import json
import logging

from aws_lambda_typing.events.api_gateway_proxy import (
    APIGatewayProxyEventV1,
    RequestContextV1,
)
from aws_lambda_typing.responses.api_gateway_proxy import APIGatewayProxyResponseV1

from critical_workflow import critical_request
from general_workflow import general_request
from iam_workflow import iam_request

# from pr_workflow import pr_request
from utils.jira import upload_comment

log = logging.getLogger()
log.setLevel("INFO")
# FORMAT = "[%(filename)s:%(lineno)s - %(funcName)5s() ] %(message)s"
# logging.basicConfig(format=FORMAT , level=logging.INFO)


def handler(
    event: APIGatewayProxyEventV1,
    context: RequestContextV1,  # pylint: disable=unused-argument
) -> APIGatewayProxyResponseV1:
    """Lambda Handler"""
    # print("Received Event")
    # print(json.dumps(event))

    # stop slack retry events
    try:
        if event["headers"]["X-Slack-Retry-Num"]:
            return APIGatewayProxyResponseV1(
                statusCode=200,
                isBase64Encoded=True,
                body="success",
                headers={},
                multiValueHeaders={},
            )
    except KeyError:
        pass

    payload = json.loads(event.get("body"))
    clean_input = lambda inputString: inputString.translate(
        str.maketrans({"\n": r"\n", "\t": r"\t", "\\": r"\\"})
    ).replace('"', "*")

    log.info(f"PAYLOAD : {payload}")

    if "challenge" in payload.keys():
        return APIGatewayProxyResponseV1(statusCode=200, isBase64Encoded=True, body=payload["challenge"])

    if payload["event"]["type"] == "message":
        # avoid match against event type "reaction_added"
        # log.info(f"PAYLOAD : {payload}")
        slack_event = payload["event"]
        timestamp = slack_event["ts"]
        channel = slack_event["channel"]
        if "subtype" in slack_event.keys() and slack_event["subtype"] == "bot_message":
            slack_event_text = slack_event["text"]
            slack_event_text = clean_input(slack_event_text)

            if "*support request* submission from" in slack_event_text.lower():
                general_request(slack_event_text, channel, timestamp)
            elif "*active directory request* submission from" in slack_event_text.lower():
                iam_request(slack_event_text, channel, timestamp)
            elif "*911 escalation* submission from" in slack_event_text.lower():
                critical_request(slack_event_text, channel, timestamp)
            # elif "*pr review* submission form" in slack_event_text.lower():
            #     pr_request(slack_event_text, channel, timestamp)
        elif "subtype" in slack_event.keys() and slack_event["subtype"] != "file_share":
            # avoid match against subtype "message_changed"
            pass
        else:
            user = slack_event["user"]
            timestamp = slack_event["thread_ts"]
            if user not in ["UPPTPNRAQ", "U04R0U7PL6A", "U0552GL91C7"]:
                upload_comment(user_id=user, timestamp=timestamp, slack_event=slack_event)
    else:
        pass

    return APIGatewayProxyResponseV1(
        statusCode=200,
        isBase64Encoded=True,
        body="success",
        headers={},
        multiValueHeaders={},
    )
