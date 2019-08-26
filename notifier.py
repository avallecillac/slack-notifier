import boto3
from datetime import datetime, timedelta
import json
import os
import copy
from botocore.exceptions import BotoCoreError


def handler(event, context):
    try:
        dynamodb = boto3.client("dynamodb")
        response = dynamodb.get_item(
            TableName=os.environ["ACCOUNTS_TABLE_NAME"],
            Key={
                'accountId': {
                    'S': event['accountId']
                }
            },
            ProjectionExpression="accountId,#name,slackChannels",
            ExpressionAttributeNames={"#name": "name"}
        )
    except Exception as e:
        print("Not able to get item from accounts table.")
        raise e
    notification_builder = NotificationBuilder()
    sns_message = notification_builder.get_notification(
        response['Item'], event)
    sns = boto3.client("sns")
    try:
        # sns.publish(
        #     TopicArn=os.environ["NOTIFICATION_TOPIC_ARN"],
        #     Message=json.dumps(sns_message)
        # )
        print("Slack Notification to be sent: {}".format(json.dumps(sns_message)))
        return event
    except Exception as e:
        print("Not able to publish message to sns notification topic")
        raise e


class NotificationBuilder:

    def __init__(self):
        self.slack_notification = copy.deepcopy({
            "type": "slack",
            "recipients": [
                os.environ['SLACK_NOTIFICATION_REPORT_PATH']
            ],
            "payload": {
                "text": "",
                "attachments": [
                    {
                        "color": "danger",
                        "fields": [],
                        "attachment_type": "default"
                    }
                ]
            }
        })

    def set_notification_fields(self, account, event):
        fields = [
            {
                "title": "AWS Account " + account['name']['S'],
                "value": "Account Id: " + account['accountId']['S'],
                "short": False
            },
            {
                "title": "Resource Type",
                "value": event['resourceType'],
                "short": False
            },
            {
                "title": "Resource Id",
                "value": event['resourceId'],
                "short": False
            },
            {
                "title": "NON-COMPLIANT Reason",
                "value": "Required Tags are not present",
                "short": False
            }
        ]
        self.slack_notification['payload']['attachments'][0]['fields'].extend(
            fields)

    def set_notification_recipients(self, account):
        if 'slackChannels' in account:
            for channel in account['slackChannels']['L']:
                self.slack_notification['recipients'].append(channel['S'])

    def get_first_notification(self, account, event):

        notification_time = datetime.strptime(
            event['notificationCreationTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
        deletion_time = notification_time + timedelta(days=14)
        notification_text = (
            "*A non-compliant resource has been created in your AWS Account* on {notificationTime}. \n"
            " *If no actions are taken, the resource will be DELETED on {deletionTime}*"
        ).format(notificationTime=notification_time, deletionTime=deletion_time)
        return notification_text

    def get_second_notification(self, account, event):
        notification_time = datetime.strptime(
            event['notificationCreationTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
        deletion_time = notification_time + timedelta(days=14)
        notification_text = (
            "*This notification is a reminder of a non-compliant resource created in your AWS Account* \n"
            "We advise you to take actions before it is DELETED on {deletionTime}*"
        ).format(notificationTime=notification_time, deletionTime=deletion_time)
        return notification_text

    def get_third_notification(self, account, event):
        notification_time = datetime.strptime(
            event['notificationCreationTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
        deletion_time = notification_time + timedelta(days=14)
        notification_text = (
            "*This notification is a reminder of a non-compliant resource created in your AWS Account* \n"
            " *If no actions are taken, the resource will be DELETED on {deletionTime}*"
        ).format(notificationTime=notification_time, deletionTime=deletion_time)
        return notification_text

    def get_error_notification(self, account, event):
        notification_text = (
            "*An unexpected error occured executing the state machine for required tags* \n"
            "{error}").format(error=event['error-info'])
        return notification_text

    def get_prod_notification(self, account, event):
        notification_time = datetime.strptime(
            event['notificationCreationTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
        notification_text = (
            "*A non-compliant resource has been created in your AWS Account* on {notificationTime}. \n"
            " *Please review the NON-COMPLIANT reason and take actions*"
        ).format(notificationTime=notification_time)

        return notification_text

    states = {
        "first_notification": get_first_notification,
        "second_notification": get_second_notification,
        "third_notification": get_third_notification,
        "error_notification": get_error_notification,
        "prod_notification": get_prod_notification
    }

    def get_notification(self, account, event):
        if 'error-info' in event:
            get_notification_text = self.states.get("error_notification")
        elif event['compliance']['accountType'] in ['prod']:
            get_notification_text = self.states.get("prod_notification")
            self.set_notification_recipients(account)
        else:
            get_notification_text = self.states.get(
                event['compliance']['next_state'], "Invalid state")
            self.set_notification_recipients(account)
        self.slack_notification['payload']['attachments'][0]['fields'] = []
        self.slack_notification['payload']['text'] = get_notification_text(
            self, account, event)
        self.set_notification_fields(account, event)
        return self.slack_notification
