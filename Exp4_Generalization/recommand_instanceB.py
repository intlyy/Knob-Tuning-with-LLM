from flask import Flask, request, jsonify
from openai import OpenAI
import json
import re

history_knobs = """
{

}
"""
OLAP_history_knobs = """
{

}
"""

history_metrics = """
{

}
"""

OLAP_history_output = """
{

}
"""

history_output = """
{

}
"""

OLAP_knobs = """
    {
    "innodb_buffer_pool_size": {
        "max": 17179869184,   
        "min": 10737418240,
        "type": "integer",
        "description": "The size in bytes of the buffer pool, the memory area where InnoDB caches table and index data."
    },
    "sort_buffer_size": {
        "max": 134217728,
        "min": 32768,
        "type": "integer",
        "description": "This variable defines: For related information, see Section 14."
    },
    "read_buffer_size": {
        "max": 2147479552,
        "min": 8192,
        "type": "integer",
        "description": "Each thread that does a sequential scan for a MyISAM table allocates a buffer of this size (in bytes) for each table it scans."
    },
    "innodb_log_buffer_size": {
        "max": 4294967295,
        "min": 262144,
        "type": "integer",
        "description": "The size in bytes of the buffer that InnoDB uses to write to the log files on disk."
    },
    "innodb_io_capacity": {
        "max": 2000000,
        "min": 100,
        "type": "integer",
        "description": "The innodb_io_capacity variable defines the number of I/O operations per second (IOPS) available to InnoDB background tasks, such as flushing pages from the buffer pool and merging data from the change buffer."
    },
    "innodb_io_capacity_max": {
        "max": 40000,
        "min": 100,
        "type": "integer",
        "description": "If flushing activity falls behind, InnoDB can flush more aggressively, at a higher rate of I/O operations per second (IOPS) than defined by the innodb_io_capacity variable."
    },
    "max_connections": {
        "max": 100000,
        "min": 1,
        "type": "integer",
        "description": "The maximum permitted number of simultaneous client connections."

    },
    "innodb_thread_concurrency": {
        "max": 1000,
        "min": 0,
        "type": "integer",
        "description": "Defines the maximum number of threads permitted inside of InnoDB."
    },
    "query_cache_size": {
        "max": 2147483648,
        "min": 0,
        "type": "integer",
        "description": "The amount of memory allocated for caching query results."
    },
    "tmp_table_size": {
        "max": 1073741824,
        "min": 1024,
        "type": "integer",
        "description": "The maximum size of internal in-memory temporary tables."
    }
}
"""

