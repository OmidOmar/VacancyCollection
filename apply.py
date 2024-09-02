import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime

# Path to the ChromeDriver executable
chrome_driver_path = "/Users/omidomar/Documents/Python/LinkedIN/CD/chromedriver"

# Path to the CSV file containing URLs
get_file=user_input = input("CSV File name: ")
csv_file_path = "/Users/omidomar/Documents/Python/LinkedIN/"+get_file+'.csv'

# User credentials
email = input("Email: ")  # Replace with your email
password = input("Password: ")  # Replace with your password

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Initialize the Chrome WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Flag to check if privacy prompt has been handled
privacy_prompt_handled = False

# Data storage
applied_details = []
manually_checked = []
ignored_details = []
error_details = []

def handle_privacy_prompt():
    global privacy_prompt_handled
    try:
        print("Checking for privacy prompt.")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ccmgt_explicit_accept"))
        )
        privacy_prompt = driver.find_element(By.ID, "ccmgt_explicit_accept")
        if privacy_prompt.is_displayed():
            print("Privacy prompt found. Accepting privacy prompt.")
            driver.execute_script("arguments[0].scrollIntoView(true);", privacy_prompt)
            time.sleep(1)  # Allow time for scrolling
            privacy_prompt.click()
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element(privacy_prompt)
            )
            print("Privacy prompt accepted and no longer visible.")
            privacy_prompt_handled = True
    except Exception as e:
        print(f"No privacy prompt found or failed to accept: {e}")

def login():
    try:
        # Open the sign-in page
        sign_in_url = "https://www.totaljobs.com/candidate/login?ReturnUrl=/"
        print(f"Opening sign-in page: {sign_in_url}")
        driver.get(sign_in_url)
        
        # Wait for the page to load
        print("Waiting for the sign-in page to load.")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Sign-in page loaded.")
        
        # Enter email
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "stepstone-form-element-12"))
        )
        print("Entering email.")
        email_input.send_keys(email)

        # Enter password
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "stepstone-form-element-16"))
        )
        print("Entering password.")
        password_input.send_keys(password)

        # Click the login button
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='login-submit-btn']"))
        )
        print("Clicking login button.")
        login_button.click()

        # Wait for login to complete
        print("Waiting for login to complete.")
        WebDriverWait(driver, 20).until(
            EC.url_changes(sign_in_url)
        )
        print("Logged in successfully.")

    except Exception as e:
        print(f"An error occurred during login: {e}")

def click_apply_button():
    try:
        print("Finding the apply button.")
        apply_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@data-testid='harmonised-apply-button']"))
        )
        print("Button found.")
        
        # Ensure the button is in view and clickable
        driver.execute_script("arguments[0].scrollIntoView(true);", apply_button)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='harmonised-apply-button']"))
        )
        print("Button is clickable.")
        
        # Try clicking using JavaScript as a fallback
        try:
            apply_button.click()
            print("Button clicked.")
        except Exception as click_exception:
            print(f"Normal click failed: {click_exception}. Trying JavaScript click.")
            driver.execute_script("arguments[0].click();", apply_button)
            print("Button clicked using JavaScript.")
        
    except Exception as e:
        print(f"Failed to click the apply button: {e}")

