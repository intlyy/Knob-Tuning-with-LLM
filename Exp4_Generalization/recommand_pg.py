from flask import Flask, request, jsonify
from openai import OpenAI
import json
import re

history_knobs = """
{

}
"""

history_metrics = """
{

}
"""


history_output = """
{

}
"""


knobs = """
    Here are twenty three database knobs. They are configuration parameters of the database that directly affect its performance. There followed a list of their names、 meanings、 maximum value、 minimum value and boot value.
    1. autovacuum_analyze_scale_factor. Number of tuple inserts, updates, or deletes prior to analyze as a fraction of reltuples. 100.0, 0.0, 0.1. 
    2. autovacuum_analyze_threshold. Minimum number of tuple inserts, updates, or deletes prior to analyze. 10000000.0, 0.0, 50.0. 
    3. autovacuum_naptime. Time to sleep between autovacuum runs. 2147483.0, 1.0, 600.0. 
    4. autovacuum_vacuum_cost_delay. Vacuum cost delay in milliseconds, for autovacuum. 100.0, -1.0, 20.0. 
    5. autovacuum_vacuum_scale_factor. Number of tuple updates or deletes prior to vacuum as a fraction of reltuples. 100.0, 0.0, 0.2. 
    6. autovacuum_vacuum_threshold. Minimum number of tuple updates or deletes prior to vacuum. 10000000.0, 0.0, 50.0. 
    7. backend_flush_after. Number of pages after which previously performed writes are flushed to disk. 256.0, 0.0, 0.0. 
    8. bgwriter_flush_after. Number of pages after which previously performed writes are flushed to disk. 256.0, 0.0, 64.0. 
    9. bgwriter_lru_maxpages. Background writer maximum number of LRU pages to flush per round. 1000.0, 0.0, 100.0. 
    10. default_statistics_target. Sets the default statistics target. 10000.0, -100.0, 100.0. 
    ......
"""

inner_metrics = """
{
   
}
"""
environment = """
    - Workload: OLTP, SYSBENCH Read-Write Mixed Model, Read-Write Ratio = 50%, threads=32 .
    - Data: 13 GB data contains 50 tables and each table contains 1,000,000 rows of record.
    - Database Kernel: PostgreSQL 10.0.
    - Hardware: 8 vCPUs and 16 GB RAM.
"""


db_metric = "throughput"

def extract_key_value_pairs(json_string):
    pattern = re.compile(r'"(\w+)":\s*([\d.]+)')
    matches = pattern.findall(json_string)
    data = {key: value for key, value in matches}
    return data

def convert_to_bytes(value):
    units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4
    }
    match = re.match(r'(\d+)([KMGT]B)', value)
    if match:
        number = int(match.group(1))
        unit = match.group(2)
        return number * units[unit]
    return int(value)

def replace_units(json_string):
    def replace_match(match):
        return str(convert_to_bytes(match.group(0)))
    

    json_string = re.sub(r'\d+[KMGT]B', replace_match, json_string)
    return json_string


def call_open_source_llm(model, messages):



    client = OpenAI(

    )

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature = 0

    )

    for choice in completion.choices:

        print(choice.message.content)

        pattern = r'\{[^{}]+\}'
        match = re.search(pattern, choice.message.content, re.DOTALL)

        if match:
            json_str = match.group(0)
            json_str = replace_units(json_str)
            config_dict = extract_key_value_pairs(json_str)

            print(config_dict)
        else:
            print("No JSON configuration found in the input.")
            return 0

        return config_dict

def call_local_llm(base_url, model, extra_body, messages):


    client = OpenAI(
        base_url=base_url,
        api_key="",
    )

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature = 0,
        max_tokens = 2048,
        n = 1,
        extra_body = extra_body
    )

    for choice in completion.choices:

        pattern = r'\{[^{}]+\}'
        match = re.search(pattern, choice.message.content, re.DOTALL)

        if match:
            json_str = match.group(0)
            json_str = replace_units(json_str)
            config_dict = extract_key_value_pairs(json_str)
            print(config_dict)
        else:
            print("No JSON configuration found in the input.")
            return 0

        return config_dict




def process_data():

    throughput = 
    now_inner_metrics = 


    #last_knobs = json.dumps(last_knobs, indent=4)
    now_inner_metrics = json.dumps(now_inner_metrics, indent=4)

    #print(last_knobs)
    print(now_inner_metrics)
    print(throughput)

    if throughput == 0 :
        throughput = "0, because database starting failed under current configuration"
    
    messages = [
    {
        "role": "system",
        "content": """
            You are an experienced database administrators, skilled in database knob tuning.
        """
    },
    {
        "role": "user",
        "content": """
            Task Overview: 
            Recommend optimal knob configuration based on the inner metrics and workload characteristics in order to optimize the {db_metric} metric.

            Workload and database kernel information: 
            {environment}



            Output Format:
            Strictly utilize the aforementioned knobs, ensuring that the generated configuration are formatted as follows:
            {{
                "knob": value, 
                ……
            }}

            Current Configuration: Default 
            Database Feedback:
            - Throughput : {throughput} 

            Now, let's think step by step.

        """.format(  throughput = throughput, environment=environment, db_metric = db_metric )
    }
    ]

    # llm_name = "llama3-70B-instruct"
    #llm_name = "llama3-8B-instruct"
    #llm_name = "qwen2-7B-instruct"
    # llm_name = "qwen2-72B-instruct"
    # llm_name = "mixtral-8x7B-instruct"

    if llm_name == "llama3-70B-instruct":
        base_url = ""
        model = "meta-llama/Meta-Llama-3-70B-Instruct"
        extra_body = {"stop_token_ids": [128009, 128001]}
    elif llm_name == "llama3-8B-instruct":
        base_url = ""
        model = "meta-llama/Meta-Llama-3-8B-Instruct"
        extra_body = {"stop_token_ids": [128009, 128001]}
    elif llm_name == "qwen2-7B-instruct":
        base_url = ""
        model = "qwen/Qwen2-7B-Instruct"

    #model = "gpt-4o"
    #model = "gpt-4-0125-preview"
    #model = "claude-3-opus-20240229"
    #model = "gpt-3.5-turbo-0125"

    global last_result
    result = call_local_llm(base_url, model, extra_body, messages)
    #result = call_open_source_llm(model, messages)
    if (result == 0):
        result = last_result
        result = {
            "knob": result,
            "flag": 0
            }

    else:
        for k, v in result.items():
            print('{} = {}'.format(k, v))
        last_result = result
        result = {
            "knob": result,
            "flag": 1
            }
    

    print(result)

if __name__ == '__main__':
    process_data()
