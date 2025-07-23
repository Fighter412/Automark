from parser import *
import json, constants

def analyse_mark_scheme(exam, count):
    path = "{0}/{1}/Mark scheme".format(constants.ASSETS_PATH, exam)
    for i in range(1, count+1):
        # Read the lines from the file
        file_name = "{0}/{1}.txt".format(path, i)
        file = open(file_name, "r")
        line = file.readlines()[0]
        file.close()
        print(line)
        if i == 1:
            response = json.loads(line)
        else:
            response["Blocks"].extend(json.loads(line)["Blocks"])

    # use functions from Srce Cde
    word_map = map_word_id(response)
    table = extract_table_info(response, word_map)

    # Merge tables     
    questions = []
    for item in table:
        if len(table[item][0]) == 6:
            if table[item][0] == [' ', 'Question', ' ', 'Answer', 'Mark', 'Guidance']:
                questions.extend(table[item][1:])
            else:
                questions.extend(table[item])
    #for row in questions:
    #    print(row)  


    curr_question = '1'
    curr_part = None
    curr_subpart = None
    next_part = None
    next_subpart = None
    questions_dict = {}
    curr_question_dict = {}
    curr_part_dict = {}
    answer = ''
    mark = ''
    guidance = ''


    for i in range(len(questions)):
        curr_row = questions[i]
        answer += curr_row[3]
        mark += curr_row[4]
        guidance += curr_row[5]
        if curr_row[0][0] != ' ': 
            curr_question = curr_row[0][0]
        if curr_row[1] != ' ':
            curr_part = curr_row[1]
        if curr_row[2] != ' ':
            curr_subpart = curr_row[2]
        if i < len(questions) - 1:
            next_row = questions[i+1]
            next_question = curr_question
            if next_row[0][0] != ' ': 
                next_question = next_row[0][0]
            next_part = curr_part
            if next_row[1] != ' ':
                next_part = next_row[1]
            if next_part != curr_part:
                next_subpart = None
            else:
                next_subpart = curr_subpart
                if next_row[2] != ' ':
                    next_subpart = next_row[2]
            next_qdif = not curr_question == next_question
            if next_qdif:
                if curr_part is not None:
                    next_part = "different"
                if curr_subpart is not None:
                    next_subpart = "different"
        else:
            if curr_part is not None:
                next_part = "different"
            if curr_subpart is not None:
                next_subpart = "different"
            next_qdif = True
        if curr_subpart is not None:
            curr_part_dict.update({curr_subpart: {"Answer": answer, "Mark": mark, "Guidance": guidance}})
            answer = ''
            mark = ''
            guidance = ''
        if curr_part != next_part:
            if curr_part_dict == {}: 
                curr_question_dict.update({curr_part: {"Answer": answer, "Mark": mark, "Guidance": guidance}})
            else:
                curr_question_dict.update({curr_part: curr_part_dict})
            curr_part_dict = {}
            answer = ''
            mark = ''
            guidance = ''
            curr_subpart = None
        if next_qdif:
            if curr_question_dict == {}:
                questions_dict.update({curr_question: {"Answer": answer, "Mark": mark, "Guidance": guidance}})
            else:
                questions_dict.update({curr_question: curr_question_dict})
            curr_question_dict = {}
            curr_part_dict = {}
            answer = ''
            mark = ''
            guidance = ''
            curr_part = None
            curr_subpart = None
            curr_question = "different"
    return(questions_dict)
    #file = open(r"Python\Marking\output.json", "w")
    #file.write(json.dumps(questions_dict))
    #file.close()
    #print(json.dumps(questions_dict))

