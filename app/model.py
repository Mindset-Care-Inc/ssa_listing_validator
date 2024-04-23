import logging
from typing import Dict

import uuid

from langchain_openai import OpenAI, ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from boto3.resources.base import ServiceResource
from boto3.dynamodb.conditions import Key

from app.api.entities import User

_logger = logging.getLogger(__name__)

class SkeletonApp():
    def __init__(self, database: ServiceResource, openai: OpenAI, config_dict: Dict) -> None:
        self.database: ServiceResource = database
        self.openai: OpenAI = openai
        self.config_dict: Dict = config_dict
        self.create_table()
    
    def hello_world(self, name: str) -> str:
        response = self.generate_response(name)
        record = User(name, response)
        self.store_user_record(record)
        return response
    
    def store_user_record(self, user: User) -> None:
        request_id = uuid.uuid4()
        response = user.response_msg.replace("'", "''")

        # Define the table name
        table = self.database.Table("skeleton_app_table")
        table.put_item(Item={
            'user_name': user.user_name,
            'request_id': str(request_id),
            'response':response
        })
    
    def get_response_count_by_user(self, name: str) -> int:
        # Define the table name
        table = self.database.Table("skeleton_app_table")

        # Query the table to get the latest item
        response = table.query(
            ScanIndexForward=False, # Descending order
            KeyConditionExpression=Key("user_name").eq(name)
        )

        return int(response['Count'])
    
    def create_table(self) -> None:
        existing_tables = self.database.meta.client.list_tables()['TableNames']
        if 'skeleton_app_table' not in existing_tables:
            table = self.database.create_table(
                TableName='skeleton_app_table',
                KeySchema=[
                    {'AttributeName':'user_name', 'KeyType': 'HASH'},
                    {'AttributeName':'request_id', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName':'user_name', 'AttributeType': 'S'},
                    {'AttributeName':'request_id', 'AttributeType': 'S'}
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
                }
            )

            table.wait_until_exists()
            print(f"Table 'skeleton_app_table' created.")
            print(f"Table item count: {table.item_count}.")
        else:
            print(f"Table 'skeleton_app_table' already exists.")
    
    def generate_response(self, name: str) -> str:
        chat_ai = ChatOpenAI(api_key=self.openai.openai_api_key)
        prompt = [
            SystemMessage(content="You're a helpful assistant. I would like you to answer questions in a positive manner."),
            HumanMessage(content=f"Can you reword the following phrase? 'Hello {name}! Nice to meet you.'"),
            SystemMessage(content="Please just response with the reworded phrase."),
            ]
        response = chat_ai.invoke(prompt)
        return str(response.content)
