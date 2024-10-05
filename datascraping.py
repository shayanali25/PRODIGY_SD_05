import requests
from bs4 import BeautifulSoup
import csv
import tkinter as tk
from tkinter import messagebox
import time
import random

# Function to scrape product data
def get_product_data(page_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    for _ in range(3):  # Retry mechanism, try 3 times
        try:
            response = requests.get(page_url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            break
        except requests.exceptions.HTTPError as e:
            if response.status_code == 503:
                time.sleep(random.uniform(5, 10))  # Random delay between 5-10 seconds
                continue  # Retry if the error was 503
            else:
                messagebox.showerror("Error", f"HTTP error occurred: {e}")
                return []
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch the page: {e}")
            return []

    if response.status_code != 200:
        messagebox.showerror("Error", "Failed to fetch the page after retries.")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    # Change the tags/class names according to the site you are scraping
    product_list = soup.find_all('div', class_='s-main-slot s-result-list s-search-results sg-row')

    for product in product_list:
        try:
            product_name = product.h2.a.text.strip()
        except AttributeError:
            product_name = "No product name"

        try:
            price = product.find('span', class_='a-price-whole').text.strip()
        except AttributeError:
            price = "No price"

        try:
            rating = product.find('span', class_='a-icon-alt').text.strip()
        except AttributeError:
            rating = "No rating"

        products.append([product_name, price, rating])

    return products

# Function to save products to a CSV file
def save_to_csv(products):
    if not products:
        messagebox.showwarning("No Data", "No products found on the page.")
        return

    with open('scraped_products.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Product Name', 'Price', 'Rating'])
        writer.writerows(products)

    messagebox.showinfo("Success", "Product data has been saved to 'scraped_products.csv'.")

# GUI Application for user-driven scraping
def scrape_products():
    url = url_entry.get().strip()

    if not url:
        messagebox.showwarning("Input Error", "Please enter a valid URL.")
        return

    scrape_button.config(state=tk.DISABLED)
    status_label.config(text="Scraping in progress...")

    products = get_product_data(url)

    if products:
        save_to_csv(products)

    status_label.config(text="")
    scrape_button.config(state=tk.NORMAL)

# Create the GUI window
app = tk.Tk()
app.title("Product Scraper")

# URL Entry
url_label = tk.Label(app, text="Enter Product Page URL:")
url_label.grid(row=0, column=0, padx=10, pady=10)

url_entry = tk.Entry(app, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

# Scrape button
scrape_button = tk.Button(app, text="Scrape Products", command=scrape_products)
scrape_button.grid(row=1, column=1, padx=10, pady=10)

# Status Label
status_label = tk.Label(app, text="")
status_label.grid(row=2, column=1, padx=10, pady=10)

# Run the GUI
app.mainloop()
