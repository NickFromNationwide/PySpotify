from string import ascii_lowercase

import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError


class GenericDatabaseLayer(object):
    def __init__(self, table_name, key_name, region='us-west-2'):
        self.dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table_name = table_name
        self.table = self.dynamodb.Table(table_name)
        self.json_encoder_object = None
        self.primary_key_name = key_name
        self.sort_key_name = None

    def readFromDatabase(self, key_id, return_response=False, except_return="error", no_key_return=None):
        try:
            response = self.table.get_item(
                Key={
                    self.primary_key_name: key_id
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            if except_return == "error":
                return e.response['Error']['Message']
            else:
                return except_return
        else:
            try:
                item = response['Item']
            except KeyError:
                return no_key_return
            else:
                if return_response:
                    return item, response
                return item

    def appendToDatabase(self, key_id, parameter_dict=None, return_response=False, except_return="error"):
        if parameter_dict is None:
            parameter_dict = {}
        user_id_dictionary = {self.primary_key_name: key_id}
        item_dictionary = {**parameter_dict, **user_id_dictionary}
        try:
            response = self.table.put_item(
                Item=item_dictionary
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            if except_return == "error":
                return e.response['Error']['Message']
            else:
                return except_return
        else:
            if return_response:
                return True, response
            return True

    def updateToDatabase(self, key_id, update_dict=None, return_response=False, except_return="error"):
        if update_dict is None:
            update_dict = {}
        expression_template = "set {table_name} = :{letter}"
        second_expression_template = ", {table_name}=:{letter}"
        payload_dictionary = {}
        iter_key_id = 0
        update_expression = ""
        for item in update_dict:
            letter = ascii_lowercase[iter_key_id]
            payload_dictionary[str(':'+letter)] = update_dict[item]
            if iter_key_id == 0:
                update_expression = update_expression + expression_template.format(table_name=item, letter=letter)
            else:
                update_expression = update_expression + second_expression_template.format(table_name=item, letter=letter)

            iter_key_id = iter_key_id + 1

        try:
            response = self.table.update_item(
                Key={self.primary_key_name: key_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=payload_dictionary,
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            if except_return == "error":
                return e.response['Error']['Message']
            else:
                return except_return
        else:
            if return_response:
                return True, response
            return True

    def deleteFromDatabase(self, key_id, return_response=False, except_return="error"):
        try:
            response = self.table.delete_item(
                Key={self.primary_key_name: key_id}
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            if except_return == "error":
                return e.response['Error']['Message']
            else:
                return except_return
        else:
            if return_response:
                return True, response
            return True

    def scanFromDatabase(self, scan_attr, attr_value, no_key_return=None, except_return='error'):
        fe = Attr(scan_attr).eq(attr_value)
        try:
            response = self.table.scan(
                FilterExpression=fe
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            if except_return == "error":
                return e.response['Error']['Message']
            else:
                return except_return
        else:
            try:
                items = response['Items']
            except KeyError:
                return except_return
            else:
                if not items:
                    return no_key_return
                return items
