import subprocess
import tkinter as tk
import tkinter.messagebox as messagebox
import pymysql 
from Tracker import open_pyqt5_window
import random
import string
import json
import smtplib
import tkinter.simpledialog as simpledialog
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def ask_string_with_size(title, prompt, entry_width=35, width=300, height=120, spawn_x=620, spawn_y=410):
    # Create a new Toplevel window
    dialog = tk.Toplevel()
    dialog.title(title)
    
    # Set the size and position of the window
    if spawn_x is not None and spawn_y is not None:
        dialog.geometry(f"{width}x{height}+{spawn_x}+{spawn_y}")
    else:
        dialog.geometry(f"{width}x{height}")

    # Create a Label for the prompt
    label = tk.Label(dialog, text=prompt)
    label.pack(pady=10)

    # Create a StringVar to store the user input
    user_input = tk.StringVar()
    
    # Create an Entry widget for user input
    entry = tk.Entry(dialog, textvariable=user_input, width=entry_width)
    entry.pack(pady=5)

    # Function to return the user input when OK button is clicked
    def on_ok():
        dialog.destroy()

    # Create a button to confirm the input
    ok_button = tk.Button(dialog, text="OK", command=on_ok)
    ok_button.pack(pady=5)

    # Focus on the Entry widget
    entry.focus_set()

    # Wait for the dialog to be closed
    dialog.wait_window(dialog)

    # Return the user input
    return user_input.get()

def generate_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


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
    if not (new_email.endswith('@gmail.com')):
        print("Please enter a valid gmail adress")
        messagebox.showwarning("Invalid Gmail", "Please enter a valid gmail adress")
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

            verification_code = generate_code()
            send_emaill(new_email, verification_code)
            
            enteredd_code = ask_string_with_size("Verification", "Enter the verification code sent to your gmail:")
            if enteredd_code == verification_code:
                # If username and email are unique, insert the new user into the database
                insert_query = "INSERT INTO Users (username, mail, password) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (new_username, new_email, new_password))
            else:
                return

        # Commit the transaction
        connection.commit()

        # Optionally, display a success message or perform other actions after registration
        print("Registration successful")
        messagebox.showinfo("Successful","Registration successful you can login to your account.")
        signin_show_command()
    
    finally:
        # Close the connection
        connection.close()

def send_email(receiver_email, code):
    # Your email sending logic here
    smtp_server = "smtp.gmail.com"  # Update with your SMTP server
    smtp_port = 587  # Update with your SMTP port
    sender_email = "pricetrackereo@gmail.com"  # Update with your email address
    sender_password = "exyn kiqc kjxf fdvx"  # Update with your email password
    
    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Password Reset Code"

    # Add body to email
    body = f"Your password reset code is: {code}"
    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

def send_emaill(receiver_email, code):
    # Your email sending logic here
    smtp_server = "smtp.gmail.com"  # Update with your SMTP server
    smtp_port = 587  # Update with your SMTP port
    sender_email = "pricetrackereo@gmail.com"  # Update with your email address
    sender_password = "exyn kiqc kjxf fdvx"  # Update with your email password
    
    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Account Verification"

    # Add body to email
    body = f"Your verification code is: {code}"
    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

def forgot_password():
    # Ask the user to enter their email address
    email = ask_string_with_size("Forgot Password", "Enter your email address:")

    # Check if the email address exists in the database
    if not email_exists(email) and email != "":
        messagebox.showerror("Error", "Email address not found. Please enter a valid email.")
        email = ask_string_with_size("Forgot Password", "Enter your email address:")
        return

    # Generate a random code
    code = generate_code()
    send_email(email, code)
    # Prompt the user to enter the code
    entered_code = ask_string_with_size("Forgot Password", "Enter the code sent to your email:")

    # Check if the entered code matches the generated code
    if entered_code == code:
        # If code is correct, prompt the user to enter a new password
        new_password = ask_string_with_size("Forgot Password", "Enter your new password:")
        if len(new_password) < 8:
            print("Password must be at least 8 characters long")
            messagebox.showwarning("Short Password", "Password must be at least 8 characters long")
            new_password = ask_string_with_size("Forgot Password", "Enter your new password:")
            return

        # Update the password in the database for the user with the provided email address
        update_password(email, new_password)
        messagebox.showinfo("Successful","Password updated")
        
    else:
        # If code is incorrect, display an error message
        messagebox.showerror("Error", "Invalid code. Please try again.")
        entered_code = ask_string_with_size("Forgot Password", "Enter the code sent to your email:")
        