def process_url(url, first_link=False):
    global applied_details, manually_checked, ignored_details, error_details
    try:
        print(f"Opening URL: {url}")
        driver.get(url)
        
        # Wait for the page to load
        print("Waiting for the page to load.")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Page loaded.")
        
        # Handle privacy prompt only for the first link
        if first_link:
            print("Handling privacy prompt.")
            handle_privacy_prompt()

        # Click the apply button
        print("Clicking the apply button.")
        click_apply_button()

        # Wait for the action to complete
        print("Waiting for the action to complete.")
        time.sleep(2)  # Adjust the sleep time if needed
        print("Action completed.")

        # Check if a new tab was opened
        print("Checking if a new tab has opened.")
        original_window = driver.current_window_handle
        all_windows = driver.window_handles

        if len(all_windows) > 1:
            print("A new tab was opened.")
            # Switch to the new tab and close it
            for window in all_windows:
                if window != original_window:
                    driver.switch_to.window(window)
                    driver.close()
                    print("New tab closed.")
                    break
            # Switch back to the original window
            driver.switch_to.window(original_window)

        # Check if the URL contains specific segments
        current_url = driver.current_url
        if '/?conversationUuid=' in current_url:
            print("URL contains '/?conversationUuid='. Storing job details in manually checked CSV.")
            manually_checked.append((url, 'Manually Checked'))
        elif 'application/dynamic-apply?workflow=SingleApply' in current_url:
            print("URL contains 'application/dynamic-apply?workflow=SingleApply'. Storing job details in manually checked CSV.")
            manually_checked.append((url, 'Manually Checked'))
        elif 'dynamic-apply?workflow=ApplyExpress' in current_url:
            print("URL contains 'dynamic-apply?workflow=ApplyExpress'. Checking for 'Send application' button.")
            try:
                send_application_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='sendApplication']"))
                )
                print("Send application button found and clickable. Clicking it.")
                send_application_button.click()
                print("Send application button clicked.")
                
                # Wait for confirmation
                WebDriverWait(driver, 10).until(
                    EC.url_contains('application/confirmation?applicationId')
                )
                print("Confirmation URL found. Storing job details in applied details CSV.")
                applied_details.append((url, 'Applied', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
            except Exception as e:
                print(f"'Send application' button not found or not clickable: {e}")
                error_details.append((url, 'Error', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        else:
            print("URL does not match any expected patterns. Ignoring.")
            ignored_details.append((url, 'Ignored', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    except Exception as e:
        print(f"An error occurred while processing the URL {url}: {e}")
        error_details.append((url, 'Error', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

try:
    # Log in first
    login()

    # Read URLs from the CSV file
    print("Reading URLs from the CSV file.")
    df = pd.read_csv(csv_file_path)
    print("Column names in the CSV file:")
    print(df.columns.tolist())  # Print columns to debug

    # Adjust the column name based on the output of the above print statement
    urls = df['Link'].tolist()  # Column name for URLs is 'Link'

    first_link = True
    for url in urls:
        process_url(url, first_link)
        first_link = False  # Set to False after the first URL is processed

finally:
    # Save applied details to CSV
    applied_details_df = pd.DataFrame(applied_details, columns=['URL', 'Status', 'Applied Date and Time'])
    applied_details_df.to_csv('/Users/omidomar/Documents/Python/LinkedIN/Applied_Details.csv', index=False)
    
    # Save manually checked details to CSV
    manually_checked_df = pd.DataFrame(manually_checked, columns=['URL', 'Status'])
    manually_checked_df.to_csv('/Users/omidomar/Documents/Python/LinkedIN/Manually_Checked_Details.csv', index=False)
    
    # Save ignored and error details to CSV
    ignored_details_df = pd.DataFrame(ignored_details, columns=['URL', 'Status', 'Date and Time'])
    ignored_details_df.to_csv('/Users/omidomar/Documents/Python/LinkedIN/Ignored_Details.csv', index=False)
    
    error_details_df = pd.DataFrame(error_details, columns=['URL', 'Status', 'Date and Time'])
    error_details_df.to_csv('/Users/omidomar/Documents/Python/LinkedIN/Error_Details.csv', index=False)

    # Write summary to a text file
    summary_file_path = '/Users/omidomar/Documents/Python/LinkedIN/summary.txt'
    with open(summary_file_path, 'a') as summary_file:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary_file.write(f"\nSummary as of {now}:\n")
        summary_file.write(f"Jobs Applied: {len(applied_details)}\n")
        summary_file.write(f"Jobs Manually Checked: {len(manually_checked)}\n")
        summary_file.write(f"Jobs Ignored: {len(ignored_details)}\n")
        summary_file.write(f"Errors Encountered: {len(error_details)}\n")

    # Prompt user to decide whether to exit the program
    user_input = input("Do you want to exit the program? (y/n): ").strip().lower()
    if user_input == 'y':
        print("Exiting the program.")
    else:
        print("Program will not exit. The browser will remain open.")
    
    # Close the browser
    print("Closing the browser.")
    driver.quit()
    print("Browser closed.")