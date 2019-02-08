import os.path

terms = dict()  # Dictionary of terms
input_folder = ""


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
    with open(os.path.join(input_folder, f_input), "r", encoding="utf8") as f:
        string_buffer = f.read().replace('\n', ' \n')       # Preserve newlines
        string_buffer = string_buffer.replace('\t', ' \t')  # Preserve tabs
        token_buffer = string_buffer.split(' ')             # Only split on whitespace
        for token in token_buffer:
            if token.upper() in terms.keys():
                output_token_list.append("<removed " + terms[token.upper()] + ">")
            else:
                output_token_list.append(token)

        result_string = " ".join(output_token_list)
        output_file = open(os.path.join(f_output, f_input), "w", encoding="utf8")
        output_file.write(result_string)


if __name__ == "__main__":
    load_terms("/Users/frank/Desktop/Ensho/terms.txt")
    input_folder = "/Users/frank/Desktop/Ensho/corpus"
    process_file("000000.txt", "/Users/frank/Desktop/Ensho/output")
