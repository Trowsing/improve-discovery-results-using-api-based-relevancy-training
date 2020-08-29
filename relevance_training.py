import csv
import json

import requests
from ibm_cloud_sdk_core.api_exception import ApiException
from requests.auth import HTTPBasicAuth

import discovery_details as dt


def delete_and_add_example(query_id, document_id, relevance):
    deleteResult = dt.discovery.delete_training_example(
        dt.environment_id, dt.collection_id, query_id, document_id
    )
    print(f"Delete result = {json.dumps(deleteResult.get_result())}")
    add_example_result = dt.discovery.create_training_example(
        dt.environment_id,
        dt.collection_id,
        query_id,
        document_id=document_id,
        cross_reference=None,
        relevance=relevance,
    )
    print(f"add_example_result = {json.dumps(add_example_result.get_result())}")


def create_training_example(query_id, document_id, relevance):
    print("---")
    print(f"document_id = {document_id}")
    print(f"relevance = {relevance}")
    try:
        create_result = dt.discovery.create_training_example(
            dt.environment_id,
            dt.collection_id,
            query_id,
            document_id=document_id,
            cross_reference=None,
            relevance=relevance,
        )
        print(f"create_result = {json.dumps(create_result)}")
    except ApiException as apiE:
        if apiE.code == 409:  # Example already exists. Delete it and add
            print(
                "Example exists. Delete example and add example with new relevancy score"
            )
            delete_and_add_example(query_id, document_id, relevance)


# function for posting to training data endpoint
def training_post(training_obj):
    nlQuery = training_obj["natural_language_query"]
    examples = training_obj["examples"]
    try:
        dt.discovery.add_training_data(
            dt.environment_id,
            dt.collection_id,
            natural_language_query=nlQuery,
            filter=None,
            examples=examples,
        )
    except ApiException as apiE:
        # Check if the query already exists
        try:
            if apiE.code == 409:  # Query already exists
                error = apiE.message
                partAfterQueryId = error.split("id ", 1)[1]
                query_id = partAfterQueryId.split(" ", 1)[0]
                print("Query already exists. Add examples")
                print(f"query_id = {query_id}")

                for example in training_obj["examples"]:
                    create_training_example(
                        query_id, example["document_id"], example["relevance"]
                    )
            else:
                print(
                    f"""ApiException occurred in training_post when calling 
                    discovery.add_training_data api with error code = {apiE.code}"""
                )
                print(apiE)
                raise Exception(apiE)
        except Exception as e:
            print(
                "Exception occurred in training_post when calling discovery.add_training_data api"
            )
            print(e)
            raise Exception(e)


# open the training file and create new training data objects
with open("./training_file.tsv", "r") as training_doc:

    training_csv = csv.reader(training_doc, delimiter="\t")

    # create a new object for each example
    questions_count = 0
    for row in training_csv:
        noOfExamples = int((len(row) - 1) / 3)
        training_obj = {}
        training_obj["examples"] = []
        training_obj["natural_language_query"] = row[0]
        questions_count = questions_count + 1
        print(f"Question No. {questions_count}")
        print(f"""Question = {training_obj["natural_language_query"]}""")
        i = 1
        for j in range(1, noOfExamples + 1):
            example_obj = {}
            if row[i + 2] and row[i + 2].strip() == "":
                row[i + 2] = 0
            example_obj["relevance"] = row[i + 2]
            example_obj["document_id"] = row[i]
            if example_obj["document_id"]:
                training_obj["examples"].append(example_obj)
            i = i + 3

        training_post(training_obj)
        print("----------------")
    print(f"Number of questions = {questions_count}")
    print("**************")
    print("************** RELEVANCY TRAINING COMPLETED **************")
    print("**************")
