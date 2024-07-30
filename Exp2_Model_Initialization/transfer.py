from openai import OpenAI
import json
import re


throughput = 

def extract_key_value_pairs(json_string):
    # extract "key": value model
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
history_knobs = """
{
    "tmp_table_size": 16127516,
    "max_heap_table_size": 542958715,
    "query_prealloc_size": 2897026,
    "innodb_thread_concurrency": 126,
    "sort_buffer_size": 127236112,
    "innodb_buffer_pool_size": 15169920679,
    "innodb_max_dirty_pages_pct_lwm": 54,
    "innodb_purge_threads": 29,
    "table_open_cache_instances": 53,
    "innodb_compression_failure_threshold_pct": 64,
    "innodb_purge_batch_size": 4630,
    "expire_logs_days": 55,
    "innodb_lru_scan_depth": 5027,
    "innodb_max_dirty_pages_pct": 59,
    "innodb_write_io_threads": 9,
    "innodb_stats_transient_sample_pages": 18,
    "div_precision_incrementm": 28,
    "innodb_spin_wait_delay": 5779,
    "innodb_compression_pad_pct_max": 29,
    "innodb_read_ahead_threshold": 25
}
"""

history_metrics = """
{
    "lock_deadlocks": 0,
    "lock_timeouts": 0,
    "lock_row_lock_current_waits": 0,
    "lock_row_lock_time": 0,
    "lock_row_lock_time_max": 0,
    "lock_row_lock_waits": 0,
    "lock_row_lock_time_avg": 0,
    "buffer_pool_size": 16106127360,
    "buffer_pool_reads": 94203,
    "buffer_pool_read_requests": 2990409,
    "buffer_pool_write_requests": 469598,
    "buffer_pool_wait_free": 0,
    "buffer_pool_read_ahead": 2317,
    "buffer_pool_read_ahead_evicted": 0,
    "buffer_pool_pages_total": 982980,
    "buffer_pool_pages_misc": 577,
    "buffer_pool_pages_data": 104773,
    "buffer_pool_bytes_data": 1716600832,
    "buffer_pool_pages_dirty": 40527,
    "buffer_pool_bytes_dirty": 663994368,
    "buffer_pool_pages_free": 877630,
    "buffer_pages_created": 705,
    "buffer_pages_written": 10900,
    "buffer_pages_read": 104068,
    "buffer_data_reads": 1703793152,
    "buffer_data_written": 394297344,
    "os_data_reads": 104135,
    "os_data_writes": 13327,
    "os_data_fsyncs": 5230,
    "os_log_bytes_written": 37642752,
    "os_log_fsyncs": 1979,
    "os_log_pending_fsyncs": 0,
    "os_log_pending_writes": 0,
    "trx_rseg_history_len": 4317,
    "log_waits": 0,
    "log_write_requests": 83048,
    "log_writes": 1959,
    "log_padded": 6734848,
    "adaptive_hash_searches": 131228,
    "adaptive_hash_searches_btree": 430491,
    "file_num_open_files": 66,
    "ibuf_merges_insert": 7424,
    "ibuf_merges_delete_mark": 14342,
    "ibuf_merges_delete": 3468,
    "ibuf_merges_discard_insert": 0,
    "ibuf_merges_discard_delete_mark": 0,
    "ibuf_merges_discard_delete": 0,
    "ibuf_merges": 16996,
    "ibuf_size": 77,
    "innodb_activity_count": 57537,
    "innodb_dblwr_writes": 437,
    "innodb_dblwr_pages_written": 10867,
    "innodb_page_size": 16384,
    "innodb_rwlock_s_spin_waits": 0,
    "innodb_rwlock_x_spin_waits": 0,
    "innodb_rwlock_sx_spin_waits": 290,
    "innodb_rwlock_s_spin_rounds": 17032,
    "innodb_rwlock_x_spin_rounds": 6593,
    "innodb_rwlock_sx_spin_rounds": 1292,
    "innodb_rwlock_s_os_waits": 93,
    "innodb_rwlock_x_os_waits": 38,
    "innodb_rwlock_sx_os_waits": 10,
    "dml_inserts": 13829,
    "dml_deletes": 13829,
    "dml_updates": 27658
}
"""