knobs = """
{
    "tmp_table_size": {
        "max": 1073741824,
        "min": 1024,
        "type": "integer",
        "description": "The maximum size of internal in-memory temporary tables."
    },
    "max_heap_table_size": {
        "max": 1073741824,
        "min": 16384,
        "type": "integer",
        "description": "This variable sets the maximum size to which user-created MEMORY tables are permitted to grow."
    },
    "query_prealloc_size": {
        "max": 134217728,
        "min": 8192,
        "type": "integer",
        "description": "The size in bytes of the persistent buffer used for statement parsing and execution."
    },
    "innodb_thread_concurrency": {
        "max": 1000,
        "min": 0,
        "type": "integer",
        "description": "Defines the maximum number of threads permitted inside of InnoDB."
    },
    "sort_buffer_size": {
        "max": 134217728,
        "min": 32768,
        "type": "integer",
        "description": "Each session that must perform a sort allocates a buffer of this size."
    },
    "innodb_buffer_pool_size": {
        "max": 8589934592,
        "min": 5242880,
        "type": "integer",
        "description": "The size in bytes of the buffer pool, the memory area where InnoDB caches table and index data."
    },
    "innodb_max_dirty_pages_pct_lwm": {
        "max": 99,
        "min": 0,
        "type": "integer",
        "description": "Defines a low water mark representing the percentage of dirty pages at which preflushing is enabled to control the dirty page ratio."
    },
    "innodb_purge_threads": {
        "max": 32,
        "min": 1,
        "type": "integer",
        "description": "The number of background threads devoted to the InnoDB purge operation."
    },
    "table_open_cache_instances": {
        "max": 64,
        "min": 1,
        "type": "integer",
        "description": "The number of open tables cache instances."
    },
    "innodb_compression_failure_threshold_pct": {
        "max": 100,
        "min": 0,
        "type": "integer",
        "description": "Defines the compression failure rate threshold for a table, as a percentage, at which point MySQL begins adding padding within compressed pages to avoid expensive compression failures."
    },
    "innodb_purge_batch_size": {
        "max": 5000,
        "min": 1,
        "type": "integer",
        "description": "Defines the number of undo log pages that purge parses and processes in one batch from the history list."
    },
    "expire_logs_days": {
        "max": 99,
        "min": 0,
        "type": "integer",
        "description": "The number of days for automatic binary log file removal."
    },
    "innodb_lru_scan_depth": {
        "max": 10240,
        "min": 100,
        "type": "integer",
        "description": "A parameter that influences the algorithms and heuristics for the flush operation for the InnoDB buffer pool."
    },
    "innodb_max_dirty_pages_pct": {
        "max": 99,
        "min": 0,
        "type": "integer",
        "description": "InnoDB tries to flush data from the buffer pool so that the percentage of dirty pages does not exceed this value."
    },
    "innodb_write_io_threads": {
        "max": 64,
        "min": 1,
        "type": "integer",
        "description": "The number of I/O threads for write operations in InnoDB."
    },
    "innodb_stats_transient_sample_pages": {
        "max": 100,
        "min": 1,
        "type": "integer",
        "description": "The number of index pages to sample when estimating cardinality and other statistics for an indexed column, such as those calculated by ANALYZE TABLE ."
    },
    "div_precision_increment": {
        "max": 30,
        "min": 0,
        "type": "integer",
        "description": "This variable indicates the number of digits by which to increase the scale of the result of division operations performed with the / operator."
    },
    "innodb_spin_wait_delay": {
        "max": 6000,
        "min": 0,
        "type": "integer",
        "description": "The maximum delay between polls for a spin lock."
    },
    "innodb_compression_pad_pct_max": {
        "max": 75,
        "min": 0,
        "type": "integer",
        "description": "Specifies the maximum percentage that can be reserved as free space within each compressed page, allowing room to reorganize the data and modification log within the page when a compressed table or index is updated and the data might be recompressed."
    },
    "innodb_read_ahead_threshold": {
        "max": 64,
        "min": 0,
        "type": "integer",
        "description": "Controls the sensitivity of linear read-ahead that InnoDB uses to prefetch pages into the buffer pool."
    }
}
"""

