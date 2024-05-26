import tkinter as tk
import tkinter.messagebox as messagebox
import pymysql
from Tracker import open_pyqt5_window
import random
import string
import json


def signin_command():
    # Get username and password from entry fields
    input_username = signin_username.get()
    input_password = password.get()

    # Connect to the MySQL database
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='1000emre',
                                 database='pricetracker')
    
    # Create a cursor object to execute SQL commands
    cursor = connection.cursor()

    # Execute a SELECT query to check if the username/password combination exists
    select_query = "SELECT * FROM Users WHERE username = %s AND password = %s"
    cursor.execute(select_query, (input_username, input_password))

    # Fetch the result
    user = cursor.fetchone()

    if user:
        print("Login successful")
        if remember_me_var.get():
            remember_user(input_username)
        root.destroy()
        open_pyqt5_window(input_username)
    else:
        print("Invalid username or password")
        messagebox.showwarning("Error","Invalid username or password")
        # Optionally, display an error message to the user

    # Close the cursor and connection
    cursor.close()
    connection.close()

def remember_user(username):
    remember_data = {"username": username, "remember_me": True}
    with open("remember.json", "w") as f:
        json.dump(remember_data, f)

def auto_login():
    try:
        with open("remember.json", "r") as f:
            remember_data = json.load(f)
            if remember_data["remember_me"]:
                username = remember_data["username"]
                root.destroy()
                f.close()
                open_pyqt5_window(username)
    except FileNotFoundError:
        pass
    
def signup_command():
    # Get user input from the registration form
    new_username = signup_username.get()
    new_email = email.get()
    new_password = signup_password.get()
    new_confirm_password = confirm_password.get()

    # Check if passwords match
    if new_password != new_confirm_password:
        # Display an error message or handle password mismatch
        print("Passwords do not match")
        messagebox.showwarning("Password Mismatch", "Passwords do not match")
        return

    # Check if email ends with '@gmail.com' or '@hotmail.com'
    if not (new_email.endswith('@gmail.com') or new_email.endswith('@hotmail.com')):
        print("Please enter a valid email address ending with '@gmail.com' or '@hotmail.com'")
        messagebox.showwarning("Invalid Email", "Please enter a valid email address")
        return

    # Check if password length is at least 8 characters
    if len(new_password) < 8:
        print("Password must be at least 8 characters long")
        messagebox.showwarning("Short Password", "Password must be at least 8 characters long")
        return
    
    # Connect to the MySQL database
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='1000emre',
                                 database='pricetracker')
    
    try:
        # Create a cursor object to execute SQL commands
        with connection.cursor() as cursor:
            # Check if the username already exists
            cursor.execute("SELECT * FROM Users WHERE username = %s", (new_username,))
            existing_username = cursor.fetchone()

            # Check if the email already exists
            cursor.execute("SELECT * FROM Users WHERE mail = %s", (new_email,))
            existing_email = cursor.fetchone()

            if existing_username:
                print("Username already exists. Please choose a different username.")
                messagebox.showwarning("Invalid Username", "Username already exists. Please choose a different username.")
                return

            if existing_email:
                print("Email already exists. Please use a different email address.")
                messagebox.showwarning("Invalid Email", "Email already exists. Please choose a different username.")
                return

            # If username and email are unique, insert the new user into the database
            insert_query = "INSERT INTO Users (username, mail, password) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (new_username, new_email, new_password))

        # Commit the transaction
        connection.commit()

        # Optionally, display a success message or perform other actions after registration
        print("Registration successful")
        messagebox.showwarning("","Registration successful")
        signin_show_command()
    
    finally:
        # Close the connection
        connection.close()



def signup_show_command():
    login_frame.pack_forget()  # Hide the login frame
    signup_frame.pack()        # Show the signup frame

root = tk.Tk()
auto_login()
root.title('Sign in / Sign up')
root.geometry('925x500+300+200')
root.configure(bg='#fff')
root.resizable(False,False)

remember_me_var = tk.BooleanVar()

login_frame = tk.Frame(root, width=925, height=500, bg='white')
login_frame.pack_propagate(False)   

img = tk.PhotoImage(file='login.png')
tk.Label(login_frame, image=img, bg='white').place(x=50, y=50)

