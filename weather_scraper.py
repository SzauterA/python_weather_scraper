from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import os, re
from datetime import datetime


#setting up the driver with selenium and chromedriver
def driver_setup():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument('--log-level=1')

    chromedriver_path = os.getenv('CHROMEDRIVER_PATH', 'C:/chromedriver-win64/chromedriver.exe')
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

#getting and validating input from the user
def get_city():
    while True:
        city = input("Enter city name or 'q' to exit: ").strip()
        if re.match(r"^[a-zA-ZÀ-ÿ' -]+$", city):
            return city
        else:
            print("Invalid input. Please enter a valid city name.")

#finding the city and getting the current weather data
def get_data(driver, city):
    url = 'https://openweathermap.org/find'
    try:
        driver.get(url)
        print(f"Navigating to {url} to get weather data...")
        time.sleep(2)

        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(city)
        search_box.send_keys(Keys.RETURN)
        print(f"Searching for city: {city}")
        time.sleep(2)

        forecast_list = driver.find_element(By.ID, "forecast_list_ul")
        city_link = forecast_list.find_element(By.TAG_NAME, "a")
        city_name = city_link.text.strip()
        description_element = forecast_list.find_element(By.CSS_SELECTOR, "b > i")
        description = description_element.text.strip()
        temperature = forecast_list.find_element(By.CLASS_NAME, "badge-info").text.strip()

        print(f"City: {city_name}")
        print(f"Description: {description}")
        print(f"Temperature: {temperature}")
        return city_link
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

#getting the forecast data for the next 8 days
def get_forecast(driver, city_link):
    try:
        city_link.click()
        time.sleep(2)

        print("Getting forecast data...")
        forecast_table = driver.find_element(By.CLASS_NAME, "day-list")
        rows = forecast_table.find_elements(By.TAG_NAME, "li")
        forecast_data = []
        for row in rows:
            date = row.find_element(By.TAG_NAME, "span").text.strip()
            temperature = row.find_element(By.CLASS_NAME, "day-list-values").find_element(By.TAG_NAME, "span").text.strip()
            description = row.find_element(By.CLASS_NAME, "sub").text.strip()

            forecast_data.append({
                "Date": date,
                "Temperature": temperature,
                "Description": description
            })

        print("Forecast data for the next 8 days:")
        for data in forecast_data:
            print(f"{data['Date']}: {data['Temperature']} - {data['Description']}")
        return forecast_data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
#saving the forecast data to a .csv file with pandas  
def save(forecast_data):
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    file_name = f"weather_forecast_{stamp}.csv"
    file_path = os.path.join(cur_dir, file_name)
    df = pd.DataFrame(forecast_data)
    df.to_csv(file_path, index=False, encoding="utf-8")
    print(f'Forecast data saved successfully to {file_path}.')  

#helper function to validate user input for Yes/No questions
def get_yes_no_input(prompt):
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ['yes', 'y']:
            return True
        elif user_input in ['no', 'n']:
            return False
        else:
            print("Invalid input. Please only choose between yes or no.")  

#main logic of the program
def main():
    print('Welcome to the Weather Scraper!')
    driver = driver_setup()
    try:
        while True:
            city = get_city()
            if city == 'q':
                print("Goodbye!")
                break
            city_link = get_data(driver, city)
            if city_link is None:
                print("Failed to get data. Please try again.")
                continue
            if city_link:
                if get_yes_no_input("Do you want to see the 8 day forecast? Yes/No: "):
                    forecast_data = get_forecast(driver, city_link)
                    if forecast_data:
                        if get_yes_no_input("Do you want to save the data to a .csv file? Yes/No: "):
                            save(forecast_data)              
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
