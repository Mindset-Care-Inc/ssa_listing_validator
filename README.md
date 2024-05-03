# ssa_listing_validator
Based on a set of Medical Records for an individual, use the Social Security Administration (SSA)'s Listings to measure how close the person's impairments align with the descriptions.

# Local env setup
Use the following links to setup your local enviorment

## Install Java
(Optional) Some steps may require Java so install a LTS release - https://www.oracle.com/java/technologies/downloads/#java21

## Install NoSQL Workbench + Local DynanoDB
NoSQL Workbench allow you to view/acess data from a local DynamoDB. Can run the local DynamoDB from tool - https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/workbench.settingup.install.html

Can also use a standalone local DynamoDB process - https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html#DynamoDBLocal.DownloadingAndRunning.title
Run with - `java -Djava.library.path=./dynamodb_local_latest -jar DynamoDBLocal.jar -sharedDb`

# How to run service
After creating a python virtualenv using the contents of the requirements.txt file (`pip install -r requirements.txt`), can start service using `python service.py`

# Untrack Config File
In case you don't want to have your local changes to config.json commited, you can use the following command to have it always ignored when making new changes. `git update-index --assume-unchanged config.json`



Must install on OSX
brew install libmagic