def email_exists(email):
    # Connect to the MySQL database
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='1000emre',
                                 database='pricetracker')
    
    try:
        # Create a cursor object to execute SQL commands
        with connection.cursor() as cursor:
            # Execute a SELECT query to check if the email address exists
            select_query = "SELECT COUNT(*) FROM Users WHERE mail = %s"
            cursor.execute(select_query, (email,))
            result = cursor.fetchone()

            # If the result is not 0, the email exists in the database
            if result[0] != 0:
                return True
            else:
                return False

    finally:
        # Close the connection
        connection.close()

def update_password(email, new_password):
    # Connect to the MySQL database
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='1000emre',
                                 database='pricetracker')
    
    try:
        # Create a cursor object to execute SQL commands
        with connection.cursor() as cursor:
            # Update the password for the user with the provided email address
            update_query = "UPDATE Users SET password = %s WHERE mail = %s"
            cursor.execute(update_query, (new_password, email))

        # Commit the transaction
        connection.commit()

        # Optionally, display a success message or perform other actions after updating the password
        print("Password updated successfully")

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

img = tk.PhotoImage(file='saak_logo4.png')
tk.Label(login_frame, image=img, bg='white').place(x=150, y=120)

heading = tk.Label(login_frame, text='Sign in', fg='#57a1f8', bg='white', font=('Microsoft YaHei UI Light', 23, 'bold'))
heading.place(x=580, y=75)

logoaltyazi = tk.Label(login_frame, text="""
                                Welcome to SAAK application. To use
                                this application first you have to
                                create an account. İf you have already
                                an account then you can log in. """,
                       fg='black', bg='white', font=('Microsoft YaHei UI Light', 11))
logoaltyazi.place(x=0, y=210)

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

signup_img = tk.PhotoImage(file='saak_logo4.png')
tk.Label(signup_frame, image=signup_img, border=0, bg='white').place(x=530, y=160)



def signin_show_command():
    signup_frame.pack_forget()  # Hide the signup frame
    login_frame.pack()        # Show the login frame

# Create the signup frame
signup_frame = tk.Frame(root, width=925, height=500, bg='white')
signup_frame.pack_propagate(False)

# Load the image for the signup page
signup_img = tk.PhotoImage(file='saak_logo4.png')
tk.Label(signup_frame, image=signup_img, bg='white').place(x=150, y=120)

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
        email.insert(0, 'Gmail adress')


logoaltyazii = tk.Label(signup_frame, text="""
                                To register, choose a unique username 
                                for yourself, then enter your gmail, 
                                then you can log in to our application 
                                by creating a strong password. """,
                       fg='black', bg='white', font=('Microsoft YaHei UI Light', 11))
logoaltyazii.place(x=0, y=210)

# Signup email entry
email = tk.Entry(signup_frame, width=25, fg='black', border=0, bg='white', font=('Microsoft YaHei UI Light', 11))
email.place(x=510, y=180)
email.insert(0, 'Gmail adress')
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
forgot_password_button = tk.Button(login_frame, width=13, text='Forgot Password', bg='white', fg='#57a1f8', border=1, command=forgot_password)
forgot_password_button.place(x=695, y=310)

login_frame.pack()  # Initially show the login frame

root.mainloop()
