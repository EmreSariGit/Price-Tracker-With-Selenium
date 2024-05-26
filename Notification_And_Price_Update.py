import pymysql
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

# Function to fetch product information from the database
def fetch_product_info():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='1000emre',
        database='pricetracker',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            # Fetch product information from the Products table, including user email
            cursor.execute("SELECT p.*, u.mail AS email FROM Products p JOIN Users u ON p.username = u.username")
            products = cursor.fetchall()
            for product in products:
                # Convert price from string to float
                product['product_price'] = int(product['product_price'].replace('.', '').replace(' TL', ''))
            return products
    finally:
        connection.close()

# Function to update product price in the database
def update_product_price(product_link, product_price):
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='1000emre',
        database='pricetracker'
    )
    try:
        with connection.cursor() as cursor:
            # Update product price in the Products table
            cursor.execute("UPDATE Products SET product_price = %s WHERE product_link = %s", (product_price, product_link))
            connection.commit()
    finally:
        connection.close()

# Function to send email notification
def send_email(product_name, product_link, old_price, new_price, email):
    sender_email = "pricetrackereo@gmail.com"  # Your email address
    receiver_email = email  # Receiver email address
    password = "exyn kiqc kjxf fdvx"  # Your email password

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Price Drop Notification"

    old_price_float = old_price
    new_price_float = new_price
    
    # Calculate percentage change
    percentage_change = ((old_price_float - new_price_float) / old_price_float) * 100
    
    body = f"The price of {product_name} has dropped!\n\n"
    body += f"Old Price: {old_price} TL\n"
    body += f"New Price: {new_price} TL\n"
    body += f"The product is ({"%.2f" % percentage_change}% cheaper)\n"
    body += f"You can buy it now at {product_link}."
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

# Set up Selenium WebDriver
options = Options()
options.headless = True  # Run Chrome in headless mode (without UI)
service = Service(ChromeDriverManager().install())

while True:
    
    # Fetch product information from the database
    products = fetch_product_info()

    
    # Initialize Chrome WebDriver
    driver = webdriver.Chrome(service=service, options=options)

    for product in products:
        product_name = product['product_name']
        product_link = product['product_link']
        try:
            print(f"Email of user: {product['email']}")
            
            # Visit each product link
            driver.get(product_link)
            price_element = driver.find_element(By.CLASS_NAME, 'a-price-whole')
            # Extract product price (You need to implement this part based on the structure of the webpage)
            product_price = price_element.text

            # Update product price in the database
            update_product_price(product_link, product_price)

            print(f"Price for {product_name}: {product_price}")

            # Convert new product price to float
            product_price = int(product_price.replace('.', '').replace(' TL', ''))

            if product_price < product['product_price']:
                # Send email notification
                send_email(product_name, product_link, product['product_price'], product_price, product['email'])
                print(f"Email notification sent to {product['email']}")
        except Exception as e:
            print(f"Error processing {product_name}: {str(e)}")

    # Quit the WebDriver
    driver.quit()

    # Wait for an hour before running the loop again
    time.sleep(3600)  # 3600 seconds = 1 hour
