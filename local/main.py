# To extract MAC address
import uuid
# Console elements
import signIn
import console

def AutoMark():
    MAC_ADDRESS = ':'.join(['{:02x}'.format((uuid.getnode() >> element) & 0xff) for element in range(0,8*6,8)][::-1])
    app_SignIn = signIn.signIn(MAC_ADDRESS) # signIn.signIn(window, MAC_ADDRESS)
    app_Console = console.console(MAC_ADDRESS)



if __name__== "__main__":
    AutoMark()