history_output = """
{
    "tmp_table_size": 866896964,
    "max_heap_table_size": 643296362,
    "query_prealloc_size": 2092905,
    "innodb_thread_concurrency": 285,
    "sort_buffer_size": 79669047,
    "innodb_buffer_pool_size": 11003533276,
    "innodb_max_dirty_pages_pct_lwm": 87,
    "innodb_purge_threads": 29,
    "table_open_cache_instances": 28,
    "innodb_compression_failure_threshold_pct": 80,
    "innodb_purge_batch_size": 4223,
    "expire_logs_days": 32,
    "innodb_lru_scan_depth": 9632,
    "innodb_max_dirty_pages_pct": 57,
    "innodb_write_io_threads": 31,
    "innodb_stats_transient_sample_pages": 80,
    "div_precision_increment": 5,
    "innodb_spin_wait_delay": 3278,
    "innodb_compression_pad_pct_max": 25,
    "innodb_read_ahead_threshold": 29
}
"""

last_knobs = """
{
    "tmp_table_size": 16777216,
    "max_heap_table_size": 16777216,
    "query_prealloc_size": 8192,
    "innodb_thread_concurrency": 0,
    "sort_buffer_size": 262144,
    "innodb_buffer_pool_size": 134217728,
    "innodb_max_dirty_pages_pct_lwm": 0,
    "innodb_purge_threads": 4,
    "table_open_cache_instances": 16,
    "innodb_compression_failure_threshold_pct": 5,
    "innodb_purge_batch_size": 300,
    "expire_logs_days": 0,
    "innodb_lru_scan_depth": 1024,
    "innodb_max_dirty_pages_pct": 75,
    "innodb_write_io_threads": 4,
    "innodb_stats_transient_sample_pages": 8,
    "div_precision_increment": 4,
    "innodb_spin_wait_delay": 6,
    "innodb_compression_pad_pct_max": 50,
    "innodb_read_ahead_threshold": 56
}
"""
now_inner_metrics = """
{
    "lock_deadlocks" : 0,
    "lock_timeouts" : 0,
    "lock_row_lock_current_waits" : 0,
    "lock_row_lock_time" : 0,
    "lock_row_lock_time_max" : 0,
    "lock_row_lock_waits" : 0,
    "lock_row_lock_time_avg" : 0,
    "buffer_pool_size" : 134217728,
    "buffer_pool_reads" : 42485,
    "buffer_pool_read_requests" : 673445,
    "buffer_pool_write_requests" : 117038,
    "buffer_pool_wait_free" : 1849,
    "buffer_pool_read_ahead" : 0,
    "buffer_pool_read_ahead_evicted" : 3438,
    "buffer_pool_pages_total" : 8191,
    "buffer_pool_pages_misc" : 274,
    "buffer_pool_pages_data" : 7916,
    "buffer_pool_bytes_data" : 129695744,
    "buffer_pool_pages_dirty" : 0,
    "buffer_pool_bytes_dirty" : 0,
    "buffer_pool_pages_free" : 1,
    "buffer_pages_created" : 220,
    "buffer_pages_written" : 16715,
    "buffer_pages_read" : 46759,
    "buffer_data_reads" : 766202368,
    "buffer_data_written" : 554740736,
    "os_data_reads" : 46833,
    "os_data_writes" : 18628,
    "os_data_fsyncs" : 7599,
    "os_log_bytes_written" : 7543808,
    "os_log_fsyncs" : 512,
    "os_log_pending_fsyncs" : 0,
    "os_log_pending_writes" : 0,
    "trx_rseg_history_len" : 106,
    "log_waits" : 0,
    "log_write_requests" : 16213,
    "log_writes" : 473,
    "log_padded" : 1313280,
    "adaptive_hash_searches" : 4561,
    "adaptive_hash_searches_btree" : 112144,
    "file_num_open_files" : 66,
    "ibuf_merges_insert" : 3617,
    "ibuf_merges_delete_mark" : 5039,
    "ibuf_merges_delete" : 1574,
    "ibuf_merges_discard_insert" : 0,
    "ibuf_merges_discard_delete_mark" : 0,
    "ibuf_merges_discard_delete" : 0,
    "ibuf_merges" : 6888,
    "ibuf_size" : 1,
    "innodb_activity_count" : 2922,
    "innodb_dblwr_writes" : 1155,
    "innodb_dblwr_pages_written" : 16681,
    "innodb_page_size" : 16384,
    "innodb_rwlock_s_spin_waits" : 0,
    "innodb_rwlock_x_spin_waits" : 0,
    "innodb_rwlock_sx_spin_waits" : 33,
    "innodb_rwlock_s_spin_rounds" : 9815,
    "innodb_rwlock_x_spin_rounds" : 18166,
    "innodb_rwlock_sx_spin_rounds" : 454,
    "innodb_rwlock_s_os_waits" : 667,
    "innodb_rwlock_x_os_waits" : 386,
    "innodb_rwlock_sx_os_waits" : 13,
    "dml_inserts" : 2589,
    "dml_deletes" : 2589,
    "dml_updates" : 5178
}
"""
environment = """
    - Workload: OLTP, SYSBENCH Read-Write Mixed Model, Read-Write Ratio = 50%, threads=32 .
    - Data: 13 GB data contains 50 tables and each table contains 1,000,000 rows of record.
    - Database Kernel: RDS MySQL 5.7.
    - Hardware: 8 vCPUs and 16 GB RAM.
"""


