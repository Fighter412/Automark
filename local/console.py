import tkinter, tkinter.ttk, tkinter.messagebox, requests, json, tkinter.font, tkinter.filedialog, os, pyttsx3
import constants, marking, boto3, boto3extensions


class console():

    def __init__(self, MAC_ADDRESS):
        self.MAC_ADDRESS = MAC_ADDRESS


        # Other variables
        self.expand = False

        self.currentFrame = False

        # Extract locally stored email
        file_email = open(constants.ASSETS_PATH+"/email.txt", "r")
        self.emailAddress = file_email.readline()
        file_email.close()

        # Obtain stored data from server
        response = requests.get(url=constants.INVOKE_URLs["getDataS3"],
                                 params={"email": self.emailAddress,
                                         "MAC_ADDRESS": self.MAC_ADDRESS})
        statusCode = response.status_code
        if statusCode != 200:
            tkinter.messagebox.showerror(title="Data retrieval", message="Something went wrong with retrieving data. (status code)")
            print(statusCode)
            self.function_logout()
        elif json.loads(response.text)["success"] != True:
            tkinter.messagebox.showerror(title="Data retrieval", message="Something went wrong with retrieving data. (success)")
            self.function_logout()
        self.bucket = json.loads(response.text)["bucket"]
        s3 = boto3.client("s3")
        s3.download_file(self.bucket, "data.txt", "{0}/data.txt".format(constants.ASSETS_PATH))
        f = open("{0}/data.txt".format(constants.ASSETS_PATH), "r")
        data_text = f.readline()
        f.close()
        self.data = json.loads(data_text)

        if "Classes" in self.data:
            self.classes = self.data["Classes"]
        else:
            self.classes ={}
        if "Exams" in self.data:
            self.exams = self.data["Exams"]
        else:
            self.exams = {}
        if "Student-Exam" in self.data:
            self.student_exam = self.data["Student-Exam"]
        else:
            self.student_exam = {}
        if "font" in self.data:
            self.userFont = self.data["font"]
        else:
            self.userFont = "Cascadia Mono"
        if "theme" in self.data:
            self.userTheme = self.data["theme"]
        else:
            self.userTheme = "Quiet Light (Tritanomaly)"
        if "tts" in self.data:
            self.tts = self.data["tts"]
        else:
            self.tts = False

        # Check if user has set up remember me (For user tab)
        response = requests.get(url=constants.INVOKE_URLs["logInRememberMe"],
                                 params={"email": self.emailAddress,
                                         "MAC_ADDRESS": self.MAC_ADDRESS})
        statusCode = response.status_code
        if statusCode != 200:
            tkinter.messagebox.showerror(title="Remember me check", message="Something went wrong with checking remember me status.")
        self.rememberMe = json.loads(response.text)["success"]


        # Main window
        self.window = tkinter.Tk()
        self.window.geometry("1200x800+360+124")
        self.window.resizable(False, False)
        self.window.configure(bg=constants.themes[self.userTheme][0])

        # Two main frames
        self.frameData = tkinter.Frame(self.window)
        self.frameData.config(width=1100, height=800)
        self.frameData.place(x=100,y=0)

        self.frameMenu = tkinter.Frame(self.window)
        self.frameMenu.config(bg=constants.themes[self.userTheme][1], width=300, height=800)
        self.frameMenu.place(x=0,y=0)
        self.frameMenu.lower()
        
        # Elements for Menu frame (which will not be changed)
        self.menuItems = [0, 0, 0, 0, 0, 0, 0]
        self.menuItems[0] = tkinter.Button(self.frameMenu, width=13, height=5, text="Exams",
                                           bg=constants.themes[self.userTheme][6], fg=constants.themes[self.userTheme][2], command=self.exams_tab)
        self.menuItems[0].grid(row = 0, column = 0)
        self.menuItems[0].bind("<Enter>", func=lambda e: self.sayText("Exams tab"))
        self.menuItems[1] = tkinter.Button(self.frameMenu, width=26, height=5, text="Exams",
                                           bg=constants.themes[self.userTheme][6], fg=constants.themes[self.userTheme][2], command=self.exams_tab)
        self.menuItems[1].grid(row = 0, column = 1)
        self.menuItems[1].bind("<Enter>", func=lambda e: self.sayText("Exams tab"))
        self.menuItems[2] = tkinter.Button(self.frameMenu, width=13, height=5, text="Classes",
                                           bg=constants.themes[self.userTheme][6], fg=constants.themes[self.userTheme][2], command=self.classes_tab)
        self.menuItems[2].grid(row = 2, column = 0)
        self.menuItems[2].bind("<Enter>", func=lambda e: self.sayText("Classes tab"))
        self.menuItems[3] = tkinter.Button(self.frameMenu, width=26, height=5, text="Classes",
                                           bg=constants.themes[self.userTheme][6], fg=constants.themes[self.userTheme][2], command=self.classes_tab)
        self.menuItems[3].grid(row = 2, column = 1)
        self.menuItems[3].bind("<Enter>", func=lambda e: self.sayText("Classes tab"))
        self.menuItems[4] = tkinter.Button(self.frameMenu, width=13, height=5, text="User",
                                           bg=constants.themes[self.userTheme][6], fg=constants.themes[self.userTheme][2], command=self.user_tab)
        self.menuItems[4].grid(row = 4, column = 0)
        self.menuItems[4].bind("<Enter>", func=lambda e: self.sayText("User tab"))
        self.menuItems[5] = tkinter.Button(self.frameMenu, width=26, height=5, text="User",
                                           bg=constants.themes[self.userTheme][6], fg=constants.themes[self.userTheme][2], command=self.user_tab)
        self.menuItems[5].grid(row = 4, column = 1)
        self.menuItems[5].bind("<Enter>", func=lambda e: self.sayText("User tab"))
        self.menuItems[6] = tkinter.Label(self.frameMenu, height=35, bg=constants.themes[self.userTheme][1])
        self.menuItems[6].grid(row=5, column=0)

        # Set default font
        tkinter.font.nametofont("TkDefaultFont").configure(family=self.userFont, size=9)

        # Motion tracking and close button
        self.window.bind('<Motion>', self.motion)
        self.window.protocol("WM_DELETE_WINDOW", self.function_logout)
        
        # pyttsx3 engine
        self.engine = pyttsx3.init()

        # Load exam tab on startup
        self.exams_tab()

    def motion(self, event):
        x, y = self.window.winfo_pointerxy()
        x -= self.window.winfo_x()
        y -= self.window.winfo_y()

        #print(x)
        if self.expand:
            if x > 300:
                self.expand = False
                self.frameMenu.lower()
        if x < 100:
            self.expand = True
            self.frameMenu.lift()
    
    def exams_tab(self):
        #print(self.exams)
        # Removes the previous frame if it has a value to prevent execution
        # when first running as self.currentFrame was set to False
        if self.currentFrame:
            self.currentFrame.destroy()
        # Creates the new frame and sets the currentFrame to the frame onscreen
        self.frameExams = tkinter.Frame(self.frameData)
        self.currentFrame = self.frameExams
        # Renames the title of the window and packs the frame in the window
        self.window.title("Exams")
        self.frameExams.pack()
        # Set window theme
        self.frameExams.configure(bg=constants.themes[self.userTheme][0])
        # Create frame elements
        height = len(self.exams)+1
        i = tkinter.PhotoImage(width=1, height=1)
        tkinter.Label(self.frameExams, text = "Classes", width=300, image=i, compound='c', bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = 0, column = 0)
        tkinter.ttk.Separator(self.frameExams, orient='vertical').grid(row = 0, column = 1, rowspan=height, sticky="ns")
        tkinter.Label(self.frameExams, text = "Exam", width=500, image=i, compound='c', bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = 0, column = 2)
        tkinter.ttk.Separator(self.frameExams, orient='vertical').grid(row = 0, column = 3, rowspan=height, sticky="ns")
        tkinter.Label(self.frameExams, text = "Date", width=100, image=i, compound='c', bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = 0, column = 4)
        tkinter.ttk.Separator(self.frameExams, orient='vertical').grid(row = 0, column = 5, rowspan=height, sticky="ns")
        tkinter.Label(self.frameExams, text = "Select", width=100, image=i, compound='c', bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = 0, column = 6)
        j = 0
        for i in self.exams:
            tkinter.Label(self.frameExams, text = self.exams[i]["Classes"], bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = j+1, column = 0)
            tkinter.Label(self.frameExams, text = i, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = j+1, column = 2)
            tkinter.Label(self.frameExams, text = self.exams[i]["Date"], bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = j+1, column = 4)
            tkinter.Button(self.frameExams, text = "Select", command=lambda i=i:self.frame_openExam(i), bg=constants.themes[self.userTheme][0],
                           fg=constants.themes[self.userTheme][5]).grid(row = j+1, column = 6)
            j += 1
        tkinter.Button(self.frameExams, text = "Add exam", command=self.window_addExam, bg=constants.themes[self.userTheme][0],
                       fg=constants.themes[self.userTheme][5]).grid(row = len(self.exams)+1, column = 0, columnspan=7) 
        tkinter.Label(self.frameExams, height=50, bg=constants.themes[self.userTheme][0]).grid(row=len(self.exams)+2, column = 0, columnspan=7)
        self.frameExams.mainloop()
    
    def window_addExam(self):
        # If user does not have any classes, an exam cannot be created
        if len(self.classes) == 0:
            tkinter.messagebox.showwarning(title="No classes found", message="Exams cannot be created without classes")
            return
        # Create a new frame
        self.exam_window = tkinter.Tk()
        self.exam_window.geometry("800x400+560+340")
        self.exam_window.resizable(False, False)
        tkinter.font.nametofont("TkDefaultFont").configure(family=self.userFont, size=9)
        self.exam_window.title("Add Exam")
        # Set window theme
        self.exam_window.configure(bg=constants.themes[self.userTheme][0])
        # Create frame elements
        tkinter.Label(master=self.exam_window, text="Classes", bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row=0, column=0)
        self.classes_listBox = tkinter.Listbox(self.exam_window, selectmode=tkinter.MULTIPLE, width=20, height=5, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5])
        self.classes_listBox.grid(row=1, column=0, rowspan=4)
        self.classes_options = []
        i = 0
        for item in self.classes:
            self.classes_listBox.insert(i, item)
            self.classes_options.append(item)
            i += 1
        tkinter.Label(master=self.exam_window, text="Exam description", bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row=0, column=1, rowspan=2)
        self.exam_description = tkinter.StringVar(master=self.exam_window)
        tkinter.Entry(master=self.exam_window, textvariable=self.exam_description, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row=0, column=2, rowspan=2)
        tkinter.Label(master=self.exam_window, text="Date", bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row=2, column=1)
        self.exam_date = tkinter.StringVar(master=self.exam_window)
        tkinter.Entry(master=self.exam_window, textvariable=self.exam_date, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row=2, column=2)
        tkinter.Button(master=self.exam_window, text="Finish", command=self.function_addExam, bg=constants.themes[self.userTheme][0],
                       fg=constants.themes[self.userTheme][5]).grid(row=3, column=1, columnspan=2)
        tkinter.Button(master=self.exam_window, text = "Cancel", command=self.exam_window.destroy, bg=constants.themes[self.userTheme][0],
                       fg=constants.themes[self.userTheme][5]).grid(row=4, column=1, columnspan=2)
        self.exam_window.mainloop()

    def function_addExam(self):
        selected_values = []
        selection = self.classes_listBox.curselection()
        for i in selection:
            selected_values.append(self.classes_options[i])
        self.exams.update({self.exam_description.get(): {"Classes": selected_values,
                             "Date": self.exam_date.get(),
                             "Mark scheme": {},
                             "Exam papers": {}}})
        print(self.exams)
        self.setData()
        self.exam_window.destroy()
        self.exams_tab()

    def frame_openExam(self, exam):
        # Get data
        self.exam_class = self.exams[exam]["Classes"]
        self.exam_name = exam
        self.exam_date = self.exams[exam]["Date"]
        # Removes the previous frame
        self.currentFrame.destroy()
        # Creates the new frame and sets the currentFrame to the frame onscreen
        self.frameExam = tkinter.Frame(self.frameData)
        self.currentFrame = self.frameExam
        # Renames the title of the window and packs the frame in the window
        self.window.title(self.exam_name)
        self.frameExam.pack()
        # Set window theme
        self.frameExam.configure(bg=constants.themes[self.userTheme][0])
        # Create frame elements
        tkinter.Label(self.frameExam, text = "Classes: ", bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = 0, column = 0)
        tkinter.Label(self.frameExam, text = self.exam_class, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = 0, column = 1)
        tkinter.Label(self.frameExam, text = "Name: ", bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = 1, column = 0)
        tkinter.Label(self.frameExam, text = self.exam_name, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = 1, column = 1)
        tkinter.Label(self.frameExam, text = "Date: ", bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = 2, column = 0)
        tkinter.Label(self.frameExam, text = self.exam_date, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = 2, column = 1)
        tkinter.Label(self.frameExam, text = "Select mark scheme: ", bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = 3, column = 0)
        tkinter.Button(self.frameExam, text = "Add .pdf", command=self.openMarkScheme, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = 3, column = 1)
        tkinter.Label(self.frameExam, text = "Select exam paper: ", bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = 4, column = 0)
        tkinter.Button(self.frameExam, text = "Add .pdf", command=self.openExamPaper, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = 4, column = 1)
        tkinter.Label(self.frameExam, text="Selected file: ", bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = 5, column = 0)
        self.selectedFileLbl = tkinter.Label(master=self.frameExam, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5])
        self.selectedFileLbl.grid(row=5, column=1)
        self.uploadBtn = tkinter.Button(master=self.frameExam, text="Continue", command=self.upload, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5])
        self.uploadBtn.grid(row=5, column=2, columnspan=2)
        self.uploadBtn["state"] = "disabled"
        tkinter.Label(self.frameExam, text="Mark scheme and exam papers", bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row=6, column=0)
        if self.exams[self.exam_name]["Mark scheme"] != {}:
            tkinter.Label(self.frameExam, text = "Mark scheme", bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = 7, column = 0)
            tkinter.Label(self.frameExam, text = "Status: "+self.exams[self.exam_name]["Mark scheme"]["status"], bg=constants.themes[self.userTheme][0],
                          fg=constants.themes[self.userTheme][5]).grid(row = 7, column = 1)
            self.row_select_markscheme_btn = tkinter.Button(self.frameExam,
                                                            text=["Textract", "Analyse", "View"][["Uploaded", "Textracted", "Analysed"].index(self.exams[self.exam_name]["Mark scheme"]["status"])],
                                                            command=self.selectMarkScheme, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5])
            self.row_select_markscheme_btn.grid(row=7, column=2)
        j = 8
        for i in self.exams[self.exam_name]["Exam papers"]:
            tkinter.Label(self.frameExam, text = i, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = j, column = 0)
            tkinter.Label(self.frameExam, text = "Status: "+self.exams[self.exam_name]["Exam papers"][i]["status"], bg=constants.themes[self.userTheme][0],
            fg=constants.themes[self.userTheme][5]).grid(row = j, column = 1)
            tkinter.Button(self.frameExam, 
                    text = ["Textract", "Analyse", "Mark", "View"][["Uploaded", "Textracted", "Analysed", "Marked"].index(self.exams[self.exam_name]["Exam papers"][i]["status"])],
                               command=lambda i=i:self.selectExamPaper(i), bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row = j, column = 2)
            j += 1
        tkinter.Button(self.frameExam, text = "Delete exam", command=self.deleteExam, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row=j, column = 2)
        tkinter.Label(self.frameExam, height=50, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row=j+1, column = 2)
        self.frameExam.mainloop()

    def openMarkScheme(self):
        print("Select Mark scheme for ", self.exam_name)
        self.filename = tkinter.filedialog.askopenfilename(initialdir = r"C:\Users\seanr\Documents\Programming\Coursework\Python\Version2\assets",
										title = "Select Mark Scheme",
										filetypes=[('PDF file', '*.pdf')])
        if self.filename != "":
            self.selectedFileLbl["text"] = self.filename
            self.uploadType = "MS"
            self.uploadBtn["state"] = "normal"
        else:
            self.uploadBtn["state"] = "disabled"
        print(self.filename)

    def openExamPaper(self):
        print("Select Exam paper for ", self.exam_name)
        self.filename = tkinter.filedialog.askopenfilename(initialdir = r"C:\Users\seanr\Documents\Programming\Coursework\Python\Version2\assets",
										title = "Select Exam paper",
										filetypes=[('PDF file', '*.pdf')])
        if self.filename != "":
            self.selectedFileLbl["text"] = self.filename
            self.uploadType = "QP"
            self.uploadBtn["state"] = "normal"
        else:
            self.uploadBtn["state"] = "disabled"
        print(self.filename)

    def upload(self):
        if self.uploadType == "MS":
            save_as = self.exam_name + "/Mark Scheme.pdf"
        else:
            student_id = os.path.basename(self.filename)[:-4]
            save_as = self.exam_name + "/Exam Papers/" + student_id + ".pdf"
        success = boto3extensions.upload_file(self.bucket, self.filename, save_as)
        if not success:
            tkinter.messagebox.showerror(title="Uploading pdf", message="Something went wrong with uploading pdf.")
        else:
            print("File uploaded")
            if self.uploadType == "MS":
                self.exams[self.exam_name]["Mark scheme"]["location"] = save_as
                self.exams[self.exam_name]["Mark scheme"]["status"] = "Uploaded"
            else:
                self.exams[self.exam_name]["Exam papers"][student_id] = {}
                self.exams[self.exam_name]["Exam papers"][student_id]["location"] = save_as
                self.exams[self.exam_name]["Exam papers"][student_id]["status"] = "Uploaded"
            self.uploadBtn["state"] = "disabled"
            self.setData()
        self.frame_openExam(self.exam_name)

    def selectMarkScheme(self):
        if self.exams[self.exam_name]["Mark scheme"]["status"] == "Uploaded":
            answer = tkinter.messagebox.askyesno(title="Mark scheme", message="This mark scheme paper has been uploaded, would you like to textract?")
            if answer:  # answer is boolean
                self.window.config(cursor="watch")
                self.window.update()
                response = marking.textract_ms(self.bucket, self.exam_name)
                self.window.config(cursor="")
                self.exams[self.exam_name]["Mark scheme"]["status"] = "Textracted"
                self.exams[self.exam_name]["Mark scheme"]["JobId"] = response
                self.setData()
                self.frame_openExam(self.exam_name)
        elif self.exams[self.exam_name]["Mark scheme"]["status"] == "Textracted":
            answer = tkinter.messagebox.askyesno(title="Mark scheme", message="This mark schme paper has been textracted, would you like to analyse?")
            if answer:  # answer is boolean
                self.window.config(cursor="watch")
                self.window.update()
                JobId = self.exams[self.exam_name]["Mark scheme"]["JobId"]
                response = marking.analyse_ms(self.bucket, self.exam_name, JobId)
                self.window.config(cursor="")
                self.exams[self.exam_name]["Mark scheme"]["status"] = "Analysed"
                self.exams[self.exam_name]["Mark scheme"]["Data"] = response
                self.setData()
                self.frame_openExam(self.exam_name)
        elif self.exams[self.exam_name]["Mark scheme"]["status"] == "Analysed":
            tkinter.messagebox.showinfo(title="View mark scheme", message="You have clicked to open the analysed mark scheme")

    def selectExamPaper(self, student):
        if self.exams[self.exam_name]["Exam papers"][student]["status"] == "Uploaded":
            answer = tkinter.messagebox.askyesno(title=student, message="This student paper has been uploaded, would you like to textract?")
            if answer:  # answer is boolean
                self.window.config(cursor="watch")
                self.window.update()
                response = marking.textract_qp(self.bucket, self.exam_name, student)
                self.window.config(cursor="")
                self.exams[self.exam_name]["Exam papers"][student]["status"] = "Textracted"
                self.exams[self.exam_name]["Exam papers"][student]["JobId"] = response
                self.setData()
                self.frame_openExam(self.exam_name)
        elif self.exams[self.exam_name]["Exam papers"][student]["status"] == "Textracted":
            answer = tkinter.messagebox.askyesno(title=student, message="This student paper has been textracted, would you like to analyse?")
            if answer:  # answer is boolean
                self.window.config(cursor="watch")
                self.window.update()
                JobId = self.exams[self.exam_name]["Exam papers"][student]["JobId"]
                response = marking.analyse_qp(self.bucket, self.exam_name, student, JobId)
                self.window.config(cursor="")
                self.exams[self.exam_name]["Exam papers"][student]["status"] = "Analysed"
                self.exams[self.exam_name]["Exam papers"][student]["Data"] = response
                self.setData()
                self.frame_openExam(self.exam_name)
        elif self.exams[self.exam_name]["Exam papers"][student]["status"] == "Analysed":
            if self.exams[self.exam_name]["Mark scheme"]["status"] != "Analysed":
                tkinter.messagebox.showerror(title="Marking "+student, message=student+" cannot be marked as the mark scheme is not analysed!")
            else:
                answer = tkinter.messagebox.askyesno(title=student, message="This student paper has been Analysedd, would you like to mark?")
                if answer:  # answer is boolean
                    qp_data = self.exams[self.exam_name]["Exam papers"][student]["Data"]
                    ms_data = self.exams[self.exam_name]["Mark scheme"]["Data"]
                    self.window.config(cursor="watch")
                    self.window.update()
                    response = marking.mark_qp(qp_data, ms_data)
                    self.window.config(cursor="")
                    self.exams[self.exam_name]["Exam papers"][student]["status"] = "Marked"
                    self.exams[self.exam_name]["Exam papers"][student]["Data_marked"] = response
                    self.setData()
                    self.frame_openExam(self.exam_name)
        elif self.exams[self.exam_name]["Exam papers"][student]["status"] == "Marked":
            self.openMarkedPaper(student)
    
    def openMarkedPaper(self, student):
        # Removes the previous frame
        self.currentFrame.destroy()
        # Creates the new frame and sets the currentFrame to the frame onscreen
        self.frameMarked = tkinter.Frame(self.frameData)
        self.currentFrame = self.frameMarked
        # Renames the title of the window and packs the frame in the window
        self.window.title(self.exam_name + student)
        self.frameMarked.pack()
        # Create frame elements
        y=tkinter.ttk.Scrollbar(self.frameMarked, orient='vertical')
        y.pack(side=tkinter.RIGHT, fill='y')
        text = tkinter.Text(self.frameMarked, yscrollcommand=y.set)
        text.insert(tkinter.END, json.dumps(self.exams[self.exam_name]["Exam papers"][student]["Data_marked"], indent=4))
        text.pack()
        self.frameMarked.mainloop()

    def deleteExam(self):
        answer = tkinter.messagebox.askyesno(title="Delete exam", message="Would you like to delete {0}".format(self.exam_name))
        if answer:
            self.exams.pop(self.exam_name)
            self.setData()
            self.exams_tab()
        else:
            self.frame_openExam(self.exam_name)

    def classes_tab(self):
        # Removes the previous frame
        self.currentFrame.destroy()
        # Creates the new frame and sets the currentFrame to the frame onscreen
        self.frameClasses = tkinter.Frame(self.frameData)
        self.currentFrame = self.frameClasses
        # Renames the title of the window and packs the frame in the window
        self.window.title("Classes")
        self.frameClasses.pack()
        # Set window theme
        self.frameClasses.configure(bg=constants.themes[self.userTheme][0])
        # Create frame elements
        height = len(self.classes)+1
        i = tkinter.PhotoImage(width=1, height=1)
        tkinter.Label(self.frameClasses, text = "Class", width=100, image=i, compound='c', bg=constants.themes[self.userTheme][0],
                      fg=constants.themes[self.userTheme][5]).grid(row = 0, column = 0)
        tkinter.ttk.Separator(self.frameClasses, orient='vertical').grid(row = 0, column = 1, rowspan=height, sticky="ns")
        tkinter.Label(self.frameClasses, text = "Class description", width=300, image=i, compound='c', bg=constants.themes[self.userTheme][0],
                      fg=constants.themes[self.userTheme][5]).grid(row = 0, column = 2)
        tkinter.ttk.Separator(self.frameClasses, orient='vertical').grid(row = 0, column = 3, rowspan=height, sticky="ns")
        tkinter.Label(self.frameClasses, text = "Identified students", width=500, image=i, compound='c', bg=constants.themes[self.userTheme][0],
                      fg=constants.themes[self.userTheme][5]).grid(row = 0, column = 4)
        tkinter.ttk.Separator(self.frameClasses, orient='vertical').grid(row = 0, column = 5, rowspan=height, sticky="ns")
        tkinter.Label(self.frameClasses, text = "Select", width=100, image=i, compound='c', bg=constants.themes[self.userTheme][0],
                      fg=constants.themes[self.userTheme][5]).grid(row = 0, column = 6)
        j = 0
        for i in self.classes:
            tkinter.Label(self.frameClasses, text = i, bg=constants.themes[self.userTheme][0],
            fg=constants.themes[self.userTheme][5]).grid(row = j+1, column = 0)
            tkinter.Label(self.frameClasses, text = self.classes[i]["Class description"], bg=constants.themes[self.userTheme][0],
            fg=constants.themes[self.userTheme][5]).grid(row = j+1, column = 2)
            tkinter.Label(self.frameClasses, text = self.classes[i]["Identified students"], bg=constants.themes[self.userTheme][0],
            fg=constants.themes[self.userTheme][5]).grid(row = j+1, column = 4)
            tkinter.Button(self.frameClasses, text = "Button", command=lambda:self.frame_openClass(j), bg=constants.themes[self.userTheme][0],
                           fg=constants.themes[self.userTheme][5]).grid(row = j+1, column = 6)
            j += 1
        tkinter.Button(self.frameClasses, text = "Add class", command=self.window_addClass, bg=constants.themes[self.userTheme][0],
        fg=constants.themes[self.userTheme][5]).grid(row = len(self.classes)+1, column = 0, columnspan=7)
        tkinter.Label(self.frameClasses, height=50, bg=constants.themes[self.userTheme][0]).grid(row=len(self.classes)+2, column = 0, columnspan=7)
        self.frameClasses.mainloop()
    
    def window_addClass(self):
        # Create a new frame
        self.class_window = tkinter.Tk()
        self.class_window.geometry("400x200+360+124")
        self.class_window.resizable(False, False)
        tkinter.font.nametofont("TkDefaultFont").configure(family=self.userFont, size=9)
        self.class_window.title("Add Class")
        # Set window theme
        self.class_window.configure(bg=constants.themes[self.userTheme][0])
        # Create frame elements
        tkinter.Label(master=self.class_window, text="Class name", bg=constants.themes[self.userTheme][0],
        fg=constants.themes[self.userTheme][5]).grid(row=0, column=0)
        self.class_name = tkinter.StringVar(master=self.class_window)
        tkinter.Entry(master=self.class_window, textvariable=self.class_name, bg=constants.themes[self.userTheme][0],
        fg=constants.themes[self.userTheme][5]).grid(row=0, column=1)
        tkinter.Label(master=self.class_window, text="Class description", bg=constants.themes[self.userTheme][0],
        fg=constants.themes[self.userTheme][5]).grid(row=1, column=0)
        self.class_description = tkinter.StringVar(master=self.class_window)
        tkinter.Entry(master=self.class_window, textvariable=self.class_description, bg=constants.themes[self.userTheme][0],
                      fg=constants.themes[self.userTheme][5]).grid(row=1, column=1)
        tkinter.Button(master=self.class_window, text="Finish", command=self.function_addClass, bg=constants.themes[self.userTheme][0],
        fg=constants.themes[self.userTheme][5]).grid(row=2, column=0, columnspan=2)
        tkinter.Button(self.class_window, text = "Cancel", command=self.class_window.destroy, bg=constants.themes[self.userTheme][0],
        fg=constants.themes[self.userTheme][5]).grid(row=3, column = 0, columnspan=2)
        self.class_window.mainloop()
    
    def function_addClass(self):
        self.classes.update({self.class_name.get(): {"Class description": self.class_description.get(),
                             "Identified students": {}}})
        print(self.classes)
        self.setData()
        self.class_window.destroy()
        self.classes_tab()

    def frame_openClass(self, i):
        pass

    def setData(self):
        self.data_s = json.dumps({"Bucket": self.bucket,
                                  "font": self.userFont,
                                  "theme": self.userTheme,
                                  "tts": self.tts,
                                  "Classes": self.classes,
                                  "Exams": self.exams,
                                  "Student-Exam": self.student_exam})
        f = open("{0}/data.txt".format(constants.ASSETS_PATH), "w")
        f.write(self.data_s)
        f.close()
        # Upload data to S3
        success = boto3extensions.upload_file(self.bucket, "{0}/data.txt".format(constants.ASSETS_PATH), "data.txt")
        if not success:
            tkinter.messagebox.showerror(title="Uploading pdf", message="Something went wrong with uploading data.")
        else:
            response = requests.get(url=constants.INVOKE_URLs["setDataS3"],
                                    params={"email": self.emailAddress,
                                            "MAC_ADDRESS": self.MAC_ADDRESS,
                                            "bucket": self.bucket})
            statusCode = response.status_code
            if statusCode != 200:
                tkinter.messagebox.showerror(title="Save data", message="Something went wrong with saving data.")
    
    def user_tab(self):
        # Removes the previous frame
        self.currentFrame.destroy()
        # Creates the new frame and sets the currentFrame to the frame onscreen
        self.frameUser = tkinter.Frame(self.frameData)
        self.currentFrame = self.frameUser
        # Renames the title of the window and packs the frame in the window
        self.window.title("User")
        self.frameUser.pack()
        # Set window theme
        self.frameUser.configure(bg=constants.themes[self.userTheme][0])
        # Create frame elements
        tkinter.Label(master=self.frameUser, text="Email address: "+self.emailAddress, bg=constants.themes[self.userTheme][0],
                      fg=constants.themes[self.userTheme][5]).grid(row=0, column=0, columnspan=2)
        self.rememberMeLbl = tkinter.Label(master=self.frameUser, text="Remember me: "+str(self.rememberMe), bg=constants.themes[self.userTheme][0],
                                           fg=constants.themes[self.userTheme][5])
        self.rememberMeLbl.grid(row=1, column=0)
        self.rememberMeBtn = tkinter.Button(master=self.frameUser, text="Toggle Remember Me", command=self.function_toggleRememberMe, bg=constants.themes[self.userTheme][0],
                                            fg=constants.themes[self.userTheme][5])
        self.rememberMeBtn.grid(row=1, column=1)
        self.rememberMeBtn.bind("<Enter>", func=lambda e: self.sayText("Toggle remember me"))
        self.logoutBtn = tkinter.Button(master=self.frameUser, text="Logout", command=self.function_logout, bg=constants.themes[self.userTheme][0],
                                        fg=constants.themes[self.userTheme][5])
        self.logoutBtn.grid(row=2, column=0, columnspan=2)
        self.logoutBtn.bind("<Enter>", func=lambda e: self.sayText("Log out"))

        # Fonts
        tkinter.Label(master=self.frameUser, text="Font", bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row=3, column=0)
        self.userFontVar = tkinter.StringVar()
        self.fontRBtn = []
        self.fontRBtn.append(tkinter.Radiobutton(self.frameUser, text="Arial", variable=self.userFontVar, value="Arial", command=self.function_changeFont,
                                                 bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]))
        self.fontRBtn[0].grid(row=4, column=0, columnspan=2)
        self.fontRBtn[0].bind("<Enter>", func=lambda e: self.sayText("Arial"))

        self.fontRBtn.append(tkinter.Radiobutton(self.frameUser, text="Calibri", variable=self.userFontVar, value="Calibri", command=self.function_changeFont,
                                                 bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]))
        self.fontRBtn[1].grid(row=5, column=0, columnspan=2)
        self.fontRBtn[1].bind("<Enter>", func=lambda e: self.sayText("Calibri"))

        self.fontRBtn.append(tkinter.Radiobutton(self.frameUser, text="Cascadia Mono", variable=self.userFontVar, value="Cascadia Mono", command=self.function_changeFont,
                                                 bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]))
        self.fontRBtn[2].grid(row=6, column=0, columnspan=2)
        self.fontRBtn[2].bind("<Enter>", func=lambda e: self.sayText("Cascadia Mono"))

        self.fontRBtn.append(tkinter.Radiobutton(self.frameUser, text="Comic Sans MS", variable=self.userFontVar, value="Comic Sans MS", command=self.function_changeFont,
                                                 bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]))
        self.fontRBtn[3].grid(row=7, column=0, columnspan=2)
        self.fontRBtn[3].bind("<Enter>", func=lambda e: self.sayText("Comic Sans MS"))

        self.fontRBtn.append(tkinter.Radiobutton(self.frameUser, text="Courier New", variable=self.userFontVar, value="Courier New", command=self.function_changeFont,
                                                 bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]))
        self.fontRBtn[4].grid(row=8, column=0, columnspan=2)
        self.fontRBtn[4].bind("<Enter>", func=lambda e: self.sayText("Courier New"))

        self.fontRBtn.append(tkinter.Radiobutton(self.frameUser, text="Georgia", variable=self.userFontVar, value="Georgia", command=self.function_changeFont,
                                                 bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]))
        self.fontRBtn[5].grid(row=9, column=0, columnspan=2)
        self.fontRBtn[5].bind("<Enter>", func=lambda e: self.sayText("Georgia"))

        self.fontRBtn.append(tkinter.Radiobutton(self.frameUser, text="Times New Roman", variable=self.userFontVar, value="Times New Roman", command=self.function_changeFont,
                                                 bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]))
        self.fontRBtn[6].grid(row=10, column=0, columnspan=2)
        self.fontRBtn[6].bind("<Enter>", func=lambda e: self.sayText("Times New Roman"))

        self.fontRBtn.append(tkinter.Radiobutton(self.frameUser, text="Verdana", variable=self.userFontVar, value="Verdana", command=self.function_changeFont,
                                                 bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]))
        self.fontRBtn[7].grid(row=11, column=0, columnspan=2)
        self.fontRBtn[7].bind("<Enter>", func=lambda e: self.sayText("Verdana"))
        self.userFontVar.set(self.userFont)

        # Themes
        tkinter.Label(master=self.frameUser, text="Theme", bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]).grid(row=12, column=0)
        self.userThemeVar = tkinter.StringVar()
        self.themeRBtn = []
        self.themeRBtn.append(tkinter.Radiobutton(self.frameUser, text="Quiet Light (Tritanomaly)", variable=self.userThemeVar, value="Quiet Light (Tritanomaly)",
                                                  command=self.function_changeTheme, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]))
        self.themeRBtn[0].grid(row=13, column=0, columnspan=2)
        self.themeRBtn[0].bind("<Enter>", func=lambda e: self.sayText("Quiet Light (Tritanomaly)"))

        self.themeRBtn.append(tkinter.Radiobutton(self.frameUser, text="Light + (Tritanomaly)", variable=self.userThemeVar, value="Light + (Tritanomaly)",
                                                  command=self.function_changeTheme, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]))
        self.themeRBtn[1].grid(row=14, column=0, columnspan=2)
        self.themeRBtn[1].bind("<Enter>", func=lambda e: self.sayText("Light + (Tritanomaly)"))

        self.themeRBtn.append(tkinter.Radiobutton(self.frameUser, text="Solarized Light (Protanomaly)", variable=self.userThemeVar, value="Solarized Light (Protanomaly)",
                                                  command=self.function_changeTheme, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]))
        self.themeRBtn[2].grid(row=15, column=0, columnspan=2)
        self.themeRBtn[2].bind("<Enter>", func=lambda e: self.sayText("Solarized Light (Protanomaly)"))

        self.themeRBtn.append(tkinter.Radiobutton(self.frameUser, text="Dark + (Protanomaly/ Deuteranomaly)", variable=self.userThemeVar, value="Dark + (Protanomaly/ Deuteranomaly)",
                                                  command=self.function_changeTheme, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]))
        self.themeRBtn[3].grid(row=16, column=0, columnspan=2)
        self.themeRBtn[3].bind("<Enter>", func=lambda e: self.sayText("Dark + (Protanomaly/ Deuteranomaly)"))

        self.themeRBtn.append(tkinter.Radiobutton(self.frameUser, text="Monokai (Tritanomaly)", variable=self.userThemeVar, value="Monokai (Tritanomaly)",
                                                  command=self.function_changeTheme, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]))
        self.themeRBtn[4].grid(row=17, column=0, columnspan=2)
        self.themeRBtn[4].bind("<Enter>", func=lambda e: self.sayText("Monokai (Tritanomaly)"))

        self.themeRBtn.append(tkinter.Radiobutton(self.frameUser, text="Solarized Dark (Protanomaly)", variable=self.userThemeVar, value="Solarized Dark (Protanomaly)",
                                                  command=self.function_changeTheme, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]))
        self.themeRBtn[5].grid(row=18, column=0, columnspan=2)
        self.themeRBtn[5].bind("<Enter>", func=lambda e: self.sayText("Solarized Dark (Protanomaly)"))

        self.themeRBtn.append(tkinter.Radiobutton(self.frameUser, text="Red (Tritanomaly)", variable=self.userThemeVar, value="Red (Tritanomaly)",
                                                  command=self.function_changeTheme, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]))
        self.themeRBtn[6].grid(row=19, column=0, columnspan=2)
        self.themeRBtn[6].bind("<Enter>", func=lambda e: self.sayText("Red (Tritanomaly)"))

        self.themeRBtn.append(tkinter.Radiobutton(self.frameUser, text="Black & White (Monochromacy)", variable=self.userThemeVar, value="Black & White (Monochromacy)",
                                                  command=self.function_changeTheme, bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5]))
        self.themeRBtn[7].grid(row=20, column=0, columnspan=2)
        self.themeRBtn[7].bind("<Enter>", func=lambda e: self.sayText("Black & White (Monochromacy)"))
        self.userThemeVar.set(self.userTheme)

        # TTS
        self.ttsLbl = tkinter.Label(master=self.frameUser, text="Text to speech: "+str(self.tts), 
                                    bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5])
        self.ttsLbl.grid(row=21, column=0)
        self.ttsBtn = tkinter.Button(master = self.frameUser, text="Toggle TTS", command=self.toggleTTS, 
                                     bg=constants.themes[self.userTheme][0], fg=constants.themes[self.userTheme][5])
        self.ttsBtn.grid(row=21, column=1)
        self.ttsBtn.bind("<Enter>", func=lambda e: self.sayText("Toggle text to speech", False))
        tkinter.Label(self.frameUser, height=50, bg=constants.themes[self.userTheme][0]).grid(row=22, column = 0)
        self.frameUser.mainloop()

    def function_logout(self):
        self.window.config(cursor="watch")
        self.window.update()
        response = requests.get(url=constants.INVOKE_URLs["logout"],
                                 params={"email": self.emailAddress,
                                         "MAC_ADDRESS": self.MAC_ADDRESS})
        self.window.config(cursor="")
        statusCode = response.status_code
        if statusCode != 200:
            tkinter.messagebox.showerror(title="Log out", message="Something went wrong, please try again.")
        self.window.destroy()
        exit()
        
    def function_toggleRememberMe(self):
        self.window.config(cursor="wait")
        self.window.update()
        response = requests.get(url=constants.INVOKE_URLs["toggleRememberMe"],
                                 params={"email": self.emailAddress,
                                         "MAC_ADDRESS": self.MAC_ADDRESS})
        self.window.config(cursor="")
        statusCode = response.status_code
        if statusCode != 200:
            tkinter.messagebox.showerror(title="Toggle Remember Me", message="Something went wrong, please try again.")
        self.rememberMe = json.loads(response.text)["rememberMe"]
        self.rememberMeLbl["text"] = "Remember me: "+str(self.rememberMe)
    
    def function_changeFont(self):
        self.userFont = self.userFontVar.get()
        tkinter.font.nametofont("TkDefaultFont").configure(family=self.userFont, size=9)
        self.setData()
        
    def function_changeTheme(self):
        self.userTheme = self.userThemeVar.get()
        self.window.configure(bg=constants.themes[self.userTheme][0])

        # Set Menu frame colours
        self.frameMenu.config(bg=constants.themes[self.userTheme][1])
        for i in range(6):
            self.menuItems[i].config(bg=constants.themes[self.userTheme][6], fg=constants.themes[self.userTheme][2])
        self.menuItems[6].config(bg=constants.themes[self.userTheme][1])

        self.setData()
        self.user_tab()

    def toggleTTS(self):
        if self.tts:
            self.sayText("Text to speech disabled", False)
        self.tts = not self.tts
        self.setData()
        self.user_tab()

    def sayText(self, text, checkTTS=True):
        print(text)
        if checkTTS:
            if self.tts:
                self.engine.say(text)
                self.engine.runAndWait()
        else:
            self.engine.say(text)
            self.engine.runAndWait()


if __name__ == "__main__":
    import main
    main.AutoMark()