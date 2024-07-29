from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

# Sets up and returns a Chrome WebDriver instance.
def setup_driver():
    driver = webdriver.Chrome()
    driver.get("https://www.mcxindia.com/market-data/spot-market-price")
    return driver

# Clicks a button on the web page.
def click_button(driver, by, value):
    try:
        button = driver.find_element(by, value)
        button.click()
        sleep(1)
    except Exception as e:
        print(f"An error occurred while clicking a button: {e}")

# Selects an option from a dropdown menu.
def select_option(driver, by, value, option_xpath):
    try:
        dropdown = driver.find_element(by, value)
        dropdown.click()
        sleep(1)
        option = driver.find_element(By.XPATH, option_xpath)
        option.click()
        sleep(1)
    except Exception as e:
        print(f"An error occurred while selecting an option: {e}")

# Sets a date in the date picker.
def set_date(driver, date_field_id, year, month, day):
    try:
        date_field = driver.find_element(By.ID, date_field_id)
        date_field.click()
        sleep(1)
        year_option = driver.find_element(By.XPATH, f'//select[@class="datepick-month-year"][@title="Change the year"]//option[text()="{year}"]')
        year_option.click()
        sleep(1)
        month_option = driver.find_element(By.XPATH, f'//select[@class="datepick-month-year"][@title="Change the month"]//option[text()="{month}"]')
        month_option.click()
        sleep(1)
        day_option = driver.find_element(By.XPATH, f'//a[text()="{day}"]')
        day_option.click()
        sleep(1)
    except Exception as e:
        print(f"An error occurred while setting the date: {e}")

def get_table_data(driver):
    table_data = []
    try:
        val = int(driver.find_element(By.ID, 'pagerCount').text)
        for i in range(val):
            xpath = f"//select[@id='ddlPagerArchive']//option[@value='{i+1}']"
            driver.find_element(By.XPATH, xpath).click()
            table = driver.find_element(By.ID, 'tblArchive')
            # Extracting table headers
            headers = []
            for th in table.find_elements(By.XPATH, './/thead/tr/th'):
                headers.append(th.text.strip())
            for row in table.find_elements(By.XPATH, './/tbody/tr'):
                cells = row.find_elements(By.XPATH, './td')
                # Extracting data for each row
                data = {}
                for i in range(len(cells)):
                    header = headers[i]
                    data[header] = cells[i].text.strip()
                table_data.append(data)
    except Exception as e:
        print(f"An error occurred while retrieving table data: {e}")
    return table_data

def store_data_in_panda(data):
    df = pd.DataFrame(data)
    # Count the total number of rows
    total_rows = len(df)
    print(f"Total number of rows: {total_rows}")
    # Find the date with the highest "Spot Price (Rs.)"
    df['Spot Price (Rs.)'] = df['Spot Price (Rs.)'] .str.replace(',', '').astype(float)
    max_price_row = df.loc[df['Spot Price (Rs.)'].idxmax()]
    max_price_date = max_price_row['Date']
    print(f"Date with the highest Spot Price (Rs.): {max_price_date}")
    # Save data to Excel
    filename = 'raw-data.xlsx'
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Raw Data', index=False)

def get_table_and_data():
    driver = setup_driver()
    # Clicking recent button
    click_button(driver, By.CLASS_NAME, 'today')
    # Selecting gold button
    select_option(driver, By.XPATH,
                  '//*[@id="ctl00_cph_InnerContainerRight_C004_ddlSymbols_Input"]',
                  '//*[@id="ctl00_cph_InnerContainerRight_C004_ddlSymbols_DropDown"]/div/ul/li[18]')
    # Selecting all button
    select_option(driver, By.XPATH,
                  '//*[@id="ctl00_cph_InnerContainerRight_C004_ddlLocationArchive_Input"]',
                  '//*[@id="ctl00_cph_InnerContainerRight_C004_ddlLocationArchive_DropDown"]/div/ul/li[1]')
    # Selecting session 2
    select_option(driver, By.XPATH, '//*[@id="cph_InnerContainerRight_C004_ddlSession"]',
                  '//*[@id="cph_InnerContainerRight_C004_ddlSession"]/option[3]')
    # Selecting from date
    set_date(driver, 'txtFromDate', '2023', 'November', '1')
    # Selecting to date
    set_date(driver, 'txtToDate', '2024', 'January', '24')
    # Clicking show button
    click_button(driver, By.XPATH, '//*[@id="commoditywise"]/div[4]/div[3]')
    # Get table data
    table_data = get_table_data(driver)
    driver.quit()
    return table_data

def main():
    table_data = get_table_and_data()
    print('----------------------')
    print('Data Extraction is Done')
    print('----------------------')

if __name__ == "__main__":
    main()