db_metric = "throughput"

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
                "knob": knbo_value, 
                ……
            }}

            Current Configuration:
            {last_knob}
            Database Feedback:
            - Throughput : {throughput} 
            - Inner Metrics: 
            {now_inner_metric}

            Now, let's think step by step.

        """.format(knob=knobs, inner_metric=inner_metrics, history_knob = history_knobs, history_metric = history_metrics,  history_output = history_output, environment=environment, db_metric = db_metric, last_knob = last_knobs, now_inner_metric = now_inner_metrics, throughput = throughput )
    }
]

def call_open_source_llm(model):

    client = OpenAI(

    )

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature = 1.0,
        top_p = 0.98
        #max_tokens = 2036,
        #n = 1,
        #extra_body = extra_body
    )

    for choice in completion.choices:
        print(choice.message)
        print("--------------------------")
        json_str = replace_units(choice.message.content)
        config_dict = extract_key_value_pairs(json_str) 
        print(config_dict)
        if not config_dict:
            print(0)
            return 0
        config_dict = json.dumps(config_dict)
        with open('history', 'r') as f:
            data_str = f.read()

        # Split the data into individual JSON strings
        json_strings = data_str.strip().split('\n')

        # # Prepare the final structured JSON format
        # for json_str in json_strings:
        #     d = json.loads(json_str)
        if config_dict in json_strings :
            print(-1)
            return 0
        with open('history', 'a') as f:
            print(1)
            f.write('\n')
            f.write(config_dict)
            return 1
        

def call_local_llm(base_url, model, extra_body):
    client = OpenAI(

    )

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature = 1.0,
        max_tokens = 2048,
        n = 1,
        extra_body = extra_body,
        top_p = 0.98
    )

    for choice in completion.choices:
        print(choice.message)
        print("--------------------------")
        json_str = replace_units(choice.message.content)
        config_dict = extract_key_value_pairs(json_str) 
        print(config_dict)
        if not config_dict:
            print(0)
            return 0
        config_dict = json.dumps(config_dict)
        with open('history_qianwen', 'r') as f:
            data_str = f.read()

        # Split the data into individual JSON strings
        json_strings = data_str.strip().split('\n')

        if config_dict in json_strings :
            print(-1)
            return 0
        with open('history_qianwen', 'a') as f:
            print(1)
            f.write('\n')
            f.write(config_dict)
            return 1

if __name__ == "__main__":
    #llm_name = "llama3-70B-instruct"
    #llm_name = "llama3-8B-instruct"
    llm_name = "qwen2-7B-instruct"
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

    #call_local_llm(base_url, model, extra_body)
    i = 0
    while i<15: 
        i = i+call_local_llm(base_url, model, extra_body)