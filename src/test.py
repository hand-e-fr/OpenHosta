from flask import Flask, render_template, request, send_from_directory, redirect, session, jsonify
import os
import yaml
from functools import wraps
import sys
from typing import List, Tuple

from OpenHosta.OpenHosta import emulate, config

API_KEY=""

search_model = config.Model(
    model="gpt-4o", 
    base_url="https://api.openai.com/v1/chat/completions",
    api_key=API_KEY
)

config.set_default_apiKey(api_key=API_KEY)

data_folder = "data"


def load_reports():
    reports = []
    for folder_name in os.listdir(data_folder+'/yaml'):
        if folder_name.endswith('.yaml'):
            with open(os.path.join(data_folder,'yaml', folder_name), 'r') as file:
                report_data = yaml.safe_load(file)
                report_data["file"]=folder_name
                reports.append(report_data)
    return reports

reports = load_reports()


def build_report_search_database():
    global reports
    report_id=[]
    dashboard_id=[]
    dashboard_names=[]
    question_list=[]
    chart_types=[]
    
    report_index = 0
    for r in reports:
        dashboard_index = 0
        for d in r["dashboards"]:
            for w in d["worksheets"]:
                dashboard_names.append(d["name"])
                question_list.append(f"{w["question"]}  Subject: {d["name"]} Report: {r["overview"]["code"]} Chart type: {w["type"]}")
                chart_types.append(w["type"])
                report_id.append(report_index)
                dashboard_id.append(dashboard_index)
            dashboard_index += 1
        report_index += 1

    table = list(zip(report_id, dashboard_id, question_list))
    return table


def semantic_search(query: str, documents: str) -> list:
    """
    Compare query with all strings in documents and find the 3 best match. Returns report and dashboard numbers

    query: 
        The natural language query entered by a user that serch for the right dashboard in the list of documens
        Query can be in any language but documents are described in English
    documents: 
        The list of documents to search in, each document is composed of a report number, a dashboard number and a text describing thequestion it answers

    return:
        the best match for the query in the documents. 
        it returns the report number, and dashboard number
        for each result, provide a signle word that explain why it match the query (subsystem, variable, issue, ...)

        exemple: [(1, 2, 'temperature'), (3, 1, 'speed'), (5, 3, 'failure')]
    """
    return emulate()

docs=build_report_search_database()


query=sys.argv[1]

doc_str="\n".join([f"{a}, {b}, {t}" for a,b,t in docs])
print("query:", query)
res = semantic_search(query=query, documents=doc_str)
print(res)
print("\n".join([f"{reports[i]["overview"]["code"]}: {reports[i]["dashboards"][j]["name"]} => {l}" for i,j,l in res]))

