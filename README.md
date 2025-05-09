# 📉 Price Tracker System
A price tracking system that allows users to search for products on Amazon and Alibaba and add them to a watchlist. The system automatically scans product prices using Python and Selenium, detects price drops, and sends email notifications to users. This project provides practical experience with real-time data fetching, email notification systems, and user interactions.

## 📌 Features

- **Product Search:**
Users can search for products on Amazon and Alibaba.

- **Watchlist:**
Users can add desired products to a watchlist for price tracking.

- **Automated Price Scanning:**
Python and Selenium are used to automatically scrape product prices from the websites.

- **Price Drop Notifications:**
When a price drop is detected, the system sends an email notification to the user.

- **Real-Time Data:**
Continuously fetches up-to-date pricing information.

- **User Interaction:**
Offers a practical interface for product search, list management, and notifications.

## 🧠 How It Works
- **Product Search & Watchlist Management:**
Users search for products and add items of interest to a personalized watchlist.

- **Automated Price Scanning:**
A scheduled Python script uses Selenium to scrape current product prices from Amazon and Alibaba.

- **Price Monitoring:**
The system compares the latest prices with previous records, detecting any significant drops.

- **Email Notification:**
When a price drop is confirmed, an email alert is sent to the registered user with details of the new price.

- **Real-Time Updates:**
The system updates the product pricing data in near-real-time, ensuring users are always informed with current market conditions.

## 📊 Dataset & Tools
- **Web Scraping:**
Implemented with Python and Selenium for dynamic scraping of product pages.

- **Data Persistence:**
Utilizes a database to store product information, historical prices, and user watchlists.

- **Email Service:**
Integrated with an SMTP server (such as SendGrid or Gmail SMTP) for sending notifications.