heading = tk.Label(login_frame, text='Sign in', fg='#57a1f8', bg='white', font=('Microsoft YaHei UI Light', 23, 'bold'))
heading.place(x=580, y=75)

remember_me_checkbox = tk.Checkbutton(login_frame, text="Remember Me", variable=remember_me_var, bg='white', font=('Microsoft YaHei UI Light', 9))
remember_me_checkbox.place(x=510, y=310)

def on_enter(e):
    signin_username.delete(0, 'end')

def on_leave(e):
    if signin_username.get() == '':
        signin_username.insert(0, 'Username')

signin_username = tk.Entry(login_frame, width=25, fg='black', border=0, bg="white", font=('Microsoft YaHei UI Light', 11))
signin_username.place(x=510, y=150)
signin_username.insert(0, 'Username')
signin_username.bind('<FocusIn>', on_enter)
signin_username.bind('<FocusOut>', on_leave)
tk.Frame(login_frame, width=295, height=2, bg='black').place(x=505, y=177)

def on_entera(e):
    password['show'] = '*'
    password.delete(0, 'end')

def on_leavea(e):
    if password.get() == '' or password.get() == 'Password':
        password['show'] = ''
        password.insert(0, 'Password')

def toggle_password_visibility():
    if password["show"] == "*":
        password.config(show="")
        show_button.config(text="👁️")
    else:
        password.config(show="*")
        show_button.config(text="👁️‍🗨️")

show_button = tk.Button(login_frame, text="👁️", bg="white", fg="#57a1f8", border=0, font=('Microsoft YaHei UI Light', 9), command=toggle_password_visibility)
show_button.place(x=735, y=220)
password = tk.Entry(login_frame, width=25, fg='black', border=0, bg="white", font=('Microsoft YaHei UI Light', 11))
password.place(x=510, y=220)
password.insert(0, 'Password')
password.bind('<FocusIn>', on_entera)
password.bind('<FocusOut>', on_leavea)
tk.Frame(login_frame, width=295, height=2, bg='black').place(x=505, y=247)

tk.Button(login_frame, width=39, pady=7, text='Sign in', bg='#57a1f8', fg='white', border=0, command=signin_command).place(x=515, y=274)
label = tk.Label(login_frame, text="Don't have an account?", fg='black', bg='white', font=('Microsoft YaHei UI Light', 9))
label.place(x=555, y=340)

sign_up = tk.Button(login_frame, width=6, text='Sign up', border=0, bg='white', cursor='hand2', fg='#57a1f8', command=signup_show_command)
sign_up.place(x=695, y=340)

signup_frame = tk.Frame(root, width=925, height=500, bg='white')
signup_frame.pack_propagate(False)

signup_img = tk.PhotoImage(file='register.png')
tk.Label(signup_frame, image=signup_img, border=0, bg='white').place(x=530, y=160)

def signin_show_command():
    signup_frame.pack_forget()  # Hide the signup frame
    login_frame.pack()        # Show the login frame

# Create the signup frame
signup_frame = tk.Frame(root, width=925, height=500, bg='white')
signup_frame.pack_propagate(False)

# Load the image for the signup page
signup_img = tk.PhotoImage(file='register.png')
tk.Label(signup_frame, image=signup_img, border=0, bg='white').place(x=50, y=90)

# Signup heading
signup_heading = tk.Label(signup_frame, text='Sign up', fg="#57a1f8", bg='white', font=('Microsoft YaHei UI Light', 23, 'bold'))
signup_heading.place(x=580, y=55)

def on_enter(e):
    signup_username.delete(0, 'end')

def on_leave(e):
    if signup_username.get() == '':
        signup_username.insert(0, 'Username')

# Signup username entry
signup_username = tk.Entry(signup_frame, width=25, fg='black', border=0, bg='white', font=('Microsoft YaHei UI Light', 11))
signup_username.place(x=510, y=120)
signup_username.insert(0, 'Username')
signup_username.bind('<FocusIn>', on_enter)
signup_username.bind('<FocusOut>', on_leave)
tk.Frame(signup_frame, width=295, height=2, bg='black').place(x=505, y=147)

def on_enter(e):
    email.delete(0, 'end')

