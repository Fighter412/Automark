# GUI elements
import tkinter, tkinter.ttk, tkinter.messagebox, tkinter.font
# Logic elements
import requests, json, hashlib, constants

class signIn():

    def __init__(self, MAC_ADDRESS):
        self.MAC_ADDRESS = MAC_ADDRESS
        # If user has set up remember me, the login procedure is skipped
        if self.rememberMeSignIn() == True:
            pass
        else:
            # Create window and run SignInSelect
            self.window = tkinter.Tk()
            self.window.geometry("500x300+710+390")
            self.window.resizable(False, False)
            tkinter.font.nametofont("TkDefaultFont").configure(family="Cascadia mono")
            self.currentFrame = False
            self.frame_SignInSelect()
        
    def rememberMeSignIn(self):
        # Extract locally stored email
        file_email = open(constants.ASSETS_PATH+"/email.txt", "r")
        emailAddress = file_email.readline()
        file_email.close()
        # Obtain a response from AWS
        response = requests.get(url=constants.INVOKE_URLs["logInRememberMe"],
                                 params={"email": emailAddress,
                                         "MAC_ADDRESS": self.MAC_ADDRESS})
        statusCode = response.status_code
        if statusCode != 200:
            return(False)
        success = json.loads(response.text)["success"]
        return(success)

    def frame_SignInSelect(self):
        # Removes the previous frame if it has a value to prevent execution
        # when first running as self.currentFrame was set to False
        if self.currentFrame:
            self.currentFrame.destroy()
        # Creates the new frame and sets the currentFrame to the frame onscreen
        frameSignInOptions = tkinter.Frame(self.window)
        self.currentFrame = frameSignInOptions
        # Renames the title of the window and packs the frame in the window
        self.window.title("Sign In Options")
        frameSignInOptions.pack()
        # Create frame elements
        tkinter.ttk.Button(master=frameSignInOptions, text="Login", command=self.frame_Login).pack(ipadx=20, ipady=10)
        tkinter.ttk.Button(master=frameSignInOptions, text="Sign Up", command=self.frame_SignUpEmail).pack(ipadx=20, ipady=10)
        # Wait for user inputs
        frameSignInOptions.mainloop()
    
    def frame_Login(self):
        # Removes the previous frame
        self.currentFrame.destroy()
        # Creates the new frame and sets the currentFrame to the frame onscreen
        frameLoginEmail = tkinter.Frame(self.window)
        self.currentFrame = frameLoginEmail
        # Renames the title of the window and packs the frame in the window
        self.window.title("Login")
        frameLoginEmail.pack()
        # Create frame elements
        tkinter.ttk.Label(master=frameLoginEmail, text="Email Address").grid(row=0, column=0)
        self.emailAddress = tkinter.StringVar()
        tkinter.ttk.Entry(master=frameLoginEmail, textvariable=self.emailAddress).grid(row=0, column=1)
        tkinter.ttk.Label(master=frameLoginEmail, text="Password").grid(row=1, column=0)
        self.password = tkinter.StringVar()
        tkinter.ttk.Entry(master=frameLoginEmail, textvariable=self.password, show="*").grid(row=1, column=1)
        tkinter.ttk.Button(master=frameLoginEmail, text="Continue", command=self.function_LoginCheck).grid(row=2, column=0, columnspan=2, ipadx=20, ipady=10)
        tkinter.ttk.Button(master=frameLoginEmail, text="Cancel", command=self.frame_SignInSelect).grid(row=3, column=0, columnspan=2, ipadx=20, ipady=10)
        # Wait for user inputs
        frameLoginEmail.mainloop()
    
    def function_LoginCheck(self):
        # Check if user would like remember me
        rememberMe = tkinter.messagebox.askquestion(title="Remember Me", message="Would you like to remember me on this device?", type="yesno")
        if rememberMe == "yes":
            rememberMeBool = str(int(True))
        else:
            rememberMeBool = str(int(False))
        email = self.emailAddress.get()
        password = self.password.get()
        file_email = open(constants.ASSETS_PATH+"/email.txt", "w")
        file_email.write(email)
        file_email.close()
        password_hash = hashlib.pbkdf2_hmac(constants.hash_algorithm, password.encode("utf-8"), email.encode("utf-8"), constants.hash_repitition).hex()
        # Get response from AWS
        self.window.config(cursor="watch")
        self.window.update()
        response = requests.get(url=constants.INVOKE_URLs["logInCheckEmail"],
                                 params={"email": email,
                                         "MAC_ADDRESS": self.MAC_ADDRESS,
                                         "password": password_hash,
                                         "rememberMe": rememberMeBool})
        self.window.config(cursor="")
        statusCode = response.status_code
        if statusCode != 200:
            tkinter.messagebox.showerror(title="Login", message="Something went wrong, please try again.")
            return()
        success = json.loads(response.text)["success"]
        if success:
            self.currentFrame.destroy()
            self.window.destroy()
        else:
            tkinter.messagebox.showerror(title="Login", message="Something went wrong, please try again.")

    def frame_SignUpEmail(self):
        # Removes the previous frame
        self.currentFrame.destroy()
        # Creates the new frame and sets the currentFrame to the frame onscreen
        frameSignUpEmail = tkinter.Frame(self.window)
        self.currentFrame = frameSignUpEmail
        # Renames the title of the window and packs the frame in the window
        self.window.title("Sign Up - Email")
        frameSignUpEmail.pack()
        # Create frame elements
        tkinter.ttk.Label(master=frameSignUpEmail, text="Email Address").grid(row=0, column=0)
        self.emailAddress = tkinter.StringVar()
        tkinter.ttk.Entry(master=frameSignUpEmail, textvariable=self.emailAddress).grid(row=0, column=1)
        self.signUpEmailLbl = tkinter.ttk.Label(master=frameSignUpEmail)
        self.signUpEmailLbl.grid(row=1, column=0, columnspan=2)
        self.signUpEmailFinishBtn = tkinter.ttk.Button(master=frameSignUpEmail, text="Continue", command=self.function_SignUpCheckEmail)
        self.signUpEmailFinishBtn.grid(row=2, column=0, columnspan=2, ipadx=20, ipady=10)
        self.signUpEmailFinishBtn["state"] = "disabled"
        tkinter.ttk.Button(master=frameSignUpEmail, text="Cancel", command=self.frame_SignInSelect).grid(row=3, columnspan=2, ipadx=20, ipady=10)
        # Trace the Email to update label
        self.emailAddress.trace_add(mode="write", callback=self.function_SignUpEmailValidator)
        # Wait for user inputs
        frameSignUpEmail.mainloop()

    def function_SignUpEmailValidator(self, a, b, c):
        invalid = True
        email = self.emailAddress.get()
        if email.count("@") == 1:
            if "." in email:
                if " " not in email:
                    self.signUpEmailLbl["text"] = ""
                    self.signUpEmailFinishBtn["state"] = "Enabled"
                    invalid = False
        if invalid:
            self.signUpEmailLbl["text"] = "Email must be a valid email address!"
            self.signUpEmailFinishBtn["state"] = "disabled"
    
    def function_SignUpCheckEmail(self):
        # Send email to user
        self.window.config(cursor="watch")
        self.window.update()
        response = requests.get(url=constants.INVOKE_URLs["signUpSendEmail"],
                                 params={"email": self.emailAddress.get(), "MAC_ADDRESS": self.MAC_ADDRESS})
        self.window.config(cursor="")
        statusCode = response.status_code
        if statusCode != 200:
            tkinter.messagebox.showerror(title="Sign Up - Email", message="Something went wrong, please try again.")
            return()
        self.frame_SignUpCode()
            
    def frame_SignUpCode(self):
        # Removes the previous frame
        self.currentFrame.destroy()
        # Creates the new frame and sets the currentFrame to the frame onscreen
        frameSignUpCode = tkinter.Frame(self.window)
        self.currentFrame = frameSignUpCode
        # Renames the title of the window and packs the frame in the window
        self.window.title("Sign Up - Confirmation Code")
        frameSignUpCode.pack()
        # Create frame elements
        tkinter.ttk.Label(master=frameSignUpCode, text="5 digit Confirmation Code").grid(row=0, column=0)
        self.signUpCode = tkinter.StringVar()
        tkinter.ttk.Entry(master=frameSignUpCode, textvariable=self.signUpCode).grid(row=0, column=1)
        self.codeLbl = tkinter.ttk.Label(master=frameSignUpCode)
        self.codeLbl.grid(row=1, column=0, columnspan=2)
        self.signUpCodeContinueBtn = tkinter.ttk.Button(master=frameSignUpCode, text="Continue", command=self.function_SignUpCheckCode, state="disabled")
        self.signUpCodeContinueBtn.grid(row=2, column=0, columnspan=2, ipadx=20, ipady=10)
        self.signUpCodeContinueBtn["state"] = "disabled"
        tkinter.ttk.Button(master=frameSignUpCode, text="Resend Email", command=self.frame_SignUpEmail).grid(row=3, column=0, columnspan=2, ipadx=20, ipady=10)
        # Trace the Code to update label
        self.signUpCode.trace_add(mode="write", callback=self.function_SignUpCodeValidator)
        # Wait for user inputs
        frameSignUpCode.mainloop()
    
    def function_SignUpCodeValidator(self, a, b, c):
        code = self.signUpCode.get()
        invalid = "False"
        if len(code) != 5:
            invalid = True
            self.codeLbl["text"] = "Code must be exactly 5 digits!"
        else:
            invalid = False
            for letter in code:
                if not ord("0") <= ord(letter) <= ord("9"):
                    invalid = True
                    self.codeLbl["text"] = "Code must contain only numeric characters!"
        if invalid:
            self.signUpCodeContinueBtn["state"] = "disabled"
        else:
            self.signUpCodeContinueBtn["state"] = "enabled"
            self.codeLbl["text"] = ""
    
    def function_SignUpCheckCode(self):
        # Get response from AWS
        self.window.config(cursor="watch")
        self.window.update()
        response = requests.get(url=constants.INVOKE_URLs["signUpCheckCode"],
                                 params={"email": self.emailAddress.get(),
                                         "code": self.signUpCode.get(),
                                         "MAC_ADDRESS": self.MAC_ADDRESS})
        self.window.config(cursor="")
        statusCode = response.status_code
        if statusCode != 200:
            tkinter.messagebox.showerror(title="Sign Up - Code", message="Something went wrong, please try again.")
            return()
        success = json.loads(response.text)["success"]
        if success:
            self.uniqueCode = json.loads(response.text)["uniqueCode"]
            self.frame_SignUpPassword()
        else:
            tkinter.messagebox.showerror(title="Sign Up - Code", message="Something went wrong, please try again.")

    def frame_SignUpPassword(self):
        # Removes the previous frame
        self.currentFrame.destroy()
        # Creates the new frame and sets the currentFrame to the frame onscreen
        frameSignUpPassword = tkinter.Frame(self.window)
        self.currentFrame = frameSignUpPassword
        # Renames the title of the window and packs the frame in the window
        self.window.title("Sign Up - Password")
        # Create frame elements
        tkinter.ttk.Label(master=frameSignUpPassword, text="Enter Password").grid(row=0, column=0)
        self.password = tkinter.StringVar()
        tkinter.ttk.Entry(master=frameSignUpPassword, textvariable=self.password, show="*").grid(row=0, column=1)
        tkinter.ttk.Label(master=frameSignUpPassword, text="Re-enter Password").grid(row=1, column=0)
        self.password2 = tkinter.StringVar()
        tkinter.ttk.Entry(master=frameSignUpPassword, textvariable=self.password2, show="*").grid(row=1, column=1)
        self.passwordLbl = tkinter.ttk.Label(master=frameSignUpPassword)
        self.passwordLbl.grid(row=2, column=0, columnspan=2)
        self.signUpPasswordFinishBtn = tkinter.ttk.Button(master=frameSignUpPassword, text="Finish", command=self.function_SignUpFinish)
        self.signUpPasswordFinishBtn.grid(row=3, column=0, columnspan=2, ipadx=20, ipady=10)
        self.signUpPasswordFinishBtn["state"] = "disabled"
        tkinter.ttk.Button(master=frameSignUpPassword, text="Resend Email", command=self.frame_SignUpEmail).grid(row=4, column=0, columnspan=2, ipadx=20, ipady=10)
        # Trace the passwords to update label
        self.password.trace_add(mode="write", callback=self.function_PasswordCheck)
        self.password2.trace_add(mode="write", callback=self.function_PasswordCheck)
        frameSignUpPassword.pack()
        # Wait for user inputs
        frameSignUpPassword.mainloop()
    
    def function_PasswordCheck(self, a, b, c):
        text = self.password.get()
        text2 = self.password2.get()
        if len(text) < 8:
            self.passwordLbl["text"] = "Password must be atleast 8 charachters"
            self.signUpPasswordFinishBtn["state"] = "disabled"
        else:
            symbols = "!£$&-+=@#?*%"
            errors = ["Atleast one capital letter is required", 
                      "Atleast one simple letter is required", 
                      "Atleast one number is required", 
                      "Atleast one symbol is requred ({0})".format(symbols)]
            for char in text:
                if ord("A") <= ord(char) <= ord("Z"):
                    if "Atleast one capital letter is required" in errors:
                        errors.remove("Atleast one capital letter is required")
                if ord("a") <= ord(char) <= ord("z"):
                    if "Atleast one simple letter is required" in errors:
                        errors.remove("Atleast one simple letter is required")
                if ord("0") <= ord(char) <= ord("9"):
                    if "Atleast one number is required" in errors:
                        errors.remove("Atleast one number is required")
                if char in symbols:
                    if "Atleast one symbol is requred ({0})".format(symbols) in errors:
                        errors.remove("Atleast one symbol is requred ({0})".format(symbols))
            if len(errors) > 0:
                self.passwordLbl["text"] = errors[0]
                self.signUpPasswordFinishBtn["state"] = "disabled"
            else:
                if text != text2:
                    self.passwordLbl["text"] = "Both entries must contain the same password"
                    self.signUpPasswordFinishBtn["state"] = "disabled"
                else:
                    self.passwordLbl["text"] = "Good to go"
                    self.signUpPasswordFinishBtn["state"] = "enabled"
    
    def function_SignUpFinish(self):
        # Check if user would like remember me
        rememberMe = tkinter.messagebox.askquestion(title="Remember Me", message="Would you like to remember me on this device?", type="yesno")
        if rememberMe == "yes":
            rememberMeBool = str(int(True))
        else:
            rememberMeBool = str(int(False))
        email = self.emailAddress.get()
        password = self.password.get()
        password_hash = hashlib.pbkdf2_hmac(constants.hash_algorithm, password.encode("utf-8"), email.encode("utf-8"), constants.hash_repitition).hex()
        print(password_hash)
        # Get response from AWS
        self.window.config(cursor="watch")
        self.window.update()
        response = requests.get(url=constants.INVOKE_URLs["signUpCreateAccountS3"],
                                 params={"email": email,
                                         "MAC_ADDRESS": self.MAC_ADDRESS,
                                         "uniqueCode": self.uniqueCode,
                                         "password": password_hash,
                                         "rememberMe": rememberMeBool})
        self.window.config(cursor="")
        statusCode = response.status_code
        if statusCode != 200:
            tkinter.messagebox.showerror(title="Login", message="Something went wrong, please try again.")
            return()
        success = json.loads(response.text)["success"]
        if success:
            file_email = open(constants.ASSETS_PATH+"/email.txt", "w")
            file_email.write(self.emailAddress.get())
            file_email.close()
            self.currentFrame.destroy()
            self.window.destroy()
        else:
            tkinter.messagebox.showerror(title="Password", message="Something went wrong, please try again.")

if __name__ == "__main__":
    import main
    main.AutoMark()