#!/usr/bin/env python3 -O
# -*- coding: utf-8 -*-

"""
    File name: redaction.py
    Author: Frank Gu
    Date created: Feb 8, 2019
    Date last modified: Feb 8, 2019
    Python Version: 3.7
"""

import argparse
from os import listdir
from os.path import join, isfile
import threading
import time

VERSION_STRING = "v1.0"

terms = dict()      # Dictionary of terms
file_list = []      # Shared list of files to process
list_lock = threading.Lock()    # Lock for file_list


def load_terms(f_input):
    """
    Load the terms dictionary using term as key and calculate length as value
    Provides a slight performance boost to not recalculate length every time

    :param f_input: Terms file path
    :return: void
    """
    with open(f_input, "r", encoding="utf8") as f:
        for line in f:
            sanitized_line = line.strip().upper()
            terms[sanitized_line] = str(len(sanitized_line))


def process_file(f_input, input_folder, f_output):
    """
    Redaction processing for a single file

    :param f_input:     Input file name
    :param input_folder: Input folder path
    :param f_output:    Output folder path
    :return: void
    """
    global terms

    output_token_list = []
    with open(join(input_folder, f_input), "r", encoding="utf8") as f:
        string_buffer = f.read().replace('\n', ' \n')       # Preserve newlines
        string_buffer = string_buffer.replace('\t', ' \t')  # Preserve tabs
        token_buffer = string_buffer.split(' ')             # Only split on whitespace
        for token in token_buffer:
            if token.upper() in terms.keys():
                output_token_list.append("<removed " + terms[token.upper()] + ">")
            else:
                output_token_list.append(token)

        result_string = " ".join(output_token_list)
        output_file = open(join(f_output, f_input), "w", encoding="utf8")
        output_file.write(result_string)


class FileProcessor(threading.Thread):
    def __init__(self, thread_id, input_folder, output_folder):
        threading.Thread.__init__(self)
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.thread_id = thread_id

    def run(self):
        global terms
        global file_list

        while file_list:
            list_lock.acquire()
            f_input = file_list.pop()
            list_lock.release()
            if __debug__:
                # Only provide prints when in debug mode or performance will be poor!
                print("Thread " + str(self.thread_id) + " processing: " + f_input)
            process_file(f_input, self.input_folder, self.output_folder)


def main():
    global file_list

    parser = argparse.ArgumentParser(description="Batch document redactor " + VERSION_STRING)
    parser.add_argument('terms_list', default="terms.txt", help='Terms list path', type=str, nargs='?')
    parser.add_argument('input_folder', default="corpus/", help='Input text folder', type=str, nargs='?')
    parser.add_argument('output_folder', default="output/", help='Output text folder', type=str, nargs='?')
    parser.add_argument('--n', help="Number of threads (default 1)", nargs='?', default=1, type=int)
    args = parser.parse_args()

    # List of files to process
    file_list = [f for f in listdir(args.input_folder) if isfile(join(args.input_folder, f))]
    file_list.sort()

    print("Batch document redactor " + VERSION_STRING)
    load_terms(args.terms_list)
    print("Terms list loaded, starting redaction...")

    if __debug__:
        a = time.time() # Timing facilities

    thread_pool = []
    for i in range(args.n):
        print("Starting thread " + str(i))
        new_thread = FileProcessor(i, args.input_folder, args.output_folder)
        thread_pool.append(new_thread)      # Add thread to pool
        new_thread.start()                  # Start the thread

    # Wait for all the threads to finish
    for t in thread_pool:
        t.join()

    if __debug__:
        b = time.time()
        c = b - a
        print("Time elapsed: {:8.2f}s".format(c))

    print("Redaction complete!")


if __name__ == "__main__":
    main()
