# Batch Document Redactor
Version: 1.0  
Author: Frank Gu  
Date: Feb 8, 2019  

# Overview
The batch document redactor is a CLI utility that redacts a folder of files given a list of terms for redaction. The process will produce output files in another specified folder, and preserve all tabs and newlines to ensure proper formatting. Redacted words will simply be shown as "<redacted n>", where n is the word's character length.

# Usage
On production data:
```bash
./redaction.py terms.txt input/ output/
```  

For debug outputs:
```bash
python3 ./redaction.py terms.txt input/ output/
```  

You can also specify the number of threads that you want spooled by including `--n N` flag. This number should not exceed 1.5x your actual core count. On smaller datasets (<10K items), single thread may perform better.

To generate **pydocs**:
```bash
pydocs -w redaction
```

# Implementation
This utility shall be designed to process a folder containing upwards of 10,000 files, each around 5kB and possibly over 1MB in size. The program shall minimize complexity and cost, but is not strictly required to run on a single host. The redaction shall be case-insensitive and applied to whole words only.

## Features
1. **terms_list dictionary**  
The dictionary uses upper-cased terms from the user-supplied redaction terms list as the key, and precomputed number of characters as the corresponding value. The upper-case consideration is to fulfil case-insensitive replacements. Precomputing the number of characters to replace can have performance benefits when large numbers of redactions take place; at the cost of more memory space (time-space tradeoff). The choice of a *dictionary* type ensures key uniqueness and speed of lookup.  

2. **Multi-threading**  
To take advantage of modern multi-processing systems, the utility will be multi-threaded with an optional CLI argument for the user to specify the number of threads. The `terms_list` dictionary will be a read-only shared data structure across all operating threads to eliminate data duplication space and time costs. The list is populated before thread spooling, and threads maintain read-only access to the `terms_list` thereby eliminating the need for locking on this data structure.

  The program also maintains a list of filenames to be processed obtained by scanning the input folder. This file list represents the work queue for the threads, and is lock-guarded by `list_lock`. File processing threads will acquire the lock, pop objects from this filename list to fetch the next file to process, and release the lock. Each spawned thread will continuously run until the filenames list is empty; when there are no more files to process.

  Multiprocessing was considered for parallel processing, but multi-threading proved more suitable for this use case. Due to process isolation, the `terms_list` data structure will require duplication. Furthermore, the isolation is also a problem for the implementation of the work queue. Granted, there are other approaches such as pre slicing the file list, the threaded approach seems to be the lightest-weight solution that can fully utilize available compute resources.

# Future Developments
It is possible to implement batch document redaction serverlessly on AWS using S3, SNS/SQS, and Lambda. The absolute costs of such a solution may not be lower than the conventional server approach, but the workload can be virtually scaled infinitely.  