def on_leave(e):
    if email.get() == '':
        email.insert(0, 'Email')

# Signup email entry
email = tk.Entry(signup_frame, width=25, fg='black', border=0, bg='white', font=('Microsoft YaHei UI Light', 11))
email.place(x=510, y=180)
email.insert(0, 'Email')
email.bind('<FocusIn>', on_enter)
email.bind('<FocusOut>', on_leave)
tk.Frame(signup_frame, width=295, height=2, bg='black').place(x=505, y=207)

def on_enterb(e):
    signup_password['show'] = '*'
    signup_password.delete(0, 'end')

def on_leaveb(e):
    if signup_password.get() == '' or signup_password.get() == 'Password':
        signup_password['show'] = ''
        signup_password.insert(0, 'Password')
        
def generate_random_password():
     # Generate a random password of length 8
    passwordd = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    # Insert the generated password into the password entry field
    signup_password.delete(0, 'end')
    signup_password.insert(0, passwordd)
    confirm_password.delete(0, 'end')
    confirm_password.insert(0, passwordd)

def toggle_signup_password_visibility():
    if signup_password["show"] == "*":
        signup_password.config(show="")
        show_signup_button.config(text="👁️")
    else:
        signup_password.config(show="*")
        show_signup_button.config(text="👁️‍🗨️")

show_signup_button = tk.Button(signup_frame, text="👁️", bg="white", fg="#57a1f8", border=0, font=('Microsoft YaHei UI Light', 9), command=toggle_signup_password_visibility)
show_signup_button.place(x=735, y=240)
    
# Signup password entry
signup_password = tk.Entry(signup_frame, width=25, fg='black', border=0, bg='white', font=('Microsoft YaHei UI Light', 11))
signup_password.place(x=510, y=240)
signup_password.insert(0, 'Password')
signup_password.bind('<FocusIn>', on_enterb)
signup_password.bind('<FocusOut>', on_leaveb)
tk.Frame(signup_frame, width=295, height=2, bg='black').place(x=505, y=267)

# Create a button to generate a random password
random_password_button = tk.Button(signup_frame, text='Random Password', width=16, height=1, bg='#57a1f8', fg='white', border=0, command=generate_random_password)
random_password_button.place(x=680, y=218)


def on_enterc(e):
    confirm_password['show'] = '*'
    confirm_password.delete(0, 'end')

def on_leavec(e):
    if confirm_password.get() == '' or confirm_password.get() == 'Password':
        confirm_password['show'] = ''
        confirm_password.insert(0, ' Confirm Password')

def toggle_confirm_password_visibility():
    if confirm_password["show"] == "*":
        confirm_password.config(show="")
        show_confirm_button.config(text="👁️")
    else:
        confirm_password.config(show="*")
        show_confirm_button.config(text="👁️‍🗨️")

show_confirm_button = tk.Button(signup_frame, text="👁️", bg="white", fg="#57a1f8", border=0, font=('Microsoft YaHei UI Light', 9), command=toggle_confirm_password_visibility)
show_confirm_button.place(x=735, y=300)

# Confirm password entry
confirm_password = tk.Entry(signup_frame, width=25, fg='black', border=0, bg='white', font=('Microsoft YaHei UI Light', 11))
confirm_password.place(x=510, y=300)
confirm_password.insert(0, 'Confirm Password')
confirm_password.bind('<FocusIn>', on_enterc)
confirm_password.bind('<FocusOut>', on_leavec)
tk.Frame(signup_frame, width=295, height=2, bg='black').place(x=505, y=327)

# Signup button
tk.Button(signup_frame, width=39, pady=7, text='Sign up', bg='#57a1f8', fg='white', border=0, command= signup_command).place(x=515, y=355)

# Already have an account label
label = tk.Label(signup_frame, text='I have an account', fg='black', bg='white', font=('Microsoft YaHei UI Light', 9))
label.place(x=570, y=415)

# Sign in button
signin = tk.Button(signup_frame, width=6, text='Sign in', border=0, bg='white', cursor='hand2', fg='#57a1f8', command=signin_show_command)
signin.place(x=680, y=415)


login_frame.pack()  # Initially show the login frame

root.mainloop()
