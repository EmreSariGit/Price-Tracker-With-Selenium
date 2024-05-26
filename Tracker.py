import sys
import pymysql
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit, QHeaderView, QAbstractItemView, QHBoxLayout, QScrollArea, QSizePolicy, QStyledItemDelegate, QStackedWidget, QComboBox
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QDesktopServices
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import threading
import requests
from selenium.common.exceptions import NoSuchElementException
import os
import time

 
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.35"


def open_pyqt5_window(username):
    app = QApplication(sys.argv)
    window = MainWindow(username)
    window.show()
    sys.exit(app.exec_())
    
class CustomHeaderView(QHeaderView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        # Prevent selecting the entire column when cl   icking on the header
        pass

class ImageWidget(QWidget):
    def __init__(self, image_url, width=100, height=100):  # Adjust width and height as needed
        super().__init__()
        layout = QHBoxLayout()
        self.label = QLabel()
        self.label.setFixedSize(width, height)  # Set fixed size for the QLabel
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.load_image(image_url)

    def load_image(self, image_url):
        # Fetch the image data using requests
        response = requests.get(image_url)
        if response.status_code == 200:
            image_data = response.content
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            # Scale the pixmap to fit the fixed size of the QLabel
            pixmap = pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)
        else:
            print("Failed to fetch image:", response.status_code)

