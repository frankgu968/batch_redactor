#!/usr/bin/env python3

import argparse
from os import listdir
from os.path import join, isfile

VERSION_STRING = "v0.1b"

terms = dict()      # Dictionary of terms
input_folder = ""   # Globally visible input folder


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


def process_file(f_input, f_output):
    """
    Redaction processing for a single file

    :param f_input:     Input file name
    :param f_output:    Output folder path
    :return:            true - success; false - failure
    """
    global input_folder
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch document redactor " + VERSION_STRING)
    parser.add_argument('terms_list', default="terms.txt", help='Terms list path', type=str, nargs='?')
    parser.add_argument('input_folder', default="corpus/", help='Input text folder', type=str, nargs='?')
    parser.add_argument('output_folder', default="output/", help='Output text folder', type=str, nargs='?')
    args = parser.parse_args()

    input_folder = args.input_folder
    file_list = [f for f in listdir(input_folder) if isfile(join(input_folder, f))]

    print("Batch document redeactor " + VERSION_STRING)
    load_terms(args.terms_list)
    print("Terms list loaded, starting redaction...")

    file_list.sort()

    for item in file_list:
        process_file(item, args.output_folder)
        print("Processing: " + item)
    print("Redaction complete!")
