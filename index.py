from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from datetime import datetime
import pandas as pd

login_url = 'https://www.marketwatch.com/client/login'
username = 'khamid1@unb.ca'
password = '2023financeclub'
url = 'https://www.marketwatch.com/games/unb-paper-trading-competition/rankings'

def scrape_leaderboard(url, login_url, username, password):
    # Set up headless browser
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    #Navigate to the login page
    driver.get(login_url)

    time.sleep(5)

    #Use JavaScript to set the value for username
    driver.execute_script(
        "document.getElementById('username').value = arguments[0];", 
        username
    )

    time.sleep(5)

    #Use Javascript to click continue button
    continue_button_selector = "#basic-login > div:nth-child(1) > form > div:nth-child(2) > div:nth-child(6) > div.sign-in.hide-if-one-time-linking > button.solid-button.continue-submit.new-design"
    driver.execute_script(f"document.querySelector('{continue_button_selector}').click();")

    time.sleep(5)

    #Use JavaScript to set the value for password
    driver.execute_script(
        "document.getElementById('password-login-password').value = arguments[0];", 
        password
    )
    
    print("-_------------------SUCCESS---------------_-")
    
    #Use Javascript to login
    login_button_selector = "#password-login > div > form > div > div:nth-child(5) > div.sign-in.hide-if-one-time-linking > button"
    driver.execute_script(f"document.querySelector('{login_button_selector}').click();")
    
    time.sleep(5)

    # Navigate to the competition URL
    driver.get(url)

    time.sleep(5)

    #Use BeautifulSoup to parse the page content
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    #Find ranking table
    table = soup.find('table', {'class': 'table table--primary ranking'})
    
    time.sleep(5)

    #click 'next page' to go to page 2 of the rankings
    next_page_button_selector = "#maincontent > div.content-region.region--primary > div.column.column--primary > div.element.element--table.leaders > div.pagination > a.link.align--right.j-next"
    driver.execute_script(f"document.querySelector('{next_page_button_selector}').click();")
    time.sleep(10)

    #get table 2
    soup2 = BeautifulSoup(driver.page_source, 'html.parser')
    table2 = soup2.find('table', {'class': 'table table--primary ranking'})
    
    tables = [table, table2]
    all_rows = []
    # Process each table, extracting 
    for table in tables:
        if table:
            # Extract headers
            headers = [th.get_text().strip() for th in table.find_all('th')]
            headers = headers[1:]

            # Extract rows
            for tr in table.find_all('tr')[1:]:
                cells = tr.find_all('td')
                row_data = [cell.get_text().strip() for cell in cells]
                row_data = row_data[1:]
                all_rows.append(row_data)
        else:
            print("Table not found")
    df = pd.DataFrame(all_rows, columns=headers)
    print(df)
    # Close the browser
    driver.quit()
    print("-----------------------scrapedDF--------------------\n", df)
    return df


def compare(lastWeek: pd.DataFrame, thisWeek: pd.DataFrame):
    #Intersect the dataframes on the Name column
    merged = pd.merge(lastWeek, thisWeek, on="Name", suffixes=("-last", "-this"))
    #converting strings to numerical values, formatting with regular expression
    merged["Net Worth-last"] = merged["Net Worth-last"].str.replace('[$,]', '', regex=True).astype(float)
    merged["Net Worth-this"] = merged["Net Worth-this"].str.replace('[$,]', '', regex=True).astype(float)
    #Calculating percentage change
    merged['Percentage Change'] = ((merged['Net Worth-this'] - merged['Net Worth-last']) / merged['Net Worth-last']) * 100
    merged = merged.sort_values(by="Percentage Change", ascending=False)
    return merged
    


currentDate = datetime.now().strftime("%m-%d-%y")
thisWeek = scrape_leaderboard(url, login_url, username, password)
print("-----------------------thisWeek--------------------\n", thisWeek)
lastWeek = pd.read_csv("lastWeek.csv")
print("-----------------------LastWeek--------------------\n", lastWeek)
merged = compare(lastWeek, thisWeek)
#drop unnecessary fields from the merged df
merged = merged.drop(columns=["Last-last", "Trades-last", "Total Returns-last", "Last-this", "Trades-this", "Total Returns-this"])
print("-----------------------merged--------------------\n", merged)
merged.to_csv(f"weeklyMovers/weeklyMovers-{currentDate}.csv", index=False)
thisWeek.to_csv("lastWeek1.csv", index=False)