class ClickableSecondColumnTableWidget(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if item is not None and self.column(item) == 3:
            super().mousePressEvent(event)  # Handle the event for the first column item
        else:
            event.ignore()  # Ignore mouse press event for other columns

class LinkDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(LinkDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if index.column() == 3: 
            url = index.data(Qt.DisplayRole)
            rect = option.rect
            text = index.model().data(index, Qt.DisplayRole)
            option.displayAlignment = Qt.AlignLeft | Qt.AlignTop
            option.textElideMode = Qt.ElideNone
            painter.setPen(Qt.blue)
            painter.drawText(rect, Qt.AlignCenter | Qt.TextWrapAnywhere, text)
        else:
            super().paint(painter, option, index)

    def editorEvent(self, event, model, option, index):
        if index.column() == 3 and event.type() == event.MouseButtonRelease:
            url = index.data(Qt.DisplayRole)
            QDesktopServices.openUrl(QUrl(url))
            return True
        return super().editorEvent(event, model, option, index)
    

class MainWindow(QMainWindow):
    
    def __init__(self, username):
        super().__init__()
        self.username = username
        username = self.username
        
        self.connection = pymysql.connect(
            host='localhost',
            user='root',
            password='1000emre',
            database='pricetracker',
            cursorclass=pymysql.cursors.DictCursor
        )

        self.setWindowTitle("Amazon Product Tracker")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create the stacked widget
        self.stackedWidget = QStackedWidget()
        
        # Create the different menus
        self.products = self.menu_tracked_products()
        self.search = self.menu_search_products()
        self.profile = self.menu_profile()
        
        # Add menus to the stacked widget
        self.stackedWidget.addWidget(self.products)
        self.stackedWidget.addWidget(self.search)
        self.stackedWidget.addWidget(self.profile)
        
        # Create bottom navigation buttons
        self.productsButton = QPushButton('Tracked Products')
        self.searchButton = QPushButton('Search')
        self.profileButton = QPushButton('Profile')
        
        # Connect buttons to methods and update styles
        self.productsButton.clicked.connect(lambda: self.changePage(self.products, self.productsButton))
        self.searchButton.clicked.connect(lambda: self.changePage(self.search, self.searchButton))
        self.profileButton.clicked.connect(lambda: self.changePage(self.profile, self.profileButton))
        
        # Initial button styles
        self.buttons = [self.productsButton, self.searchButton, self.profileButton]
        self.updateButtonStyles(self.searchButton)
        self.stackedWidget.setCurrentWidget(self.search)
        
        # Layout for buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.productsButton)
        buttonLayout.addWidget(self.searchButton)
        buttonLayout.addWidget(self.profileButton)
        
       # Main layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.stackedWidget)
        mainLayout.addLayout(buttonLayout)
        
        # Central widget
        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        
        self.setCentralWidget(centralWidget)
        
        # Start thread to open Amazon
        thread = threading.Thread(target=self.open_amazon)
        thread.start()   
        
    
    def open_amazon(self):
        # Configure Chrome options
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")
        options.add_argument(f"user-agent={user_agent}")

        # Set up the WebDriver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options = options)

        # Open Amazon Turkey
        self.driver.get("https://www.amazon.com.tr/")
        self.driver.execute_script("window.open('');")
        try:
            fakebar = ""
            fakesearchbar = ""
            fakesearchbar = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div/div[2]/form/div/div/input')
            fakebar = fakesearchbar.get_attribute("id")
        except NoSuchElementException:
            print("Element not found.")
        if fakebar == "nav-bb-search":
            self.driver.refresh()
            self.driver.implicitly_wait(5)           
        print(fakebar)
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get("https://tr.aliexpress.com/") 
    
    def search_amazon(self, menuWidget):
        self.driver.switch_to.window(self.driver.window_handles[0])
        
        # Get user input from the entry widget
        search_query = self.search_entry.text()
        if not search_query:
            print("Search query is empty. Nothing to search.")
            return  # Close the function if search query is empty
            
        # Find the search input field and enter the search query
        search_box = self.driver.find_element(By.ID, "twotabsearchtextbox")
        search_box.clear()  # Clear any existing text in the search box
        search_box.send_keys(search_query)  # Enter the search query
        search_box.send_keys(Keys.RETURN)  # Press Enter to submit the search

        # Wait for a few seconds to allow time for the search results to load
        self.driver.implicitly_wait(5)

        # Find product image URLs using XPath
        product_image_elements = self.driver.find_elements(By.XPATH, "/html/body/div[1]/div[1]/div[1]/div[1]/div/span[1]/div[1]/div/div//span/div/div/div//span/a/div/img")
        
        # Find product names using XPath
        product_name_elements = self.driver.find_elements(By.XPATH, "/html/body//div//div/div/div/div/span/div/div//h2/a/span")
        
        # Find product prices using XPath
        product_price_elements = self.driver.find_elements(By.XPATH, '/html/body//div//div/div/div/div/span/div/div//div//a/span//span[@class="a-price-whole"]')
        
        # Find product links using XPath
        product_id_elements = self.driver.find_elements(By.XPATH, "/html/body/div[1]/div[1]/div[1]/div[1]/div/span[1]/div[1]/div[not(@data-image-index='1')]")[2:]

        # Create empty lists to store product names, prices, and links
        products = []
        
        min_price_text = self.min_price_entry.text()
        max_price_text = self.max_price_entry.text()
        
        if min_price_text.strip() != '':
            try:
                min_price = int(min_price_text)
            except ValueError:
                return
        else:
            # Set a default minimum price or leave it as None
            min_price = None
        
        if max_price_text.strip() != '':
            try:
                max_price = int(max_price_text)
            except ValueError:
                return
        else:
            # Set a default maximum price or leave it as None
            max_price = None
        
        # Variables to track the number of valid products printed
        products_to_print = 5
        printed_count = 0
        i = 0
        
        # Append product information to corresponding lists
        while printed_count < products_to_print and i < len(product_price_elements):  # Display up to 5 search results
            product_price = product_price_elements[i].text.strip() + " TL"
            pricee = product_price.replace('.', '').replace(' TL', '')
            price = int(pricee)
            if (min_price is None or price >= min_price) and (max_price is None or price <= max_price):
                product_image_url = product_image_elements[i].get_attribute("src")
                product_name = product_name_elements[i].text.strip()
                product_id = product_id_elements[i].get_attribute("data-asin")
                product_link = "https://www.amazon.com.tr/dp/" + product_id
                products.append((product_image_url, product_name, product_price, product_link))
                printed_count += 1
            i += 1

        # Display search results in table
        self.display_results(products, menuWidget)
        
    def search_aliexpress(self, menuWidget):
        self.driver.switch_to.window(self.driver.window_handles[1])
        
        search_query = self.search_entry.text()
        if not search_query:
            print("Search query is empty. Nothing to search.")
            return  # Close the function if search query is empty
        
        # Find the search input field and enter the search query
        search_box = self.driver.find_element(By.ID, "search-words")
        search_box.clear()  # Clear any existing text in the search box
        search_box.send_keys(search_query)  # Enter the search query
        search_box.send_keys(Keys.RETURN)  # Press Enter to submit the search

        # Wait for a few seconds to allow time for the search results to load
        self.driver.implicitly_wait(5)
        
        page_height = self.driver.execute_script("return document.body.scrollHeight")
        current_position = 0
        scroll_increment = 1000
        while current_position < page_height:
            # Scroll down by the scroll increment
            self.driver.execute_script("window.scrollTo(0, {});".format(current_position))
            
            # Wait for a short time to allow content to load
            time.sleep(0.1)
            
            # Update the current scroll position
            current_position += scroll_increment
            
            # Update the page height in case content is dynamically loaded
            page_height = self.driver.execute_script("return document.body.scrollHeight")

        
        # Find product image URLs using XPath
        product_image_elements = self.driver.find_elements(By.XPATH, '/html/body/div[4]/div[1]/div/div[2]/div[2]/div/div/div/div/a/div[1]/div[1]/div[1]/div/img[1][@class="images--item--3XZa6xf"]')[:15]
        
        # Find product names using XPath
        product_name_elements = self.driver.find_elements(By.XPATH, '/html/body/div[4]/div[1]/div/div[2]/div[2]/div/div/div/div/a/div[2]/div[1]/h3')[:15]

        # Find product prices using XPath
        product_price_elements = self.driver.find_elements(By.XPATH, '//div[@class="multi--price-sale--U-S0jtj"]')[:15]
        
        # Find product links using XPath
        product_id_elements = self.driver.find_elements(By.XPATH, '/html/body/div[4]/div[1]/div/div[2]/div[2]/div/div/div/div/a[@class="multi--container--1UZxxHY cards--card--3PJxwBm search-card-item"]')[:15]

        # Create empty lists to store product names, prices, and links
        products = []
        
        min_price_text = self.min_price_entry.text()
        max_price_text = self.max_price_entry.text()
        
        if min_price_text.strip() != '':
            try:
                min_price = int(min_price_text)
            except ValueError:
                return
        else:
            # Set a default minimum price or leave it as None
            min_price = None
        
        if max_price_text.strip() != '':
            try:
                max_price = int(max_price_text)
            except ValueError:
                return
        else:
            # Set a default maximum price or leave it as None
            max_price = None
        
        # Variables to track the number of valid products printed
        products_to_print = 5
        printed_count = 0
        i = 0
        
        # Append product information to corresponding lists
        while printed_count < products_to_print and i < len(product_price_elements):  # Display up to 5 search results
            price_spans = product_price_elements[i].find_elements(By.TAG_NAME, 'span')
            complete_price = ''.join(span.text for span in price_spans)
            comma_index = complete_price.find(',')
            product_price = complete_price[:comma_index]  + " TL"
            pricee = product_price.replace('.', '').replace(' TL', '')
            price = int(pricee)
            if (min_price is None or price >= min_price) and (max_price is None or price <= max_price):
                product_image_url = product_image_elements[i].get_attribute("src")
                product_name = product_name_elements[i].text.strip()
                big_link = product_id_elements[i].get_attribute("href")
                nice_part = big_link.find('?algo')
                product_link = big_link[:nice_part]
                products.append((product_image_url, product_name, product_price, product_link))
                printed_count += 1
            i += 1

        # Display search results in table
        self.display_results(products, menuWidget)
    
    def menu_tracked_products(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.setAlignment(Qt.AlignTop)
        
        a_layout = QHBoxLayout()
        layout.addLayout(a_layout)
        
        amazon_button = QPushButton("Show Amazon Products")
        amazon_button.clicked.connect(lambda: self.display_database_results(widget, 'amazon'))
        a_layout.addWidget(amazon_button)
        amazon_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; border: none; border-radius: 10px; padding: 8px 20px; font-size: 14px; } QPushButton:hover { background-color: #0D47A1; }")
        
        aliexpress_button = QPushButton("Show Aliexpress Products")
        aliexpress_button.clicked.connect(lambda: self.display_database_results(widget, 'aliexpress'))
        a_layout.addWidget(aliexpress_button)
        aliexpress_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; border: none; border-radius: 10px; padding: 8px 20px; font-size: 14px; } QPushButton:hover { background-color: #0D47A1; }")

        
        widget.setLayout(layout)
        
        return widget
        
    def menu_search_products(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.setAlignment(Qt.AlignTop)
        
        # Create search label, entry, and button
        search_layout = QHBoxLayout()
        layout.addLayout(search_layout)

        self.comboBox = QComboBox()
        self.comboBox.addItems(['Amazon', 'Ali Express'])
        selectedOption = self.comboBox.currentText()
        search_layout.addWidget(self.comboBox)
        
        self.search_entry = QLineEdit()
        search_layout.addWidget(self.search_entry, 3)
        
        # Add min price input
        self.min_price_label = QLabel("Min Price:")
        search_layout.addWidget(self.min_price_label)
        self.min_price_label.setStyleSheet("QLabel { color: #505050; font-size: 14px; }")
        
        self.min_price_entry = QLineEdit()
        search_layout.addWidget(self.min_price_entry)
        self.min_price_entry.setPlaceholderText("Min Price")
        self.min_price_entry.setStyleSheet("QLineEdit { border: 2px solid #88CCF9; border-radius: 10px; padding: 6px 10px; font-size: 14px; } QLineEdit:focus { border-color: #2196F3; }")

        # Add max price input
        self.max_price_label = QLabel("Max Price:")
        search_layout.addWidget(self.max_price_label)
        self.max_price_label.setStyleSheet("QLabel { color: #505050; font-size: 14px; }")
        
        self.max_price_entry = QLineEdit()
        search_layout.addWidget(self.max_price_entry)
        self.max_price_entry.setPlaceholderText("Max Price")
        self.max_price_entry.setStyleSheet("QLineEdit { border: 2px solid #88CCF9; border-radius: 10px; padding: 6px 10px; font-size: 14px; } QLineEdit:focus { border-color: #2196F3; }")

        search_button = QPushButton("Search")
        search_button.clicked.connect(lambda: self.on_search_button_clicked(widget))
        search_layout.addWidget(search_button)
        
        self.search_entry.setStyleSheet("QLineEdit { border: 2px solid #88CCF9; border-radius: 10px; padding: 6px 10px; font-size: 14px; } QLineEdit:focus { border-color: #2196F3; }")
        search_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; border: none; border-radius: 10px; padding: 8px 20px; font-size: 14px; } QPushButton:hover { background-color: #0D47A1; }")
       
        widget.setLayout(layout)
        return widget
    
    def on_search_button_clicked(self, menuWidget):
        
        selectedOption = self.comboBox.currentText()
        
        # Example conditionals based on your logic
        if selectedOption == 'Amazon':
            self.search_amazon(menuWidget)
        elif selectedOption == "Ali Express":
            self.search_aliexpress(menuWidget)
            print("xd")
        else:
            print("No specific condition met, performing standard search")
    
    def menu_profile(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        widget.setLayout(layout)
        
        return widget
    
    def changePage(self, page, button):
        self.stackedWidget.setCurrentWidget(page)
        self.updateButtonStyles(button)
    
    
    def display_database_results(self, menu_widget, keyword):
        
        for i in reversed(range(menu_widget.layout().count())):
            item = menu_widget.layout().itemAt(i)
            if item.widget() and isinstance(item.widget(), QScrollArea):
                item.widget().deleteLater()
        
        # Create a scroll area for the database table
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Create a container widget for the database table
        table_container = QWidget()
        scroll_area.setWidget(table_container)
        table_container_layout = QVBoxLayout(table_container)
        table_container_layout.setContentsMargins(0, 0, 0, 0)  # Set margins to 0
        viewport = scroll_area.viewport()
        viewport.setStyleSheet("QScrollBar:vertical {"" border: none;"   " background: transparent;" " width: 14px;" " margin: 0px 2px 0px 3px;" "}" "QScrollBar::handle:vertical {" " background: #3b8cff;"  " border-radius: 4px;"   "}"  "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"  " border: none;"  " background: transparent;" "}"  "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {" " background: transparent;" "}")
        
        # Create table to display database results
        self.database_table_widget = ClickableSecondColumnTableWidget()
        header_view = CustomHeaderView(Qt.Horizontal)
        self.database_table_widget.setHorizontalHeader(header_view)
        self.database_table_widget.verticalHeader().setVisible(False)
        self.database_table_widget.setStyleSheet("QTableWidget { border: 1px solid #CCCCCC; border-radius: 10px; } ""QTableWidget::item { padding: 0px; } ""QTableWidget::item:selected { background-color: #E3F2FD; color: black; } ""QHeaderView::section { background-color: #2196F3; color: white; font-weight: bold; } "
        )
        # Set selection mode to SingleSelection
        self.database_table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        ROW_HEIGHT = 150
        # Add the database table widget to the container widget's layout
        table_container_layout.addWidget(self.database_table_widget)
        self.database_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.database_table_widget.verticalHeader().setDefaultSectionSize(ROW_HEIGHT)
        
        link_delegate = LinkDelegate()
        self.database_table_widget.setItemDelegateForColumn(3, link_delegate)

        # Set row and column count
        productss = self.fetch_products_from_database()
        products = self.filter_products_by_link(productss, keyword)
        
        self.database_table_widget.setRowCount(len(products))
        self.database_table_widget.setColumnCount(5)

        # Set headers
        self.database_table_widget.setHorizontalHeaderLabels(
            ["Image", "Name", "Price", "Link", "Delete product"]
        )

        for row, product in enumerate(products):
            for col, data in enumerate(product.values()):  # Iterate over values of the dictionary
                item = QTableWidgetItem()
                if col == 0:  # If it's the image column
                    widget = ImageWidget(data)  # Create a custom widget for the image
                    self.database_table_widget.setCellWidget(row, col, widget)
                else:
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.TextWordWrap)  # Enable word wrap for multiline text
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    self.database_table_widget.setItem(row, col, item)

            # Create delete button
            delete_button = QPushButton("Delete")
            delete_button.setObjectName("delete_button")  # Set object name for styling
            delete_button.setStyleSheet(
                "QPushButton#delete_button { background-color: #FF6347; color: white; border: none; border-radius: 10px; padding: 8px 20px; font-size: 15px; } "
                "QPushButton#delete_button:hover { background-color: #8B0000; } "
                "QPushButton#delete_button { padding-left: 10px; padding-right: 10px; }"
            )
            # Ensure to get the correct product ID
            delete_button.clicked.connect(lambda _, name=product['product_name']: self.delete_product(name))
            self.database_table_widget.setCellWidget(row, 4, delete_button)  # Adding button to the last column
        
        layout = menu_widget.layout()
        layout.addWidget(scroll_area)
        
    def filter_products_by_link(self, productss, keyword):
        # Filter products to only include those with 'amazon' in the product_link
        return [product for product in productss if keyword in product['product_link']]

    def display_results(self, products, menuWidget):
        
        for i in reversed(range(menuWidget.layout().count())):
            item = menuWidget.layout().itemAt(i)
            if item.widget() and isinstance(item.widget(), ClickableSecondColumnTableWidget):
                item.widget().deleteLater()
        
        table_widget = ClickableSecondColumnTableWidget()
        header_view = CustomHeaderView(Qt.Horizontal)
        table_widget.setHorizontalHeader(header_view)
        table_widget.verticalHeader().setVisible(False)
        
        # Set selection mode to SingleSelection
        table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        
        table_widget.setStyleSheet(
                "QTableWidget { border: 1px solid #CCCCCC; border-radius: 10px; } "
                "QTableWidget::item { padding: 0px; } "
                "QTableWidget::item:selected { background-color: #E3F2FD; color: black; } "
                "QHeaderView::section { background-color: #2196F3; color: white; font-weight: bold; } "
                    )
           
        # Re-enable automatic resizing
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_widget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        link_delegate = LinkDelegate()
        table_widget.setItemDelegateForColumn(3, link_delegate)
        
        # Clear previous search results
        table_widget.clear()

        # Set row and column count
        table_widget.setRowCount(len(products))
        table_widget.setColumnCount(5)

        # Set headers
        table_widget.setHorizontalHeaderLabels(["Image","Name", "Price", "Link", "Track"])

        # Display product information in table
        for row, product in enumerate(products):
            for col, data in enumerate(product):
                item = QTableWidgetItem()
                if col == 0:  # If it's the image column
                    widget = ImageWidget(data)  # Create a custom widget for the image
                    table_widget.setCellWidget(row, col, widget)
                    
                else:
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.TextWordWrap)  # Enable word wrap for multiline text
                    item.setTextAlignment(Qt.AlignCenter)    
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    table_widget.setItem(row, col, item)
            
            track_button = QPushButton("Track Product")
            track_button.setObjectName("track_button")  # Set object name for styling
            track_button.clicked.connect(lambda _, row=row: self.track_product(products[row], table_widget))
            track_button.setStyleSheet("QPushButton#track_button { background-color: #6FC2F9; color: white; border: none; border-radius: 10px; padding: 8px 20px; font-size: 15px; } QPushButton#track_button:hover { background-color: #0D47A1; } QPushButton#track_button { padding-left: 10px; padding-right: 10px; }")
            table_widget.setCellWidget(row, 4, track_button)  # Adding button to the last column
        layout = menuWidget.layout()
        layout.addWidget(table_widget)

    def track_product(self, product, table_widget):
        # Extract product information
        username = self.username
        product_image_link, product_name, product_price, product_link = product

        # Insert product information into the database
        query = "INSERT INTO Products (username, product_image_link, product_name, product_price, product_link) VALUES (%s, %s, %s, %s, %s)"
        values = (username, product_image_link, product_name, product_price, product_link)
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
                print("Product tracked successfully:", values)
                
                # Find the index of the clicked product in the table
            for row in range(table_widget.rowCount()):
                for col in range(table_widget.columnCount()):
                    item = table_widget.item(row, col)
                    if item and item.text() == product_name:
                        # Get the button widget from the cell
                        button_widget = table_widget.cellWidget(row, 4)
                        if button_widget:
                            # Change button color to green
                            button_widget.setStyleSheet("background-color: #4CAF50; color: white; border: none; border-radius: 10px; padding: 8px 20px; font-size: 15px;")
                            # Change button text to "Tracked"
                            button_widget.setText("Tracked")
                            # Disconnect the signal-slot connection to prevent further clicks
                            button_widget.clicked.disconnect()
                
                
        except pymysql.Error as e:
            print("Error tracking product:", e)

    
    def fetch_products_from_database(self):
        # Fetch products from the database for the current user
        username = self.username
        query = "SELECT product_image_link, product_name, product_price, product_link, id FROM Products WHERE username = %s"
        values = (username,)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                return cursor.fetchall()
        except pymysql.Error as e:
            print("Error fetching products from the database:", e)
            return []

    def delete_product(self, product_name):
        # Delete product from the database based on its name
        query = "DELETE FROM Products WHERE product_name = %s"
        values = (product_name,)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
                print("Product deleted successfully")
                # Refresh the table to reflect the changes
        except pymysql.Error as e:
            print("Error deleting product:", e)
                    
    def updateButtonStyles(self, activeButton):
        for button in self.buttons:
            if button == activeButton:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50; /* Green */
                        border: none;
                        color: white;
                        padding: 15px 32px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                        margin: 4px 2px;
                        border-radius: 12px;
                        transition-duration: 0.4s;
                        cursor: pointer;
                    }
                    QPushButton:hover {
                        background-color: white;
                        color: black;
                        border: 2px solid #4CAF50;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #D3D3D3; /* Light Gray */
                        border: none;
                        color: black;
                        padding: 15px 32px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                        margin: 4px 2px;
                        border-radius: 12px;
                        transition-duration: 0.4s;
                        cursor: pointer;
                    }
                    QPushButton:hover {
                        background-color: #A9A9A9; /* Dark Gray */
                        color: black;
                        border: 2px solid #4CAF50;
                    }
                """)
    
    def logout(self):
        # Delete JSON file storing login data
        if os.path.exists("remember.json"):
            os.remove("remember.json")
        
        # Perform logout actions here, such as closing the window or opening the login window
        self.close()  # Close the main window
        
       
