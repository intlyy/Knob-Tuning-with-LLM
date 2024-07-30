import json

# giveb_json
given_json = {"tmp_table_size": 866896964, "max_heap_table_size": 643296362, "query_prealloc_size": 2092905, "innodb_thread_concurrency": 285, "sort_buffer_size": 79669047, "innodb_buffer_pool_size": 11003533276, "innodb_max_dirty_pages_pct_lwm": 87, "innodb_purge_threads": 29, "table_open_cache_instances": 28, "innodb_compression_failure_threshold_pct": 80, "innodb_purge_batch_size": 4223, "expire_logs_days": 32, "innodb_lru_scan_depth": 9632, "innodb_max_dirty_pages_pct": 57, "innodb_write_io_threads": 31, "innodb_stats_transient_sample_pages": 80, "div_precision_increment": 5, "innodb_spin_wait_delay": 3278, "innodb_compression_pad_pct_max": 25, "innodb_read_ahead_threshold": 29}

# get keys
given_keys = set(given_json.keys())

# read file
with open('history_qianwen', 'r') as f:
        data_str = f.read()

# Split the data into individual JSON strings
json_strings = data_str.strip().split('\n')

idx = 1
for json_str in json_strings:
    d = json.loads(json_str)
    record_keys = set(d.keys())    
    if record_keys == given_keys:
        print(f"Record {idx} has the same keys.")
    else:
        print(f"Record {idx} does not have the same keys.")
    idx = idx+1

# check
for idx, record in enumerate(output_data):
    record_keys = set(record.keys())
    if record_keys == given_keys:
        print(f"Record {idx} has the same keys.")
    else:
        print(f"Record {idx} does not have the same keys.")
