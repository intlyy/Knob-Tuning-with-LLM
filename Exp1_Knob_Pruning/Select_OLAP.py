from openai import OpenAI

knobs = """
{
    "sort_buffer_size": {
        "max": 134217728,
        "min": 32768,
        "type": "integer",
        "description": "Each session that must perform a sort allocates a buffer of this size."
    },
    "innodb_random_read_ahead": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Enables the random read-ahead technique for optimizing InnoDB I/O."
    },
    "max_heap_table_size": {
        "max": 1073741824,
        "min": 16384,
        "type": "integer",
        "description": "This variable sets the maximum size to which user-created MEMORY tables are permitted to grow."
    },
    "tmp_table_size": {
        "max": 1073741824,
        "min": 1024,
        "type": "integer",
        "description": "The maximum size of internal in-memory temporary tables."
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
    "innodb_read_io_threads": {
        "max": 64,
        "min": 1,
        "type": "integer",
        "description": "The number of I/O threads for read operations in InnoDB."
    },
    "max_join_size": {
        "max": 18446744073709551615,
        "min": 1,
        "type": "integer",
        "description": "Do not permit statements that probably need to examine more than max_join_size rows (for single-table statements) or row combinations (for multiple-table statements) or that are likely to do more than max_join_size disk seeks."
    },
    "query_prealloc_size": {
        "max": 134217728,
        "min": 8192,
        "type": "integer",
        "description": "The size in bytes of the persistent buffer used for statement parsing and execution."
    },
    "innodb_sync_spin_loops": {
        "max": 30000,
        "min": 0,
        "type": "integer",
        "description": "The number of times a thread waits for an InnoDB mutex to be freed before the thread is suspended."
    },
    "innodb_purge_threads": {
        "max": 32,
        "min": 1,
        "type": "integer",
        "description": "The number of background threads devoted to the InnoDB purge operation."
    },
    "general_log": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Whether the general query log is enabled."
    },
    "max_delayed_threads": {
        "max": 16384,
        "min": 0,
        "type": "integer",
        "description": "This system variable is deprecated (because DELAYED inserts are not supported); expect it to be removed in a future release."
    },
    "max_binlog_size": {
        "max": 1073741824,
        "min": 4096,
        "type": "integer",
        "description": "If a write to the binary log causes the current log file size to exceed the value of this variable, the server rotates the binary logs (closes the current file and opens the next one)."
    },
    "read_buffer_size": {
        "max": 2147479552,
        "min": 8192,
        "type": "integer",
        "description": "Each thread that does a sequential scan for a MyISAM table allocates a buffer of this size (in bytes) for each table it scans."
    },
    "innodb_spin_wait_delay": {
        "max": 6000,
        "min": 0,
        "type": "integer",
        "description": "The maximum delay between polls for a spin lock."
    },
    "innodb_read_ahead_threshold": {
        "max": 64,
        "min": 0,
        "type": "integer",
        "description": "Controls the sensitivity of linear read-ahead that InnoDB uses to prefetch pages into the buffer pool."
    },
    "max_write_lock_count": {
        "max": 18446744073709551615,
        "min": 1,
        "type": "integer",
        "description": "After this many write locks, permit some pending read lock requests to be processed in between."
    },
    "query_cache_size": {
        "max": 2147483648,
        "min": 0,
        "type": "integer",
        "description": "The amount of memory allocated for caching query results."
    },
    "innodb_io_capacity": {
        "max": 2000000,
        "min": 100,
        "type": "integer",
        "description": "The innodb_io_capacity variable defines the number of I/O operations per second (IOPS) available to InnoDB background tasks, such as flushing pages from the buffer pool and merging data from the change buffer."
    },
    "query_alloc_block_size": {
        "max": 134217728,
        "min": 1024,
        "type": "integer",
        "description": "The allocation size in bytes of memory blocks that are allocated for objects created during statement parsing and execution."
    },
    "innodb_max_undo_log_size": {
        "max": 18446700000000000000,
        "min": 10485760,
        "type": "integer",
        "description": "Defines a threshold size for undo tablespaces."
    },
    "eq_range_index_dive_limit": {
        "max": 4294967295,
        "min": 0,
        "type": "integer",
        "description": "This variable indicates the number of equality ranges in an equality comparison condition when the optimizer should switch from using index dives to index statistics in estimating the number of qualifying rows."
    },
    "host_cache_size": {
        "max": 65536,
        "min": 0,
        "type": "integer",
        "description": "The MySQL server maintains an in-memory host cache that contains client host name and IP address information and is used to avoid Domain Name System (DNS) lookups; see Section5."
    },
    "max_binlog_cache_size": {
        "max": 18446744073709551615,
        "min": 4096,
        "type": "integer",
        "description": "If a transaction requires more than this many bytes, the server generates a Multi-statement transaction required more than 'max_binlog_cache_size' bytes of storage error."
    },
    "connect_timeout": {
        "max": 31536000,
        "min": 2,
        "type": "integer",
        "description": "The number of seconds that the mysqld server waits for a connect packet before responding with Bad handshake."
    },
    "innodb_io_capacity_max": {
        "max": 40000,
        "min": 100,
        "type": "integer",
        "description": "If flushing activity falls behind, InnoDB can flush more aggressively, at a higher rate of I/O operations per second (IOPS) than defined by the innodb_io_capacity variable."
    },
    "preload_buffer_size": {
        "max": 1073741824,
        "min": 1024,
        "type": "integer",
        "description": "The size of the buffer that is allocated when preloading indexes."
    },
    "max_seeks_for_key": {
        "max": 18446744073709551615,
        "min": 1,
        "type": "integer",
        "description": "Limit the assumed maximum number of seeks when looking up rows based on a key."
    },
    "stored_program_cache": {
        "max": 524288,
        "min": 16,
        "type": "integer",
        "description": "Sets a soft upper limit for the number of cached stored routines per connection."
    },
    "key_cache_block_size": {
        "max": 16384,
        "min": 512,
        "type": "integer",
        "description": "The size in bytes of blocks in the key cache."
    },
    "read_rnd_buffer_size": {
        "max": 134217728,
        "min": 1,
        "type": "integer",
        "description": "This variable is used for reads from MyISAM tables, and, for any storage engine, for Multi-Range Read optimization."
    },
    "optimizer_search_depth": {
        "max": 62,
        "min": 0,
        "type": "integer",
        "description": "The maximum depth of search performed by the query optimizer."
    },
    "key_cache_division_limit": {
        "max": 100,
        "min": 1,
        "type": "integer",
        "description": "The division point between the hot and warm sublists of the key cache buffer list."
    },
    "binlog_group_commit_sync_delay": {
        "max": 1000000,
        "min": 0,
        "type": "integer",
        "description": "Controls how many microseconds the binary log commit waits before synchronizing the binary log file to disk."
    },
    "innodb_max_purge_lag": {
        "max": 4294967295,
        "min": 0,
        "type": "integer",
        "description": "Defines the desired maximum purge lag."
    },
    "max_digest_length": {
        "max": 1048576,
        "min": 0,
        "type": "integer",
        "description": "The maximum number of bytes of memory reserved per session for computation of normalized statement digests."
    },
    "innodb_ft_num_word_optimize": {
        "max": 10000,
        "min": 1000,
        "type": "integer",
        "description": "Number of words to process during each OPTIMIZE TABLE operation on an InnoDB FULLTEXT index."
    },
    "innodb_commit_concurrency": {
        "max": 1000,
        "min": 0,
        "type": "integer",
        "description": "The number of threads that can commit at the same time."
    },
    "innodb_api_bk_commit_interval": {
        "max": 1073741824,
        "min": 1,
        "type": "integer",
        "description": "How often to auto-commit idle connections that use the InnoDB memcached interface, in seconds."
    },
    "group_concat_max_len": {
        "max": 18446700000000000000,
        "min": 4,
        "type": "integer",
        "description": "The maximum permitted result length in bytes for the GROUP_CONCAT() function."
    },
    "innodb_flushing_avg_loops": {
        "max": 1000,
        "min": 1,
        "type": "integer",
        "description": "Number of iterations for which InnoDB keeps the previously calculated snapshot of the flushing state, controlling how quickly adaptive flushing responds to changing workloads."
    },
    "innodb_log_file_size": {
        "max": 1073741824,
        "min": 4194304,
        "type": "integer",
        "description": "The size in bytes of each log file in a log group."
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
    "max_connections": {
        "max": 100000,
        "min": 1,
        "type": "integer",
        "description": "The maximum permitted number of simultaneous client connections."
    },
    "innodb_ft_total_cache_size": {
        "max": 1600000000,
        "min": 32000000,
        "type": "integer",
        "description": "The total memory allocated, in bytes, for the InnoDB full-text search index cache for all tables."
    },
    "innodb_online_alter_log_max_size": {
        "max": 18446700000000000000,
        "min": 65536,
        "type": "integer",
        "description": "Specifies an upper limit in bytes on the size of the temporary log files used during online DDL operations for InnoDB tables."
    },
    "innodb_ft_max_token_size": {
        "max": 84,
        "min": 10,
        "type": "integer",
        "description": "Maximum character length of words that are stored in an InnoDB FULLTEXT index."
    },
    "innodb_stats_transient_sample_pages": {
        "max": 100,
        "min": 1,
        "type": "integer",
        "description": "The number of index pages to sample when estimating cardinality and other statistics for an indexed column, such as those calculated by ANALYZE TABLE ."
    },
    "innodb_adaptive_flushing": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Specifies whether to dynamically adjust the rate of flushing dirty pages in the InnoDB buffer pool based on the workload."
    },
    "table_open_cache_instances": {
        "max": 64,
        "min": 1,
        "type": "integer",
        "description": "The number of open tables cache instances."
    },
    "transaction_prealloc_size": {
        "max": 131072,
        "min": 1024,
        "type": "integer",
        "description": "There is a per-transaction memory pool from which various transaction-related allocations take memory."
    },
    "table_open_cache": {
        "max": 250000,
        "min": 1,
        "type": "integer",
        "description": "The number of open tables for all threads."
    },
    "innodb_rollback_segments": {
        "max": 128,
        "min": 1,
        "type": "integer",
        "description": "Defines the number of rollback segments used by InnoDB for transactions that generate undo records."
    },
    "innodb_ft_enable_diag_print": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Whether to enable additional full-text search (FTS) diagnostic output."
    },
    "innodb_open_files": {
        "max": 655350,
        "min": 10,
        "type": "integer",
        "description": "Specifies the maximum number of files that InnoDB can have open at one time."
    },
    "log_syslog_include_pid": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Whether to include the server process ID in each line of error log output written to syslog."
    },
    "require_secure_transport": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Whether client connections to the server are required to use some form of secure transport."
    },
    "innodb_max_purge_lag_delay": {
        "max": 10000000,
        "min": 0,
        "type": "integer",
        "description": "Specifies the maximum delay in microseconds for the delay imposed when the innodb_max_purge_lag threshold is exceeded."
    },
    "default_week_format": {
        "max": 7,
        "min": 0,
        "type": "integer",
        "description": "The default mode value to use for the WEEK() function."
    },
    "query_cache_min_res_unit": {
        "max": 65536,
        "min": 512,
        "type": "integer",
        "description": "The minimum size (in bytes) for blocks allocated by the query cache."
    },
    "innodb_autoextend_increment": {
        "max": 1000,
        "min": 1,
        "type": "integer",
        "description": "The increment size (in megabytes) for extending the size of an auto-extending InnoDB system tablespace file when it becomes full."
    },
    "transaction_alloc_block_size": {
        "max": 131072,
        "min": 1024,
        "type": "integer",
        "description": "The amount in bytes by which to increase a per-transaction memory pool which needs memory."
    },
    "updatable_views_with_limit": {
        "enum_values": [
            "YES",
            "NO"
        ],
        "type": "enum",
        "description": "This variable controls whether updates to a view can be made when the view does not contain all columns of the primary key defined in the underlying table, if the update statement contains a LIMIT clause."
    },
    "query_cache_wlock_invalidate": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Normally, when one client acquires a WRITE lock on a table, other clients are not blocked from issuing statements that read from the table if the query results are present in the query cache."
    },
    "innodb_ft_cache_size": {
        "max": 80000000,
        "min": 1600000,
        "type": "integer",
        "description": "The memory allocated, in bytes, for the InnoDB FULLTEXT search index cache, which holds a parsed document in memory while creating an InnoDB FULLTEXT index."
    },
    "flush": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "If ON, the server flushes (synchronizes) all changes to disk after each SQL statement."
    },
    "innodb_use_native_aio": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Specifies whether to use the Linux asynchronous I/O subsystem."
    },
    "innodb_log_files_in_group": {
        "max": 10,
        "min": 2,
        "type": "integer",
        "description": "The number of log files in the log group."
    },
    "innodb_ft_min_token_size": {
        "max": 16,
        "min": 0,
        "type": "integer",
        "description": "Minimum length of words that are stored in an InnoDB FULLTEXT index."
    },
    "max_points_in_geometry": {
        "max": 1048576,
        "min": 3,
        "type": "integer",
        "description": "The maximum value of the points_per_circle argument to the ST_Buffer_Strategy() function."
    },
    "max_binlog_stmt_cache_size": {
        "max": 18446744073709500416,
        "min": 4096,
        "type": "integer",
        "description": "If nontransactional statements within a transaction require more than this many bytes of memory, the server generates an error."
    },
    "check_proxy_users": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Some authentication plugins implement proxy user mapping for themselves (for example, the PAM and Windows authentication plugins)."
    },
    "innodb_fill_factor": {
        "max": 100,
        "min": 10,
        "type": "integer",
        "description": "InnoDB performs a bulk load when creating or rebuilding indexes."
    },
    "innodb_buffer_pool_size": {
        "max": 17179869184,
        "min": 10737418240,
        "type": "integer",
        "description": "The size in bytes of the buffer pool, the memory area where InnoDB caches table and index data."
    },
    "log_queries_not_using_indexes": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "If you enable this variable with the slow query log enabled, queries that are expected to retrieve all rows are logged."
    },
    "show_compatibility_56": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "The INFORMATION_SCHEMA has tables that contain system and status variable information (see Section24."
    },
    "innodb_log_buffer_size": {
        "max": 4294967295,
        "min": 262144,
        "type": "integer",
        "description": "The size in bytes of the buffer that InnoDB uses to write to the log files on disk."
    },
    "skip_networking": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "This variable controls whether the server permits TCP/IP connections."
    },
    "div_precision_increment": {
        "max": 30,
        "min": 0,
        "type": "integer",
        "description": "This variable indicates the number of digits by which to increase the scale of the result of division operations performed with the / operator."
    },
    "innodb_undo_log_truncate": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "When enabled, undo tablespaces that exceed the threshold value defined by innodb_max_undo_log_size are marked for truncation."
    },
    "innodb_max_dirty_pages_pct_lwm": {
        "max": 99,
        "min": 0,
        "type": "integer",
        "description": "Defines a low water mark representing the percentage of dirty pages at which preflushing is enabled to control the dirty page ratio."
    },
    "innodb_compression_level": {
        "max": 9,
        "min": 0,
        "type": "integer",
        "description": "Specifies the level of zlib compression to use for InnoDB compressed tables and indexes."
    },
    "key_buffer_size": {
        "max": 17179869184,
        "min": 8,
        "type": "integer",
        "description": "Index blocks for MyISAM tables are buffered and are shared by all threads."
    },
    "innodb_print_all_deadlocks": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "When this option is enabled, information about all deadlocks in InnoDB user transactions is recorded in the mysqld error log."
    },
    "log_bin_use_v1_row_events": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Whether Version 2 binary logging is in use."
    },
    "log_statements_unsafe_for_binlog": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "If error 1592 is encountered, controls whether the generated warnings are added to the error log or not."
    },
    "innodb_deadlock_detect": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "This option is used to disable deadlock detection."
    },
    "innodb_stats_persistent": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Specifies whether InnoDB index statistics are persisted to disk."
    },
    "innodb_compression_pad_pct_max": {
        "max": 75,
        "min": 0,
        "type": "integer",
        "description": "Specifies the maximum percentage that can be reserved as free space within each compressed page, allowing room to reorganize the data and modification log within the page when a compressed table or index is updated and the data might be recompressed."
    },
    "innodb_sort_buffer_size": {
        "max": 67108864,
        "min": 65536,
        "type": "integer",
        "description": "This variable defines: For related information, see Section 14."
    },
    "innodb_ft_result_cache_limit": {
        "max": 4294967295,
        "min": 1000000,
        "type": "integer",
        "description": "The InnoDB full-text search query result cache limit (defined in bytes) per full-text search query or per thread."
    },
    "session_track_state_change": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "Controls whether the server tracks changes to the state of the current session and notifies the client when state changes occur."
    },
    "innodb_thread_sleep_delay": {
        "max": 1000000,
        "min": 0,
        "type": "integer",
        "description": "Defines how long InnoDB threads sleep before joining the InnoDB queue, in microseconds."
    },
    "sync_frm": {
        "enum_values": [
            "ON",
            "OFF"
        ],
        "type": "enum",
        "description": "If this variable is set to 1, when any nontemporary table is created its ."
    },
    "innodb_change_buffer_max_size": {
        "max": 50,
        "min": 0,
        "type": "integer",
        "description": "Maximum size for the InnoDB change buffer, as a percentage of the total size of the buffer pool."
    },
    "ft_min_word_len": {
        "max": 8,
        "min": 1,
        "type": "integer",
        "description": "The minimum length of the word to be included in a MyISAM FULLTEXT index."
    },
    "innodb_ft_sort_pll_degree": {
        "max": 16,
        "min": 1,
        "type": "integer",
        "description": "Number of threads used in parallel to index and tokenize text in an InnoDB FULLTEXT index when building a search index."
    },
    "innodb_adaptive_flushing_lwm": {
        "max": 70,
        "min": 0,
        "type": "integer",
        "description": "Defines the low water mark representing percentage of redo log capacity at which adaptive flushing is enabled."
    },
    "innodb_flush_log_at_trx_commit": {
        "enum_values": [
            "0",
            "1",
            "2"
        ],
        "type": "enum",
        "description": "Controls the balance between strict ACID compliance for commit operations and higher performance that is possible when commit-related I/O operations are rearranged and done in batches."
    },
    "innodb_flush_neighbors": {
        "enum_values": [
            "0",
            "1",
            "2"
        ],
        "type": "enum",
        "description": "Specifies whether flushing a page from the InnoDB buffer pool also flushes other dirty pages in the same extent."
    }
}
"""

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
            Select the 10 most important knobs from the 100 provided and give their range of values for the current tuning task in order to optmize the latency metric. 
            Workload and database kernel information: 
            - Workload: OLAP, JOB(join-order-benchmark) contains 113 multi-joint queries with realistic and complex joins, Read-Only .
            - Data: 8.9 GB data contains 21 tables.
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
        Now, let's think step by step.  Please note that the provided range only represents the upper and lower bounds of the values. Please determine the range of values based on the current situation      
        """.format(knob=knobs)
    }
]

def call_open_source_llm(model):
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

    )
    
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature = 0,
        max_tokens = 2036,
        n = 1,
        extra_body = extra_body
    )

    for choice in completion.choices:
        print(choice.message)
        print("--------------------------")

if __name__ == "__main__":
    #llm_name = "llama3-70B-instruct"
    #llm_name = "llama3-8B-instruct"
    #llm_name = "qwen2-7B-instruct"
    # llm_name = "qwen2-72B-instruct"
    # llm_name = "mixtral-8x7B-instruct"

    #model = "gpt-4-0125-preview"
    model = "claude-3-opus-20240229"



    #call_local_llm(base_url, model, extra_body)
    call_open_source_llm(model)