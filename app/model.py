import logging
from typing import Dict

import uuid

from langchain_openai import OpenAI, ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from boto3.resources.base import ServiceResource
from boto3.dynamodb.conditions import Key

import langchain

from langchain import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from langchain_community.document_loaders import UnstructuredURLLoader

import pickle
import time

from app.api.entities import User,FeedBack

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

    def store_user_feedback(self, question: str, answer:str,feedback:str) -> str:
        record = FeedBack(question, answer,feedback)
        self.store_user_feedback_db(record)
        return 'saved to db'
    
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


    def store_user_feedback_db(self, user: User) -> None:
        request_id = uuid.uuid4()

        # Define the table name
        table = self.database.Table("skeleton_app_table")
        table.put_item(Item={
            'user_name': user.question,
            'request_id': str(request_id),
            'response':user.answer,
            'feedback': user.feedback
        })
    
    def search_websites(self, user_input: str) -> None:
        vectorstore_openai = self.create_embeddings()

        chain = RetrievalQAWithSourcesChain.from_llm(llm=self.openai, retriever=vectorstore_openai.as_retriever())
        langchain.debug=True
        result = chain({"question": user_input}, return_only_outputs=True)
        # output={}
        # print('type',type(result["answer"]))
        # print('type',type(result.get("sources", "")))
        # output['answer'] = result["answer"]
        # output['Citations'] = result.get("sources", "")
        # print(output)
        output = [result['answer'],result.get("sources", "")] 
        return output

    def create_embeddings(self):
        file_path = "faiss_store_openai.pkl"
        urls = [
            'https://www.ssa.gov/disability/professionals/bluebook/5.00-Digestive-Adult.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/1.00-Musculoskeletal-Adult.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/2.00-SpecialSensesandSpeech-Adult.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/3.00-Respiratory-Adult.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/4.00-Cardiovascular-Adult.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/6.00-Genitourinary-Adult.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/7.00-HematologicalDisorders-Adult.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/8.00-Skin-Adult.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/9.00-Endocrine-Adult.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/10.00-MultipleBody-Adult.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/11.00-Neurological-Adult.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/12.00-MentalDisorders-Adult.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/13.00-NeoplasticDiseases-Malignant-Adult.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/14.00-Immune-Adult.htm'

            'https://www.ssa.gov/disability/professionals/bluebook/100.00-GrowthImpairment-Childhood.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/101.00-Musculoskeletal-Childhood.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/102.00-SpecialSensesandSpeech-Childhood.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/103.00-Respiratory-Childhood.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/104.00-Cardiovascular-Childhood.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/105.00-Digestive-Childhood.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/106.00-Genitourinary-Childhood.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/107.00-HematologicalDisorders-Childhood.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/108.00-Skin-Childhood.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/109.00-Endocrine-Childhood.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/110.00-MultipleBody-Childhood.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/111.00-Neurological-Childhood.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/112.00-MentalDisorders-Childhood.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/113.00-NeoplasticDiseases-Malignant-Childhood.htm',
            'https://www.ssa.gov/disability/professionals/bluebook/114.00-Immune-Childhood.htm'

        ]
        # load data
        loader = UnstructuredURLLoader(urls=urls)
        data = loader.load()
        # split data
        text_splitter = RecursiveCharacterTextSplitter(
            separators=['\n\n', '\n', '.', ','],
            chunk_size=1000
        )
        docs = text_splitter.split_documents(data)
        # create embeddings and save it to FAISS index

        
        embeddings = OpenAIEmbeddings(openai_api_key=self.config_dict['open_ai_key'])
        vectorstore_openai = FAISS.from_documents(docs, embeddings)
        time.sleep(5)

        return vectorstore_openai
        

        # Save the FAISS index to a pickle file
        #with open(file_path, "wb") as f:
        #    pickle.dump(vectorstore_openai, f)
    
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
