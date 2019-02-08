#!/usr/bin/env python3

import argparse
from os import listdir
from os.path import join, isfile
import threading
import datetime

VERSION_STRING = "v0.1b"

terms = dict()      # Dictionary of terms
input_folder = ""   # Globally visible input folder
file_list = []
list_lock = threading.Lock()


def load_terms(f_input):
    """
    Load the terms dictionary using term as key and calculate length as value
    Provides a slight performance boost to not recalculate length every time

    :param f_input: Terms file path
    :return: true - success; false - failure
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
    :return:            true - success; false - failure
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


class fileProcessor(threading.Thread):
    def __init__(self, input_folder, output_folder):
        threading.Thread.__init__(self)
        self.input_folder = input_folder
        self.output_folder = output_folder

    def run(self):
        global terms
        global file_list
        while(file_list):
            list_lock.acquire()
            f_input = file_list.pop()
            list_lock.release()
            print(f_input)
            process_file(f_input, self.input_folder, self.output_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch document redactor " + VERSION_STRING)
    parser.add_argument('terms_list', default="terms.txt", help='Terms list path', type=str, nargs='?')
    parser.add_argument('input_folder', default="corpus/", help='Input text folder', type=str, nargs='?')
    parser.add_argument('output_folder', default="output/", help='Output text folder', type=str, nargs='?')
    parser.add_argument('--n', help="Number of threads (default 4)", nargs='?', default=4, type=int)
    args = parser.parse_args()

    file_list = [f for f in listdir(args.input_folder) if isfile(join(args.input_folder, f))]

    print("Batch document redeactor " + VERSION_STRING)
    load_terms(args.terms_list)
    print("Terms list loaded, starting redaction...")

    file_list.sort()
    a = datetime.datetime.now()
    threadPool = []
    for i in range(args.n):
        print("Starting thread")
        newThread = fileProcessor(args.input_folder, args.output_folder)
        threadPool.append(newThread)
        newThread.start()

    for t in threadPool:
        t.join()
    b = datetime.datetime.now()
    c = b - a
    print(c.seconds)

    print("Redaction complete!")
