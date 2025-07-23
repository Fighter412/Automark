# constants.py stores all the constants required for AutoMark

# URL's for REST API
INVOKE_URLs = {
    "logInRememberMe":          "https://grlzvnk971.execute-api.eu-west-2.amazonaws.com/stage/resource",
    "signUpSendEmail":          "https://w0uw4mutpg.execute-api.eu-west-2.amazonaws.com/stage/resource",
    "signUpCheckCode":          "https://81xgq5nk1d.execute-api.eu-west-2.amazonaws.com/stage/resource",
    "signUpCreateAccount":      "https://bnsbb6zf86.execute-api.eu-west-2.amazonaws.com/stage/resource",
    "signUpCreateAccountS3":    "https://9bd3adqxxi.execute-api.eu-west-2.amazonaws.com/stage/resource",
    "logInCheckEmail":          "https://tq9s3yiaac.execute-api.eu-west-2.amazonaws.com/stage/resource",
    "getData":                  "https://cnp19h1chc.execute-api.eu-west-2.amazonaws.com/stage/resource",
    "getDataS3":                "https://5ni6b34ldc.execute-api.eu-west-2.amazonaws.com/stage/resource",
    "setData":                  "https://rmwdbbom72.execute-api.eu-west-2.amazonaws.com/stage/resource",
    "setDataS3":                "https://mhl5ehvld5.execute-api.eu-west-2.amazonaws.com/stage/resource",
    "toggleRememberMe":         "https://http2pky29.execute-api.eu-west-2.amazonaws.com/stage/resource",
    "logout":                   "https://4eet0gtfd5.execute-api.eu-west-2.amazonaws.com/stage/resource"
}

# Assets folder
ASSETS_PATH = "C:/Users/seanr/Documents/Programming/Coursework/Python/Version2/assets"

# Password hashing
hash_algorithm = "sha512"
hash_repitition = 1000


# analysis
threshold_top = 0.20
threshold_bottom = 0.90
threshold_question = 0.15
threshold_part = 0.15
threshold_subpart = 0.20

# bedrock
instruction = "You are an exam assessor grading a GCE Computer Science paper. Assign marks to the student based on this information. If the student is incorrect, provide feedback as to how the student can improve (Less than 10 words). Also provide a breakdown of as to how the student received each mark. Provide an output strictly to this json format, without any extra information."
output_format = {"Mark": "type_number", "Feedback": "type_string or null", "Breakdown": "type_object"}
example_output_1 = {"Mark": 1, "Feedback": None, "Breakdown": {"1": "Realtime operating system"}}
example_output_2 = {"Mark": 2, "Feedback": "Purpose of utility software missing", "Breakdown": {"1": "Example: Disk defragmenter", "2": "Data compression software"}}

# Accessibility/ Customisation
fonts = ["Arial", "Calibri", "Cascadia Mono", "Comic Sans MS", "Courier New", "Georgia", "Times New Roman", "Verdana"]
themes = {
    "Quiet Light (Tritanomaly)":
    ["#F5F5F5", "#6D705B", "#333333", "#777777", "#9C5D27", "#AA3731", "#4B69C6"],
    "Light + (Tritanomaly)" :
    ["#FFFFFF", "#237893", "#000000", "#795E26", "#0000FF", "#001080", "#AF00DB"],
    "Solarized Light (Protanomaly)":
    ["#FDF6E3", "#237893", "#333333", "#AAB2AC", "#268BD2", "#859900", "#B58900"],
    "Dark + (Protanomaly/ Deuteranomaly)":
    ["#1E1E1E", "#858585", "#D4D4D4", "#DCDCAA", "#9CDCFE", "#C586C0", "#569CD6"],
    "Monokai (Tritanomaly)":
    ["#272822", "#F8F8F2", "#A6E22E", "#66D9EF", "#FD971F", "#F92672", "#AE81FF"],
    "Solarized Dark (Protanomaly)":
    ["#002B36", "#858585", "#BBBBBB", "#268BD2", "#4A666C", "#859900", "#B58900"],
    "Red (Tritanomaly)":
    ["#390000", "#A23F3F", "#F8F8F8", "#FEC758", "#FB9A4B", "#F12727", "#994646"],
    "Black & White (Monochromacy)":
    ["#000000", "#444444", "#666666", "#AAAAAA", "#BBBBBB", "#DDDDDD", "#FFFFFF"]
}