inner_metrics = """
{
    "lock_deadlocks": "Number of deadlocks",
    "lock_timeouts": "Number of lock timeouts",
    "lock_row_lock_current_waits": "Number of row locks currently being waited for (innodb_row_lock_current_waits)",
    "lock_row_lock_time": "Time spent in acquiring row locks, in milliseconds (innodb_row_lock_time)",
    "lock_row_lock_time_max": "The maximum time to acquire a row lock, in milliseconds (innodb_row_lock_time_max)",
    "lock_row_lock_waits": "Number of times a row lock had to be waited for (innodb_row_lock_waits)",
    "lock_row_lock_time_avg": "The average time to acquire a row lock, in milliseconds (innodb_row_lock_time_avg)",
    "buffer_pool_size": "Server buffer pool size (all buffer pools) in bytes",
    "buffer_pool_reads": "Number of reads directly from disk (innodb_buffer_pool_reads)",
    "buffer_pool_read_requests": "Number of logical read requests (innodb_buffer_pool_read_requests)",
    "buffer_pool_write_requests": "Number of write requests (innodb_buffer_pool_write_requests)",
    "buffer_pool_wait_free": "Number of times waited for free buffer (innodb_buffer_pool_wait_free)",
    "buffer_pool_read_ahead": "Number of pages read as read ahead (innodb_buffer_pool_read_ahead)",
    "buffer_pool_read_ahead_evicted": "Read-ahead pages evicted without being accessed (innodb_buffer_pool_read_ahead_evicted)",
    "buffer_pool_pages_total": "Total buffer pool size in pages (innodb_buffer_pool_pages_total)",
    "buffer_pool_pages_misc": "Buffer pages for misc use such as row locks or the adaptive hash index (innodb_buffer_pool_pages_misc)",
    "buffer_pool_pages_data": "Buffer pages containing data (innodb_buffer_pool_pages_data)",
    "buffer_pool_bytes_data": "Buffer bytes containing data (innodb_buffer_pool_bytes_data)",
    "buffer_pool_pages_dirty": "Buffer pages currently dirty (innodb_buffer_pool_pages_dirty)",
    "buffer_pool_bytes_dirty": "Buffer bytes currently dirty (innodb_buffer_pool_bytes_dirty)",
    "buffer_pool_pages_free": "Buffer pages currently free (innodb_buffer_pool_pages_free)",
    "buffer_pages_created": "Number of pages created (innodb_pages_created)",
    "buffer_pages_written": "Number of pages written (innodb_pages_written)",
    "buffer_pages_read": "Number of pages read (innodb_pages_read)",
    "buffer_data_reads": "Amount of data read in bytes (innodb_data_reads)",
    "buffer_data_written": "Amount of data written in bytes (innodb_data_written)",
    "os_data_reads": "Number of reads initiated (innodb_data_reads)",
    "os_data_writes": "Number of writes initiated (innodb_data_writes)",
    "os_data_fsyncs": "Number of fsync() calls (innodb_data_fsyncs)",
    "os_log_bytes_written": "Bytes of log written (innodb_os_log_written)",
    "os_log_fsyncs": "Number of fsync log writes (innodb_os_log_fsyncs)",
    "os_log_pending_fsyncs": "Number of pending fsync write (innodb_os_log_pending_fsyncs)",
    "os_log_pending_writes": "Number of pending log file writes (innodb_os_log_pending_writes)",
    "trx_rseg_history_len": "Length of the TRX_RSEG_HISTORY list",
    "log_waits": "Number of log waits due to small log buffer (innodb_log_waits)",
    "log_write_requests": "Number of log write requests (innodb_log_write_requests)",
    "log_writes": "Number of log writes (innodb_log_writes)",
    "log_padded": "Bytes of log padded for log write ahead",
    "adaptive_hash_searches": "Number of successful searches using Adaptive Hash Index",
    "adaptive_hash_searches_btree": "Number of searches using B-tree on an index search",
    "file_num_open_files": "Number of files currently open (innodb_num_open_files)",
    "ibuf_merges_insert": "Number of inserted records merged by change buffering",
    "ibuf_merges_delete_mark": "Number of deleted records merged by change buffering",
    "ibuf_merges_delete": "Number of purge records merged by change buffering",
    "ibuf_merges_discard_insert": "Number of insert merged operations discarded",
    "ibuf_merges_discard_delete_mark": "Number of deleted merged operations discarded",
    "ibuf_merges_discard_delete": "Number of purge merged  operations discarded",
    "ibuf_merges": "Number of change buffer merges",
    "ibuf_size": "Change buffer size in pages",
    "innodb_activity_count": "Current server activity count",
    "innodb_dblwr_writes": "Number of doublewrite operations that have been performed (innodb_dblwr_writes)",
    "innodb_dblwr_pages_written": "Number of pages that have been written for doublewrite operations (innodb_dblwr_pages_written)",
    "innodb_page_size": "InnoDB page size in bytes (innodb_page_size)",
    "innodb_rwlock_s_spin_waits": "Number of rwlock spin waits due to shared latch request",
    "innodb_rwlock_x_spin_waits": "Number of rwlock spin waits due to exclusive latch request",
    "innodb_rwlock_sx_spin_waits": "Number of rwlock spin waits due to sx latch request",
    "innodb_rwlock_s_spin_rounds": "Number of rwlock spin loop rounds due to shared latch request",
    "innodb_rwlock_x_spin_rounds": "Number of rwlock spin loop rounds due to exclusive latch request",
    "innodb_rwlock_sx_spin_rounds": "Number of rwlock spin loop rounds due to sx latch request",
    "innodb_rwlock_s_os_waits": "Number of OS waits due to shared latch request",
    "innodb_rwlock_x_os_waits": "Number of OS waits due to exclusive latch request",
    "innodb_rwlock_sx_os_waits": "Number of OS waits due to sx latch request",
    "dml_inserts": "Number of rows inserted",
    "dml_deletes": "Number of rows deleted",
    "dml_updates": "Number of rows updated"
}
"""
environment = """
    - Workload: OLTP, SYSBENCH Read-Write Mixed Model, Read-Write Ratio = 50%, threads=32 .
    - Data: 13 GB data contains 50 tables and each table contains 1,000,000 rows of record.
    - Database Kernel: RDS MySQL 8.0.
    - Hardware: 40 vCPUs and 256 GB RAM.
"""

