import json

def analyse_exam_paper(blocks):

    answers = {}
    for item in blocks:
        Type = item["Type"]
        Question_Number = item["Question_Number"]
        Part_Number = item["Part_Number"]
        Subpart_Number = item["Subpart_Number"]
        Question = item["Question"]
        if Type == "Answer":
            Answer = item["Answer"]
            Long = item["Long"]
            if Question_Number is not None:
                if Part_Number is not None:
                    if Subpart_Number is not None:
                        if Question_Number not in answers:
                            answers[Question_Number] = {}
                        if Part_Number not in answers[Question_Number]:
                            answers[Question_Number][Part_Number] = {}
                        answers[Question_Number][Part_Number][Subpart_Number] = {"Question": Question,
                                                                            "Answer": Answer, "Long": Long}
                    else:
                        if Question_Number not in answers:
                            answers[Question_Number] = {}
                        answers[Question_Number][Part_Number] = {"Question": Question,
                                                                 "Answer": Answer, "Long": Long}
                else:
                    answers[Question_Number] = {"Question": Question, "Answer": Answer, "Long": Long}
        else:   # Type == "Additional"
            if Question_Number is not None:
                if Part_Number is not None:
                    if Subpart_Number is not None:
                        if Question_Number not in answers:
                            answers[Question_Number] = {}
                        if Part_Number not in answers[Question_Number]:
                            answers[Question_Number][Part_Number] = {}
                        if Subpart_Number not in answers[Question_Number][Part_Number]:
                            answers[Question_Number][Part_Number][Subpart_Number] = {"Question": Question}
                        else:
                            answers[Question_Number][Part_Number][Subpart_Number]["Question"] += Question
                    else:
                        if Question_Number not in answers:
                            answers[Question_Number] = {}
                        if Part_Number not in answers[Question_Number]:
                            answers[Question_Number][Part_Number] = {"Question": Question}
                        else:
                            answers[Question_Number][Part_Number]["Question"] += Question
                else:
                    if Question_Number not in answers:
                        answers[Question_Number] = {"Question": Question}
                    else:
                        answers[Question_Number]["Question"] += Question

    return(answers)
    # file = open(r"Python\Marking\output4append.json", "w")
    # file.write(json.dumps(answers))
    # #file.write(json.dumps(text))
    # file.close()

