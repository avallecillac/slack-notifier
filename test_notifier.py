import unittest
from notifier import NotificationBuilder
import os
import boto3
import copy
from moto import mock_dynamodb2, mock_sns
from unittest.mock import patch


@mock_dynamodb2
@mock_sns
class TestSendNotification(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.env = patch.dict('os.environ', {'SLACK_NOTIFICATION_REPORT_PATH': 'http://test.slack.test/infra', "ACCOUNTS_TABLE_NAME": "accounts-table", "NOTIFICATION_TOPIC_ARN":
                                             "arn:aws:sns:eu-west-1:123456789012:Notifications"})
        self.slack_notification = {
            "type": "slack",
            "recipients": [
                'http://test.slack.test/infra'
            ],
            "payload": {
                "text": "",
                "attachments": [
                        {
                            "color": "danger",
                            "fields": [
                                {
                                    "title": "AWS Account test-sandbox",
                                    "value": "Account Id: 012345678921",
                                    "short": False
                                },
                                {
                                    "title": "Resource Type",
                                    "value": "AWS::S3::TestResourceType",
                                    "short": False
                                },
                                {
                                    "title": "Resource Id",
                                    "value": "test-resource-id",
                                    "short": False
                                },
                                {
                                    "title": "NON-COMPLIANT Reason",
                                    "value": "Required Tags are not present",
                                    "short": False
                                }
                            ],
                            "attachment_type": "default"
                        }
                ]
            }
        }

    def tearDown(self):
        self.slack_notification = {}

    def test_error_notification(self):
        input_event = {
            "accountId": "012345678921",
            "resourceId": "test-resource-id",
            "resourceType": "AWS::S3::TestResourceType",
            "region": "eu-west-1",
            "notificationCreationTime": "2019-07-29T09:58:39.751Z",
            "error-info": {
                "message": "test error message"
            }
        }
        account_item = self.get_account_item()
        with self.env:
            notification = NotificationBuilder()
            result_message = notification.get_notification(
                account_item, input_event)
        expected_notification = copy.deepcopy(self.slack_notification)
        expected_notification["payload"]["text"] = (
            "*An unexpected error occured executing the state machine for required tags* \n"
            "{'message': 'test error message'}"
        )
        self.assertDictEqual(result_message, expected_notification)

    def test_first_notification_message(self):
        input_event = {
            "accountId": "012345678921",
            "resourceId": "test-resource-id",
            "resourceType": "AWS::S3::TestResourceType",
            "region": "eu-west-1",
            "notificationCreationTime": "2019-07-29T09:58:39.751Z",
            "compliance": {
                "compliant": "false",
                "next_state": "first_notification",
                "accountType": "sandbox"
            }
        }
        account_item = self.get_account_item()
        with self.env:
            notification = NotificationBuilder()
            result_message = notification.get_notification(
                account_item, input_event)
        expected_notification = copy.deepcopy(self.slack_notification)
        expected_notification["payload"]["text"] = (
            "*A non-compliant resource has been created in your AWS Account* on 2019-07-29 09:58:39.751000. \n"
            " *If no actions are taken, the resource will be DELETED on 2019-08-12 09:58:39.751000*"
        )
        expected_notification["recipients"].extend(
            self.get_account_slack_channels(account_item))
        self.assertDictEqual(result_message, expected_notification)

    def test_second_notification_message(self):
        input_event = {
            "accountId": "012345678921",
            "resourceId": "test-resource-id",
            "resourceType": "AWS::S3::TestResourceType",
            "region": "eu-west-1",
            "notificationCreationTime": "2019-07-29T09:58:39.751Z",
            "compliance": {
                "compliant": "false",
                "next_state": "second_notification",
                "accountType": "sandbox"
            }
        }
        account_item = self.get_account_item()
        with self.env:
            notification = NotificationBuilder()
            result_message = notification.get_notification(
                account_item, input_event)
        expected_notification = copy.deepcopy(self.slack_notification)
        expected_notification["payload"]["text"] = (
            "*This notification is a reminder of a non-compliant resource created in your AWS Account* \n"
            "We advise you to take actions before it is DELETED on 2019-08-12 09:58:39.751000*"
        )
        expected_notification["recipients"].extend(
            self.get_account_slack_channels(account_item))
        self.assertDictEqual(result_message, expected_notification)

    def test_third_notification_message(self):
        input_event = {
            "accountId": "012345678921",
            "resourceId": "test-resource-id",
            "resourceType": "AWS::S3::TestResourceType",
            "region": "eu-west-1",
            "notificationCreationTime": "2019-07-29T09:58:39.751Z",
            "compliance": {
                "compliant": "false",
                "next_state": "third_notification",
                "accountType": "sandbox"
            }
        }
        account_item = self.get_account_item()
        with self.env:
            notification = NotificationBuilder()
            result_message = notification.get_notification(
                account_item, input_event)
        expected_notification = copy.deepcopy(self.slack_notification)
        expected_notification["payload"]["text"] = (
            "*This notification is a reminder of a non-compliant resource created in your AWS Account* \n"
            " *If no actions are taken, the resource will be DELETED on 2019-08-12 09:58:39.751000*"
        )
        expected_notification["recipients"].extend(
            self.get_account_slack_channels(account_item))
        self.assertDictEqual(result_message, expected_notification)

    def test_third_notification_message(self):
        input_event = {
            "accountId": "012345678921",
            "resourceId": "test-resource-id",
            "resourceType": "AWS::S3::TestResourceType",
            "region": "eu-west-1",
            "notificationCreationTime": "2019-07-29T09:58:39.751Z",
            "compliance": {
                "compliant": "false",
                "next_state": "third_notification",
                "accountType": "sandbox"
            }
        }
        account_item = self.get_account_item()
        with self.env:
            notification = NotificationBuilder()
            result_message = notification.get_notification(
                account_item, input_event)
        expected_notification = copy.deepcopy(self.slack_notification)
        expected_notification["payload"]["text"] = (
            "*This notification is a reminder of a non-compliant resource created in your AWS Account* \n"
            " *If no actions are taken, the resource will be DELETED on 2019-08-12 09:58:39.751000*"
        )
        expected_notification["recipients"].extend(
            self.get_account_slack_channels(account_item))
        self.assertDictEqual(result_message, expected_notification)

    def test_prod_notification(self):
        input_event = {
            "accountId": "012345678921",
            "resourceId": "test-resource-id",
            "resourceType": "AWS::S3::TestResourceType",
            "region": "eu-west-1",
            "notificationCreationTime": "2019-07-29T09:58:39.751Z",
            "compliance": {
                "compliant": "false",
                "next_state": "third_notification",
                "accountType": "prod"
            }
        }
        account_item = self.get_account_item()
        with self.env:
            notification = NotificationBuilder()
            result_message = notification.get_notification(
                account_item, input_event)
        expected_notification = copy.deepcopy(self.slack_notification)
        expected_notification["payload"]["text"] = (
            "*A non-compliant resource has been created in your AWS Account* on 2019-07-29 09:58:39.751000. \n"
            " *Please review the NON-COMPLIANT reason and take actions*"
        )
        expected_notification["recipients"].extend(
            self.get_account_slack_channels(account_item))
        self.assertDictEqual(result_message, expected_notification)

    def get_account_item(self):
        account_item = {
            "accountId": {
                "S": "012345678921"
            },
            "name": {
                "S": "test-sandbox"
            },
            "slackChannels": {
                "L": [
                    {"S": "http://test.slack.test/1231231"},
                    {"S": "http://test.slack.test/2354234"},
                    {"S": "http://test.slack.test/4234543"}
                ]
            }
        }
        return account_item

    def get_account_slack_channels(self, account):
        slack_channels = []
        for channel in account['slackChannels']['L']:
            slack_channels.append(channel['S'])
        return slack_channels


if __name__ == "__main__":
    unittest.main()
