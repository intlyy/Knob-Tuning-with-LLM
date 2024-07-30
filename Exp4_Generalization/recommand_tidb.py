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
{
    "tidb_mem_quota_query": {
        "max": 9223372036854775807,
        "min": -1,
        "type": "integer",
        "description": " set the threshold value of memory quota for a session."
    },
    "tidb_server_memory_limit": {
        "max": 99%,
        "min": 1%,
        "type": "integer",
        "description": "This variable specifies the memory limit for a TiDB instance. "
    },
    "tidb_server_memory_limit_gc_trigger": {
        "max": 99%,
        "min": 50%,
        "type": "integer",
        "description": "The threshold at which TiDB tries to trigger GC. When the memory usage of TiDB reaches the value of tidb_server_memory_limit * the value of tidb_server_memory_limit_gc_trigger, TiDB will actively trigger a Golang GC operation. Only one GC operation will be triggered in one minute."
    },
    "tidb_enable_tmp_storage_on_oom": {
        enum_value: [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Controls whether to enable the temporary storage for some operators when a single SQL statement exceeds the memory quota specified by the system variable tidb_mem_quota_query."
    },
    "scheduler-worker-pool-size": {
        "max": 12,
        "min": 1,
        "type": "integer",
        "description": "The number of threads in the Scheduler thread pool. Scheduler threads are mainly used for checking transaction consistency before data writing. If the number of CPU cores is greater than or equal to 16, the default value is 8; otherwise, the default value is 4. "
    },
    "write-buffer-size": {
        "max": 16GB,
        "min": 0,
        "type": "integer",
        "description": "Memtable size. "
    },
    "auto-adjust-pool-size": {
        enum_value: [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Controls whether to automatically adjust the thread pool size. "
    }
}
"""

inner_metrics = """
{
    numbackends , xact_commit , xact_rollback , blks_read , blks_hit  , tup_returned , tup_fetched , tup_inserted , tup_updated , tup_deleted , conflicts , temp_files , temp_bytes , deadlocks , blk_read_time , blk_write_time 
}
"""
environment = """
    - Workload: OLTP, SYSBENCH Read-Write Mixed Model, Read-Write Ratio = 50%, threads=32 .
    - Data: 13 GB data contains 50 tables and each table contains 1,000,000 rows of record.
    - Database Kernel: TiDB v8.2 .
    - Hardware: 12 vCPUs and 16 GB RAM.
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
        #max_tokens = 2036,
        #n = 1,
        #extra_body = extra_body
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
        api_key="token-abc123",
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
            Recommend optimal knob configuration in order to optimize the {db_metric} metric.

            Knobs:
            {knob}

            Workload and database kernel information: 
            {environment}

            Output Format:
            Strictly utilize the aforementioned knobs, ensuring that the generated configuration are formatted as follows:
            {{
                "knob_1": value_n, 
                ……
                "knob_n": value_n
            }}

            Current Configuration: Default 
            Database Feedback:
            - Throughput : {throughput} 

            Now, let's think step by step.

        """.format(  throughput = throughput, environment=environment, db_metric = db_metric, knob = knobs )
    }
    ]

    #llm_name = "llama3-70B-instruct"
    #llm_name = "llama3-8B-instruct"
    #llm_name = "qwen2-7B-instruct"
    # llm_name = "qwen2-72B-instruct"
    # llm_name = "mixtral-8x7B-instruct"
    

    if llm_name == "llama3-70B-instruct":
        base_url = 
        model = "meta-llama/Meta-Llama-3-70B-Instruct"
        extra_body = {"stop_token_ids": [128009, 128001]}
    elif llm_name == "llama3-8B-instruct":
        base_url = 
        model = "meta-llama/Meta-Llama-3-8B-Instruct"
        extra_body = {"stop_token_ids": [128009, 128001]}
    elif llm_name == "qwen2-7B-instruct":
        base_url = 
        model = "qwen/Qwen2-7B-Instruct"
        extra_body = {"stop_token_ids": [151645]}
    elif llm_name == "qwen2-72B-instruct":
        base_url = 
        model = "qwen/Qwen2-72B-Instruct"
        extra_body = {"stop_token_ids": [151645]}
    elif llm_name == "mixtral-8x7B-instruct":
        base_url = 
        model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
        extra_body = {"stop_token_ids": [2]}
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


