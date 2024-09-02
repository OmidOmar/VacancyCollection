import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Specify the full path to your chromedriver
chrome_driver_path = "/Users/omidomar/Documents/Python/VacancyCollection/CD/chromedriver"
csv_file_path = 'database.csv'

# Create a service object for chromedriver
service = Service(chrome_driver_path)

# Initialize the Chrome WebDriver with the service
print("Initializing Chrome WebDriver.")
driver = webdriver.Chrome(service=service)

# Open TotalJobs website
print("Opening TotalJobs website.")
driver.get("https://www.totaljobs.com/")

# Wait for and accept the privacy policy if it appears
print("Handling privacy policy prompt.")
try:
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "ccmgt_explicit_accept"))
    )
    accept_button.click()
    print("Privacy policy accepted.")
except Exception as e:
    print(f"No privacy policy prompt found or failed to click: {e}")

# Enter job title and location
print("Entering job title and location.")
search_keyword = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Job title, skill or company']"))
)
search_keyword.send_keys("database")

search_location = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Town, city or postcode']"))
)
search_location.clear()
search_location.send_keys("London")

search_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-at='searchbar-search-button']"))
)
search_button.click()
print("Search button clicked.")

# Open CSV file for writing

print(f"Opening CSV file for writing: {csv_file_path}.")
with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Job Number', 'Job Title', 'Company', 'Location', 'Salary', 'Link'])

    # Collect jobs
    jobs_collected = 0
    total_jobs_needed = 2000

    while jobs_collected < total_jobs_needed:
        print(f"Collecting jobs from page {jobs_collected // 10 + 1}.")
        
        # Wait for the results page to load
        time.sleep(5)  # Adjust the sleep time if needed

        # Extract job listings from the results page
        jobs = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="job-card-content"]')

        # Loop through each job and extract relevant information
        for job in jobs:
            if jobs_collected >= total_jobs_needed:
                break

            try:
                # Extract job title
                title_element = job.find_element(By.CSS_SELECTOR, 'h2[data-genesis-element="BASE"] a[data-testid="job-item-title"]')
                title = title_element.text
                link = title_element.get_attribute('href')

                # Extract company name
                company_element = job.find_element(By.CSS_SELECTOR, 'span[data-at="job-item-company-name"]')
                company = company_element.text

                # Extract location
                location_element = job.find_element(By.CSS_SELECTOR, 'span[data-at="job-item-location"]')
                location = location_element.text

                # Extract salary
                salary_element = job.find_element(By.CSS_SELECTOR, 'span[data-at="job-item-salary-info"]')
                salary = salary_element.text if salary_element else 'N/A'

                # Write job details to CSV
                csv_writer.writerow([jobs_collected + 1, title, company, location, salary, link])
                jobs_collected += 1

                # Print job details
                print(f"Job Number: {jobs_collected}")
                print(f"Job Title: {title}")
                print(f"Company: {company}")
                print(f"Location: {location}")
                print(f"Salary: {salary}")
                print(f"Link: {link}")
                print('-' * 40)

            except Exception as e:
                print(f"Error extracting job info: {e}")

        # Navigate to the next page
        try:
            print(f"Current URL before clicking 'Next': {driver.current_url}")

            # Update the selector for the "Next" button
            next_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//li[@class='res-1b3es54']//a[@aria-label='Next']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)  # Scroll to the button if needed
            next_button.click()
            print("Moved to the next page.")

            # Wait for new page content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="job-card-content"]'))
            )
            print(f"Current URL after clicking 'Next': {driver.current_url}")
        except Exception as e:
            print(f"Error navigating to next page: {e}")
            break  # Exit loop if no more pages are available

    # Print summary
    print(f"Total jobs collected: {jobs_collected}")

# Close the WebDriver
print("Closing the WebDriver.")
driver.quit()

print(f"Job data has been saved to {csv_file_path}.")
