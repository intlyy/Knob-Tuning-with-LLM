from openai import OpenAI

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
    "innodb_doublewrite": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "When enabled (the default), InnoDB stores all data twice, first to the doublewrite buffer, then to the actual data files."
    },
    "sort_buffer_size": {
        "max": 134217728,
        "min": 32768,
        "type": "integer",
        "description": "Each session that must perform a sort allocates a buffer of this size."
    },
    "log_output": {
        "enum_values": [
            "TABLE",
            "FILE",
            "NONE"
        ],
        "type": "enum",
        "description": "The destination or destinations for general query log and slow query log output."
    },
    "general_log": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Whether the general query log is enabled."
    },
    "innodb_random_read_ahead": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Enables the random read-ahead technique for optimizing InnoDB I/O."
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
    "innodb_change_buffering": {
        "enum_values": [
            "none",
            "inserts",
            "deletes",
            "changes",
            "purges",
            "all"
        ],
        "type": "enum",
        "description": "Whether InnoDB performs change buffering, an optimization that delays write operations to secondary indexes so that the I/O operations can be performed sequentially."
    },
    "innodb_online_alter_log_max_size": {
        "max": 18446700000000000000,
        "min": 65536,
        "type": "integer",
        "description": "Specifies an upper limit in bytes on the size of the temporary log files used during online DDL operations for InnoDB tables."
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
    },
    "innodb_concurrency_tickets": {
        "max": 4294967295,
        "min": 1,
        "type": "integer",
        "description": "Determines the number of threads that can enter InnoDB concurrently."
    },
    "innodb_log_write_ahead_size": {
        "max": 16384,
        "min": 512,
        "type": "integer",
        "description": "Defines the write-ahead block size for the redo log, in bytes."
    },
    "innodb_change_buffer_max_size": {
        "max": 50,
        "min": 0,
        "type": "integer",
        "description": "Maximum size for the InnoDB change buffer, as a percentage of the total size of the buffer pool."
    },
    "long_query_time": {
        "max": 20,
        "min": 0,
        "type": "integer",
        "description": "If a query takes longer than this many seconds, the server increments the Slow_queries status variable."
    },
    "query_cache_limit": {
        "max": 134217728,
        "min": 0,
        "type": "integer",
        "description": "Do not cache results that are larger than this number of bytes."
    },
    "max_user_connections": {
        "max": 4294967295,
        "min": 0,
        "type": "integer",
        "description": "The maximum number of simultaneous connections permitted to any given MySQL user account."
    },
    "key_cache_block_size": {
        "max": 16384,
        "min": 512,
        "type": "integer",
        "description": "The size in bytes of blocks in the key cache."
    },
    "ngram_token_size": {
        "max": 10,
        "min": 1,
        "type": "integer",
        "description": "Defines the n-gram token size for the n-gram full-text parser."
    },
    "innodb_autoextend_increment": {
        "max": 1000,
        "min": 1,
        "type": "integer",
        "description": "The increment size (in megabytes) for extending the size of an auto-extending InnoDB system tablespace file when it becomes full."
    },
    "innodb_sort_buffer_size": {
        "max": 67108864,
        "min": 65536,
        "type": "integer",
        "description": "This variable defines: For related information, see Section 14."
    },
    "join_buffer_size": {
        "max": 1073741824,
        "min": 128,
        "type": "integer",
        "description": "The minimum size of the buffer that is used for plain index scans, range index scans, and joins that do not use indexes and thus perform full table scans."
    },
    "host_cache_size": {
        "max": 65536,
        "min": 0,
        "type": "integer",
        "description": "The MySQL server maintains an in-memory host cache that contains client host name and IP address information and is used to avoid Domain Name System (DNS) lookups; see Section5."
    },
    "net_write_timeout": {
        "max": 120,
        "min": 1,
        "type": "integer",
        "description": "The number of seconds to wait for a block to be written to a connection before aborting the write."
    },
    "binlog_row_image": {
        "enum_values": [
            "full",
            "minimal",
            "noblob"
        ],
        "type": "enum",
        "description": "For MySQL row-based replication, this variable determines how row images are written to the binary log."
    },
    "table_open_cache": {
        "max": 250000,
        "min": 1,
        "type": "integer",
        "description": "The number of open tables for all threads."
    },
    "innodb_adaptive_max_sleep_delay": {
        "max": 1000000,
        "min": 0,
        "type": "integer",
        "description": "Permits InnoDB to automatically adjust the value of innodb_thread_sleep_delay up or down according to the current workload."
    },
    "innodb_ft_total_cache_size": {
        "max": 1600000000,
        "min": 32000000,
        "type": "integer",
        "description": "The total memory allocated, in bytes, for the InnoDB full-text search index cache for all tables."
    },
    "read_buffer_size": {
        "max": 2147479552,
        "min": 8192,
        "type": "integer",
        "description": "Each thread that does a sequential scan for a MyISAM table allocates a buffer of this size (in bytes) for each table it scans."
    },
    "eq_range_index_dive_limit": {
        "max": 4294967295,
        "min": 0,
        "type": "integer",
        "description": "This variable indicates the number of equality ranges in an equality comparison condition when the optimizer should switch from using index dives to index statistics in estimating the number of qualifying rows."
    },
    "innodb_flush_log_at_timeout": {
        "max": 2700,
        "min": 1,
        "type": "integer",
        "description": "Write and flush the logs every N seconds."
    },
    "key_cache_age_threshold": {
        "max": 30000,
        "min": 100,
        "type": "integer",
        "description": "This value controls the demotion of buffers from the hot sublist of a key cache to the warm sublist."
    },
    "range_alloc_block_size": {
        "max": 65536,
        "min": 4096,
        "type": "integer",
        "description": "The size in bytes of blocks that are allocated when doing range optimization."
    },
    "innodb_ft_sort_pll_degree": {
        "max": 16,
        "min": 1,
        "type": "integer",
        "description": "Number of threads used in parallel to index and tokenize text in an InnoDB FULLTEXT index when building a search index."
    },
    "innodb_ft_min_token_size": {
        "max": 16,
        "min": 0,
        "type": "integer",
        "description": "Minimum length of words that are stored in an InnoDB FULLTEXT index."
    },
    "innodb_read_io_threads": {
        "max": 64,
        "min": 1,
        "type": "integer",
        "description": "The number of I/O threads for read operations in InnoDB."
    },
    "max_binlog_size": {
        "max": 1073741824,
        "min": 4096,
        "type": "integer",
        "description": "If a write to the binary log causes the current log file size to exceed the value of this variable, the server rotates the binary logs (closes the current file and opens the next one)."
    },
    "innodb_table_locks": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "If autocommit = 0 , InnoDB honors LOCK TABLES ; MySQL does not return from LOCK TABLES ."
    },
    "innodb_ft_result_cache_limit": {
        "max": 4294967295,
        "min": 1000000,
        "type": "integer",
        "description": "The InnoDB full-text search query result cache limit (defined in bytes) per full-text search query or per thread."
    },
    "innodb_purge_rseg_truncate_frequency": {
        "max": 128,
        "min": 1,
        "type": "integer",
        "description": "Defines the frequency with which the purge system frees rollback segments in terms of the number of times that purge is invoked."
    },
    "max_binlog_stmt_cache_size": {
        "max": 18446744073709500416,
        "min": 4096,
        "type": "integer",
        "description": "If nontransactional statements within a transaction require more than this many bytes of memory, the server generates an error."
    },
    "table_definition_cache": {
        "max": 524288,
        "min": 400,
        "type": "integer",
        "description": "The number of table definitions (from ."
    },
    "innodb_thread_sleep_delay": {
        "max": 1000000,
        "min": 0,
        "type": "integer",
        "description": "Defines how long InnoDB threads sleep before joining the InnoDB queue, in microseconds."
    },
    "innodb_adaptive_flushing_lwm": {
        "max": 70,
        "min": 0,
        "type": "integer",
        "description": "Defines the low water mark representing percentage of redo log capacity at which adaptive flushing is enabled."
    },
    "max_write_lock_count": {
        "max": 18446744073709551615,
        "min": 1,
        "type": "integer",
        "description": "After this many write locks, permit some pending read lock requests to be processed in between."
    },
    "innodb_io_capacity_max": {
        "max": 40000,
        "min": 100,
        "type": "integer",
        "description": "If flushing activity falls behind, InnoDB can flush more aggressively, at a higher rate of I/O operations per second (IOPS) than defined by the innodb_io_capacity variable."
    },
    "innodb_max_purge_lag": {
        "max": 4294967295,
        "min": 0,
        "type": "integer",
        "description": "Defines the desired maximum purge lag."
    },
    "sync_binlog": {
        "max": 4294967295,
        "min": 0,
        "type": "integer",
        "description": "Controls how often the MySQL server synchronizes the binary log to disk."
    },
    "optimizer_search_depth": {
        "max": 62,
        "min": 0,
        "type": "integer",
        "description": "The maximum depth of search performed by the query optimizer."
    },
    "session_track_schema": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Controls whether the server tracks when the default schema (database) is set within the current session and notifies the client to make the schema name available."
    },
    "transaction_prealloc_size": {
        "max": 131072,
        "min": 1024,
        "type": "integer",
        "description": "There is a per-transaction memory pool from which various transaction-related allocations take memory."
    },
    "thread_cache_size": {
        "max": 16384,
        "min": 0,
        "type": "integer",
        "description": "How many threads the server should cache for reuse."
    },
    "query_cache_size": {
        "max": 2147483648,
        "min": 0,
        "type": "integer",
        "description": "The amount of memory allocated for caching query results."
    },
    "flush_time": {
        "max": 10,
        "min": 0,
        "type": "integer",
        "description": "If this is set to a nonzero value, all tables are closed every flush_time seconds to free up resources and synchronize unflushed data to disk."
    },
    "low_priority_updates": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "If set to 1, all INSERT, UPDATE, DELETE, and LOCK TABLE WRITE statements wait until there is no pending SELECT or LOCK TABLE READ on the affected table."
    },
    "ft_query_expansion_limit": {
        "max": 1000,
        "min": 0,
        "type": "integer",
        "description": "The number of top matches to use for full-text searches performed using WITH QUERY EXPANSION."
    },
    "max_error_count": {
        "max": 65535,
        "min": 0,
        "type": "integer",
        "description": "The maximum number of error, warning, and information messages to be stored for display by the SHOW ERRORS and SHOW WARNINGS statements."
    },
    "binlog_group_commit_sync_no_delay_count": {
        "max": 100000,
        "min": 0,
        "type": "integer",
        "description": "The maximum number of transactions to wait for before aborting the current delay as specified by binlog_group_commit_sync_delay."
    },
    "max_join_size": {
        "max": 18446744073709551615,
        "min": 1,
        "type": "integer",
        "description": "Do not permit statements that probably need to examine more than max_join_size rows (for single-table statements) or row combinations (for multiple-table statements) or that are likely to do more than max_join_size disk seeks."
    },
    "innodb_log_file_size": {
        "max": 1073741824,
        "min": 4194304,
        "type": "integer",
        "description": "The size in bytes of each log file in a log group."
    },
    "default_week_format": {
        "max": 7,
        "min": 0,
        "type": "integer",
        "description": "The default mode value to use for the WEEK() function."
    },
    "session_track_transaction_info": {
        "enum_values": [
            "OFF",
            "STATE",
            "CHARACTERISTICS"
        ],
        "type": "enum",
        "description": "Controls whether the server tracks the state and characteristics of transactions within the current session and notifies the client to make this information available."
    },
    "open_files_limit": {
        "max": 655350,
        "min": 0,
        "type": "integer",
        "description": "The number of file descriptors available to mysqld from the operating system: The effective open_files_limit value is based on the value specified at system startup (if any) and the values of max_connections and table_open_cache, using these formulas: The server attempts to obtain the number of file descriptors using the maximum of those values."
    },
    "flush": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "If ON, the server flushes (synchronizes) all changes to disk after each SQL statement."
    },
    "innodb_flush_neighbors": {
        "enum_values": [
            "0",
            "1",
            "2"
        ],
        "type": "enum",
        "description": "Specifies whether flushing a page from the InnoDB buffer pool also flushes other dirty pages in the same extent."
    },
    "concurrent_insert": {
        "enum_values": [
            "NEVER",
            "AUTO",
            "ALWAYS"
        ],
        "type": "enum",
        "description": "If AUTO (the default), MySQL permits INSERT and SELECT statements to run concurrently for MyISAM tables that have no free blocks in the middle of the data file."
    },
    "innodb_fill_factor": {
        "max": 100,
        "min": 10,
        "type": "integer",
        "description": "InnoDB performs a bulk load when creating or rebuilding indexes."
    },
    "back_log": {
        "max": 65535,
        "min": 1,
        "type": "integer",
        "description": "The number of outstanding connection requests MySQL can have."
    },
    "net_read_timeout": {
        "max": 60,
        "min": 1,
        "type": "integer",
        "description": "The number of seconds to wait for more data from a connection before aborting the read."
    },
    "innodb_compression_level": {
        "max": 9,
        "min": 0,
        "type": "integer",
        "description": "Specifies the level of zlib compression to use for InnoDB compressed tables and indexes."
    },
    "binlog_direct_non_transactional_updates": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Due to concurrency issues, a replica can become inconsistent when a transaction contains updates to both transactional and nontransactional tables."
    },
    "session_track_state_change": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Controls whether the server tracks changes to the state of the current session and notifies the client when state changes occur."
    },
    "automatic_sp_privileges": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "When this variable has a value of 1 (the default), the server automatically grants the EXECUTE and ALTER ROUTINE privileges to the creator of a stored routine, if the user cannot already execute and alter or drop the routine."
    },
    "transaction_alloc_block_size": {
        "max": 131072,
        "min": 1024,
        "type": "integer",
        "description": "The amount in bytes by which to increase a per-transaction memory pool which needs memory."
    },
    "innodb_old_blocks_time": {
        "max": 4294967295,
        "min": 0,
        "type": "integer",
        "description": "Non-zero values protect against the buffer pool being filled by data that is referenced only for a brief period, such as during a full table scan."
    },
    "show_compatibility_56": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "The INFORMATION_SCHEMA has tables that contain system and status variable information (see Section24."
    },
    "innodb_replication_delay": {
        "max": 10000,
        "min": 0,
        "type": "integer",
        "description": "The replication thread delay in milliseconds on a replica server if innodb_thread_concurrency is reached."
    },
    "max_sort_length": {
        "max": 8388608,
        "min": 4,
        "type": "integer",
        "description": "The number of bytes to use when sorting data values."
    },
    "innodb_page_cleaners": {
        "max": 8,
        "min": 1,
        "type": "integer",
        "description": "The number of page cleaner threads that flush dirty pages from buffer pool instances."
    },
    "innodb_sync_spin_loops": {
        "max": 30000,
        "min": 0,
        "type": "integer",
        "description": "The number of times a thread waits for an InnoDB mutex to be freed before the thread is suspended."
    },
    "explicit_defaults_for_timestamp": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "This system variable determines whether the server enables certain nonstandard behaviors for default values and NULL-value handling in TIMESTAMP columns."
    },
    "ft_min_word_len": {
        "max": 8,
        "min": 1,
        "type": "integer",
        "description": "The minimum length of the word to be included in a MyISAM FULLTEXT index."
    },
    "stored_program_cache": {
        "max": 524288,
        "min": 16,
        "type": "integer",
        "description": "Sets a soft upper limit for the number of cached stored routines per connection."
    },
    "connect_timeout": {
        "max": 31536000,
        "min": 2,
        "type": "integer",
        "description": "The number of seconds that the mysqld server waits for a connect packet before responding with Bad handshake."
    },
    "innodb_adaptive_hash_index_parts": {
        "max": 512,
        "min": 1,
        "type": "integer",
        "description": "Partitions the adaptive hash index search system."
    }
}
"""

messages = [
    {"role": "system", "content": "You are an experienced database administrators, skilled in database knob tuning."},
    {
        "role": "user",
        "content": """
            Task Overview: 
            Select the 10 most important knobs from the 100 provided and give their range of values for the current tuning task in order to optmize the throughput metric. 
            Workload and database kernel information: 
            - Workload: OLTP, SYSBENCH Read-Write Mixed Model, Read-Write Ratio = 50%, threads=32 .
            - Data: 13 GB data contains 50 tables and each table contains 1,000,000 rows of record.
            - Database Kernel: RDS MySQL 5.7.
            - Hardware: 8 vCPUs and 16 GB RAM.
            Candidate knobs:
            {knob}
            Output Format:
            Knobs should be formatted as follows:
            "knob_name": {{
                "enum_values": [
                    "value1",
                    "value2",
                    ...
                ],
                "type": "enum"
            }} 
            or
            "knob_name": {{
                "max": MAX_Value,
                "min": Min_Value,
                "type": "integer"
             }}        
        """.format(knob=knobs)
    }
]


def call_open_source_llm_1(model):
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
        print(choice.message)
        print("--------------------------")

def call_local_llm(base_url, model, extra_body):
    client = OpenAI(
        base_url=base_url,
        api_key="",
    )

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature = 0,
        max_tokens = 2026,
        n = 1,
        extra_body = extra_body
    )

    for choice in completion.choices:
        print(choice.message)
        print("--------------------------")

if __name__ == "__main__":
    #llm_name = "llama3-70B-instruct"
    #llm_name = "llama3-8B-instruct"
    llm_name = "qwen2-7B-instruct"
    # llm_name = "qwen2-72B-instruct"
    # llm_name = "mixtral-8x7B-instruct"

    #model = "claude-3-opus-20240229"

    if llm_name == "llama3-70B-instruct":
        base_url = 
        model = "meta-llama/Meta-Llama-3-70B-Instruct"
        extra_body = {"stop_token_ids": [128009, 128001]}
    elif llm_name == "llama3-8B-instruct":
        base_url = "http://10.77.110.162:11003/v1"
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

    call_local_llm(base_url, model, extra_body)
    #call_open_source_llm_1 (model)