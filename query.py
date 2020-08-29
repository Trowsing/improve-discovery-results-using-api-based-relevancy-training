import csv
import json

import requests

import discovery_details as dt


output_file = open("./training_file.tsv", "w")
writer = csv.writer(output_file, delimiter="\t")
IDENTIFIER = "title"  # Key to identify a query result.

try:
    with open("./questions.txt") as questions:
        questions_count = 0
        for line in questions:
            print(f"Question No = {questions_count + 1}")
            question = line.replace("\n", "")
            print(f"Question = {question}")

            question = "%s" % (question)

            # run Discovery query to get results from untrained service
            result = dt.discovery.query(
                environment_id=dt.environment_id,
                collection_id=dt.collection_id,
                deduplicate=False,
                highlight=True,
                passages=True,
                passages_count=5,
                natural_language_query=question,
                count=5,
            )
            # print("Query Response = " + json.dumps(result.get_result()))

            # create a row for each query and results
            result_list = [question]
            for result_doc in result.get_result()["results"]:
                id = result_doc["id"]
                text = result_doc[IDENTIFIER]
                # for resultDoc in result.get_result()["passages"]:
                # id = resultDoc["document_id"]
                # text = resultDoc["passage_text"]
                if len(text) > 1000:
                    text = text[:1000]
                result_list.extend(
                    [id, text, " "]
                )  # leave a space to enter a relevance label for each doc

            # write the row to the file
            writer.writerow(result_list)
            questions_count = questions_count + 1
            print("==========================================================")
            print("")
    print("tsv file with questions and query results created")
    print(f"Number of questions processed = {questions_count}")
    output_file.close()
except Exception as e:
    print("Exception occurred ####### ")
    print(e)
