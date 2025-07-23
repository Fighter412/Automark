from parser import *
import json, constants

def get_text(exam, student, count):

    path = "{0}/{1}/{2}".format(constants.ASSETS_PATH, exam, student)
    for i in range(1, count+1):
        # Read the lines from the file
        file_name = "{0}/{1}.txt".format(path, i)
        file = open(file_name, "r")
        line = file.readlines()[0]
        file.close()
        if i == 1:
            response = json.loads(line)
        else:
            response["Blocks"].extend(json.loads(line)["Blocks"])


    # use functions from Srce Cde
    word_map = map_word_id(response)
    word_map_x_texttype = map_word_id_x_texttype(response)
    raw_text = extract_text(response, extract_by="LINE")
    raw_text_x_handwriting = extract_text_x_handwriting(response, word_map_x_texttype)
    table = extract_table_info(response, word_map)
    key_map = get_key_map(response, word_map)
    value_map = get_value_map(response, word_map)
    final_map = get_kv_map(key_map, value_map)
    return(raw_text_x_handwriting)

check_question = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]
check_part = ["(a)", "(b)", "(c)", "(d)", "(e)", "(f)", "(g)", "(h)"]
check_subpart = ["(i)", "(ii)", "(iii)", "(iv)", "(v)", "(vi)", "(vii)", "(viii)", "(ix)", "(x)"]
check_mark = ["[1]", "[2]", "[3]", "[4]", "[5]", "[6]", "[7]", "[8]", "[9]", "[10]", "[11]", "[12]"]

def check_q(item):
    sentence = item[0]
    left = item[2]
    words = sentence.split()
    firstWord = words[0]
    long = False
    if "*" in firstWord:
        firstWord = firstWord.replace("*", "")
        long = True
    if firstWord in check_question and left < constants.threshold_question:
        return(["question", int(firstWord), long])
    elif firstWord in check_part and left < constants.threshold_part:
        return(["part", firstWord, long])
    elif firstWord in check_subpart and left < constants.threshold_subpart:
        return(["subpart", firstWord, long])
    for word in words:
        if firstWord in check_mark:
            return(["mark", word])
    return(False)

def add_answer(item):
    global question, answer, handwriting_flag
    if item[1] >= 20:
        handwriting_flag = True
    if handwriting_flag:
        answer += item[0] + " "
    else:
        question += item[0] +" "
    return()


def get_blocks(exam, student, count):
    global question, answer, handwriting_flag

    text = get_text(exam, student, count)

    questions = []

    curr_question = None
    curr_part = None
    curr_subpart = None
    question = ""
    answer = ""
    handwriting_flag = False
    long = False

    for page in text:
        if page > 1:
            ignore_flag = True
            for item in text[page]:
                if ignore_flag:
                    if 0.5-constants.threshold_top < item[2] < 0.5+constants.threshold_top:
                        ignore = True
                    else:
                        ignore = False
                if (not ignore or not ignore_flag) and item[3] < constants.threshold_bottom:
                    ignore_flag = False
                    output = check_q(item)
                    if output:
                        if output[0] == "question":
                            if question != "":
                                questions.append({"Type": "Additional", "Question_Number": curr_question,
                                                  "Part_Number": None, "Subpart_Number": None, "Question": question})
                            curr_question = output[1]
                            curr_part = None
                            curr_subpart = None
                            question = ""
                            answer = ""
                            handwriting_flag = False
                        elif output[0] == "part":
                            if question != "":
                                questions.append({"Type": "Additional", "Question_Number": curr_question,
                                                  "Part_Number": curr_part, "Subpart_Number": None, "Question": question})
                            curr_part = output[1]
                            curr_subpart = None
                            question = ""
                            answer = ""
                            handwriting_flag = False
                        elif output[0] == "subpart":
                            if question != "":
                                questions.append({"Type": "Additional", "Question_Number": curr_question,
                                                  "Part_Number": curr_part, "Subpart_Number": curr_subpart, "Question": question})
                            curr_subpart = output[1]
                            question = ""
                            answer = ""
                            handwriting_flag = False
                        if output[0] != "mark":
                            if len(item[0].split()) > 1:
                                item[0] = " ".join(item[0].split()[1:])
                                long = output[2]
                                add_answer(item)
                        else:
                            item[0] = item[0].replace(output[1], "")
                            if len(item[0].split()) > 0:
                                add_answer(item)
                            questions.append({"Type": "Answer", "Question_Number": curr_question,
                                              "Part_Number": curr_part, "Subpart_Number": curr_subpart,
                                              "Question": question, "Answer": answer, "Long": long})
                            question = ""
                            answer = ""
                            handwriting_flag = False
                    else:
                        add_answer(item)



    return(questions)