OLAP_environment = """
    - Workload: OLAP, JOB(join-order-benchmark) contains 113 multi-joint queries with realistic and complex joins, Read-Only .
    - Data: 13 GB data contains 50 tables and each table contains 1,000,000 rows of record.
    - Database Kernel: RDS MySQL 8.0.
    - Hardware: 8 vCPUs and 16 GB RAM.
"""

db_metric = "throughput"

def extract_key_value_pairs(json_string):
    pattern = re.compile(r'"(\w+)":\s*([\d.]+)')
    matches = pattern.findall(json_string)
    data = {key: int(value) for key, value in matches}
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


last_result = {

}


def process_data():
    last_knobs = {

}

    throughput = 
    now_inner_metrics = {

}


    last_knobs = json.dumps(last_knobs, indent=4)
    now_inner_metrics = json.dumps(now_inner_metrics, indent=4)

    print(last_knobs)
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

            Descriptions of Knobs and Inner Metrics:
            - knobs
            {knob}
            - inner metrics
            {inner_metric}

            Historical Knob Tuning Tasks:
            - Previous Configuration(input) :
            {history_knob}
            - Inner Metrics(input) :
            {history_metric}
            - Optimized Configuration(output) :
            {history_output}

            Output Format:
            Strictly utilize the aforementioned knobs, ensuring that the generated configuration are formatted as follows:
            {{
                "tmp_table_size": 16777216, 
                ……
                "innodb_read_ahead_threshold": 12
            }}

            Current Configuration:
            {last_knob}
            Database Feedback:
            - Throughput : {throughput} 
            - Inner Metrics: 
            {now_inner_metric}

            Now, let's think step by step.

        """.format(knob=knobs, inner_metric=inner_metrics, last_knob = last_knobs, now_inner_metric = now_inner_metrics, throughput = throughput, environment=environment, db_metric = db_metric, history_knob = history_knobs, history_metric = history_metrics, history_output = history_output )
    }
    ]

    #llm_name = "llama3-70B-instruct"
    #llm_name = "llama3-8B-instruct"
    #llm_name = "qwen2-7B-instruct"
    # llm_name = "qwen2-72B-instruct"
    # llm_name = "mixtral-8x7B-instruct"

    # if llm_name == "llama3-70B-instruct":
    #     base_url = 
    #     model = "meta-llama/Meta-Llama-3-70B-Instruct"
    #     extra_body = {"stop_token_ids": [128009, 128001]}
    # elif llm_name == "llama3-8B-instruct":
    #     base_url = 
    #     model = "meta-llama/Meta-Llama-3-8B-Instruct"
    #     extra_body = {"stop_token_ids": [128009, 128001]}
    # elif llm_name == "qwen2-7B-instruct":
    #     base_url = 
    #     model = "qwen/Qwen2-7B-Instruct"
    #     extra_body = {"stop_token_ids": [151645]}

    #model = "gpt-4o"
    #model = "gpt-4-0125-preview"
    model = "claude-3-opus-20240229"
    #model = "gpt-3.5-turbo-0125"

    global last_result
    #result = call_local_llm(base_url, model, extra_body, messages)
    result = call_open_source_llm(model, messages)
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
    
    # 
    print(result)

if __name__ == '__main__':
    process_data()
