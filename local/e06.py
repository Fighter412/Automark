import boto3
import json
import constants




def get_info(question_number, part_number = None, subpart_number = None):
    try:
        if part_number is not None:
            question = ""
            if "Question" in qp_dict[question_number]:
                question += qp_dict[question_number]["Question"]
            if subpart_number is not None:
                if "Question" in qp_dict[question_number][part_number]:
                    question += qp_dict[question_number][part_number]["Question"]
                question += qp_dict[question_number][part_number][subpart_number]["Question"]
                answer =  qp_dict[question_number][part_number][subpart_number]["Answer"]
                long = qp_dict[question_number][part_number][subpart_number]["Long"]
            else:
                question += qp_dict[question_number][part_number]["Question"]
                answer = qp_dict[question_number][part_number]["Answer"]
                long = qp_dict[question_number][part_number]["Long"]
        else:
            question = qp_dict[question_number]["Question"]
            answer = qp_dict[question_number]["Answer"]
            long = qp_dict[question_number]["Long"]
        return(question, answer, long)
    except KeyError:
        return(None, None, None)

def get_response(data):
    prompt = {"Instruction": constants.instruction,
              "Data": data,
              "Output format": constants.output_format,
              "Example output 1": constants.example_output_1,
              "Example output 2": constants.example_output_2}
    #print(prompt)
    prompt_s = json.dumps(prompt)
    payload = {"max_tokens": 8192, "top_p": 1, "stop": [], "temperature": 0.7, "top_k": 1, "prompt": prompt_s}
    payload_s = json.dumps(payload)

    response = bedrock_runtime.invoke_model(body=payload_s, modelId=bedrock_model_id,
                                            accept="application/json", contentType="application/json")
    #print("\n", "Response", response)
    response_body = json.loads(response.get("body").read())
    #print("\n", "Response_body", response_body)
    response_text = response_body["outputs"][0]["text"]
    #print("\n", "Response_text", response_text.strip())
    return(response_text.strip())


def mark_exam(qp_data, ms_dict):

    global bedrock_runtime, bedrock_model_id, qp_dict
    qp_dict = qp_data

    bedrock_runtime = boto3.client("bedrock-runtime", region_name="eu-west-2")
    bedrock_model_id = "mistral.mistral-large-2402-v1:0"

    outputAI = {}
    count=0
    for question_number in ms_dict:
        print(question_number)
        if "Answer" in ms_dict[question_number]:
            question_text, student_answer, long = get_info(question_number)
            if question_text is not None and student_answer is not None and long is not None:
                #print(long)
                model_answer = ms_dict[question_number]["Answer"]
                maximum_mark = ms_dict[question_number]["Mark"]
                guidance = ms_dict[question_number]["Guidance"]
                data = {"Question text": question_text,
                        "Model answer": model_answer,
                        "Maximum mark": maximum_mark,
                        "Guidance": guidance,
                        "Student answer": student_answer}
                response = get_response(data)
                print(data, "\n", "AI output: ", response, "\n\n")
                outputAI[question_number] = response
                count+=1
        else:
            for part_number in ms_dict[question_number]:
                print("  " + part_number)
                if "Answer" in ms_dict[question_number][part_number]:
                    question_text, student_answer, long = get_info(question_number, part_number)
                    if question_text is not None and student_answer is not None and long is not None:
                        #print(long)
                        model_answer = ms_dict[question_number][part_number]["Answer"]
                        maximum_mark = ms_dict[question_number][part_number]["Mark"]
                        guidance = ms_dict[question_number][part_number]["Guidance"]
                        data = {"Question text": question_text,
                                "Model answer": model_answer,
                                "Maximum mark": maximum_mark,
                                "Guidance": guidance,
                                "Student answer": student_answer}
                        response = get_response(data)
                        print(data, "\n", "AI output: ", response, "\n\n")
                        if question_number not in outputAI: outputAI[question_number] = {}
                        outputAI[question_number][part_number] = response
                        count+=1
                else:
                    for subpart_number in ms_dict[question_number][part_number]:
                        print("    " + subpart_number)
                        question_text, student_answer, long = get_info(question_number,
                                                                       part_number, subpart_number)
                        if question_text is not None and student_answer is not None and long is not None:
                            #print(long)
                            model_answer = ms_dict[question_number][part_number][subpart_number]["Answer"]
                            maximum_mark = ms_dict[question_number][part_number][subpart_number]["Mark"]
                            guidance = ms_dict[question_number][part_number][subpart_number]["Guidance"]
                            data = {"Question text": question_text,
                                    "Model answer": model_answer,
                                    "Maximum mark": maximum_mark,
                                    "Guidance": guidance,
                                    "Student answer": student_answer}
                            response = get_response(data)
                            print(data, "\n", "AI output: ", response, "\n\n")
                            if question_number not in outputAI: outputAI[question_number] = {}
                            if part_number not in outputAI: outputAI[question_number][part_number] = {}
                            outputAI[question_number][part_number][subpart_number] = response
                            count+=1
    return(outputAI)

