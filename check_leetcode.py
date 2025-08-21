import json
import os
import google.generativeai as genai
import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import subprocess
import time
import psutil
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def kill_chrome_processes():
    """Kill all Chrome processes to ensure clean startup."""
    print("Terminating existing Chrome processes...")
    try:
        # Use taskkill on Windows for more reliable process termination
        subprocess.run(['taskkill', '/f', '/im', 'chrome.exe'], 
                      capture_output=True, check=False)
        subprocess.run(['taskkill', '/f', '/im', 'chromedriver.exe'], 
                      capture_output=True, check=False)
        time.sleep(3)
        print("Chrome processes terminated.")
    except Exception as e:
        print(f"Note: {e}")

def get_leetcode_cookies_method1(username, password):
    """Method 1: Simple fresh Chrome instance with better login handling."""
    print("Method 1: Starting fresh Chrome instance...")
    
    kill_chrome_processes()
    
    options = uc.ChromeOptions()
    # Remove problematic arguments and keep it simple
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    driver = None
    try:
        # Use version_main parameter to avoid compatibility issues
        driver = uc.Chrome(options=options, version_main=None)
        driver.maximize_window()
        
        print("Navigating to LeetCode login page...")
        driver.get("https://leetcode.com/accounts/login/")
        time.sleep(3)
        
        # Wait for the page to load completely
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Try multiple selectors for username field
        username_field = None
        username_selectors = [
            "input[name='login']",
            "input[id='id_login']", 
            "input[type='text']",
            "input[placeholder*='Username']",
            "input[placeholder*='Email']"
        ]
        
        for selector in username_selectors:
            try:
                username_field = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                break
            except TimeoutException:
                continue
        
        if not username_field:
            print("Could not find username field")
            return None, None
            
        # Clear and enter username
        username_field.clear()
        username_field.send_keys(username)
        time.sleep(1)
        
        # Find password field
        password_field = None
        password_selectors = [
            "input[name='password']",
            "input[id='id_password']",
            "input[type='password']"
        ]
        
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
                
        if not password_field:
            print("Could not find password field")
            return None, None
            
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)
        
        # Find and click sign in button
        signin_button = None
        signin_selectors = [
            "button[id='signin_btn']",
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Sign In')",
            ".btn-primary"
        ]
        
        for selector in signin_selectors:
            try:
                signin_button = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
                
        if signin_button:
            signin_button.click()
        else:
            # Try pressing Enter as fallback
            password_field.send_keys(Keys.RETURN)
        
        print("Login submitted, waiting for success...")
        
        # Wait for successful login - try multiple indicators
        login_success = False
        success_indicators = [
            "a[href='/profile/']",
            ".user-avatar-link",
            "img.avatar",
            "[data-cy='user-avatar']"
        ]
        
        for indicator in success_indicators:
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                )
                login_success = True
                break
            except TimeoutException:
                continue
                
        if not login_success:
            print("Login may have failed or took too long")
            # Still try to get cookies in case we're actually logged in
            
        print("Extracting cookies...")
        cookies = driver.get_cookies()
        
        leetcode_session = None
        csrf_token = None
        
        for cookie in cookies:
            if cookie['name'] == 'LEETCODE_SESSION':
                leetcode_session = cookie['value']
            elif cookie['name'] == 'csrftoken':
                csrf_token = cookie['value']
                
        if leetcode_session and csrf_token:
            print("Successfully obtained session cookies!")
            return leetcode_session, csrf_token
        else:
            print(f"Missing cookies - LEETCODE_SESSION: {bool(leetcode_session)}, csrftoken: {bool(csrf_token)}")
            return None, None
            
    except Exception as e:
        print(f"Method 1 failed: {e}")
        return None, None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def get_leetcode_cookies_method2(username, password):
    """Method 2: Manual login with extended wait time."""
    print("Method 2: Opening Chrome for manual login...")
    
    kill_chrome_processes()
    
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = None
    try:
        driver = uc.Chrome(options=options, version_main=None)
        driver.maximize_window()
        
        print("Opening LeetCode login page...")
        driver.get("https://leetcode.com/accounts/login/")
        
        print("\n" + "="*50)
        print("MANUAL LOGIN REQUIRED")
        print("="*50)
        print("1. Please log in manually in the Chrome window")
        print("2. After successful login, you should see your profile")
        print("3. The script will automatically detect when you're logged in")
        print("4. DO NOT close the Chrome window")
        print("="*50 + "\n")
        
        # Wait for login completion with longer timeout
        login_success = False
        max_wait_time = 300  # 5 minutes
        check_interval = 2   # Check every 2 seconds
        elapsed_time = 0
        
        while elapsed_time < max_wait_time and not login_success:
            try:
                # Check for various login indicators
                success_indicators = [
                    "a[href*='profile']",
                    ".user-avatar-link", 
                    "img.avatar",
                    "[data-cy='user-avatar']",
                    ".navbar .avatar"
                ]
                
                for indicator in success_indicators:
                    try:
                        element = driver.find_element(By.CSS_SELECTOR, indicator)
                        if element and element.is_displayed():
                            login_success = True
                            break
                    except NoSuchElementException:
                        continue
                        
                if not login_success:
                    # Also check if URL changed to indicate successful login
                    current_url = driver.current_url
                    if 'login' not in current_url or 'problemset' in current_url or 'problems' in current_url:
                        login_success = True
                        
                if login_success:
                    break
                    
                time.sleep(check_interval)
                elapsed_time += check_interval
                
                # Show countdown every 30 seconds
                if elapsed_time % 30 == 0:
                    remaining = max_wait_time - elapsed_time
                    print(f"Still waiting for login... {remaining} seconds remaining")
                    
            except Exception as e:
                print(f"Error checking login status: {e}")
                time.sleep(check_interval)
                elapsed_time += check_interval
                
        if login_success:
            print("Login detected! Extracting cookies...")
            
            # Navigate to main page to ensure we get all cookies
            driver.get("https://leetcode.com/")
            time.sleep(2)
            
            cookies = driver.get_cookies()
            
            leetcode_session = None
            csrf_token = None
            
            for cookie in cookies:
                if cookie['name'] == 'LEETCODE_SESSION':
                    leetcode_session = cookie['value']
                elif cookie['name'] == 'csrftoken':
                    csrf_token = cookie['value']
                    
            if leetcode_session and csrf_token:
                print("Successfully obtained session cookies!")
                return leetcode_session, csrf_token
            else:
                print("Login detected but cookies not found. Trying to refresh...")
                driver.refresh()
                time.sleep(3)
                
                cookies = driver.get_cookies()
                for cookie in cookies:
                    if cookie['name'] == 'LEETCODE_SESSION':
                        leetcode_session = cookie['value']
                    elif cookie['name'] == 'csrftoken':
                        csrf_token = cookie['value']
                        
                return leetcode_session, csrf_token
        else:
            print("Login timeout reached. Please try again.")
            return None, None
            
    except Exception as e:
        print(f"Method 2 failed: {e}")
        return None, None
    finally:
        if driver:
            try:
                input("\nPress Enter to close the browser and continue...")
                driver.quit()
            except:
                pass

def get_leetcode_cookies(username, password):
    """Main function that tries different methods to get cookies."""
    print("Starting LeetCode cookie extraction...")
    
    # Try Method 1: Automated login
    print("\nTrying automated login...")
    cookies = get_leetcode_cookies_method1(username, password)
    if cookies[0] and cookies[1]:
        return cookies
    
    # Try Method 2: Manual login
    print("\nAutomated login failed. Falling back to manual login...")
    cookies = get_leetcode_cookies_method2(username, password)
    if cookies[0] and cookies[1]:
        return cookies
    
    print("\nAll methods failed to obtain cookies.")
    return None, None

# Create a scraper instance to handle all requests
scraper = cloudscraper.create_scraper()
# --- LeetCode API and GraphQL Details ---
LEETCODE_API_URL = "https://leetcode.com/graphql"
LEETCODE_BASE_URL = "https://leetcode.com"

# --- Queries ---
DAILY_CHALLENGE_QUERY = """
query questionOfToday {
  activeDailyCodingChallengeQuestion {
    question {
      questionId
      title
      titleSlug
    }
  }
}
"""
QUESTION_DETAILS_QUERY = """
query questionDetails($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    content
    codeSnippets {
      langSlug
      code
    }
  }
}
"""
SUBMISSION_STATUS_QUERY = """
query submissionList($questionSlug: String!) {
  questionSubmissionList(questionSlug: $questionSlug) {
    submissions
  }
}
"""

# --- Helper Functions ---
def get_daily_challenge():
    """Fetches details of the daily challenge."""
    response = scraper.post(LEETCODE_API_URL, json={'query': DAILY_CHALLENGE_QUERY})
    if response.status_code == 200:
        data = response.json()
        question = data['data']['activeDailyCodingChallengeQuestion']['question']
        title, title_slug, question_id = question['title'], question['titleSlug'], question['questionId']
        url = f"{LEETCODE_BASE_URL}/problems/{title_slug}/"
        return title, title_slug, question_id, url
    return None, None, None, None

def check_if_solved(question_slug, leetcode_session, csrf_token):
    """Checks for an 'Accepted' submission."""
    cookies = {'LEETCODE_SESSION': leetcode_session, 'csrftoken': csrf_token}
    variables = {'questionSlug': question_slug}
    payload = {'query': SUBMISSION_STATUS_QUERY, 'variables': variables}
    response = scraper.post(LEETCODE_API_URL, json=payload, cookies=cookies)
    if response.status_code == 200:
        data = response.json()
        submissions = json.loads(data['data']['questionSubmissionList']['submissions'])
        return any(sub['statusDisplay'] == 'Accepted' for sub in submissions)
    return False

# --- Gemini and Auto-Submission Functions ---
def get_problem_details(title_slug):
    """Gets the full problem description and C++ code snippet."""
    variables = {'titleSlug': title_slug}
    payload = {'query': QUESTION_DETAILS_QUERY, 'variables': variables}
    response = scraper.post(LEETCODE_API_URL, json=payload)
    if response.status_code == 200:
        question_data = response.json()['data']['question']
        problem_content = question_data['content']
        # FIX #1: Fetch the 'cpp' code snippet, not 'python3'
        code_snippet = next((cs['code'] for cs in question_data['codeSnippets'] if cs['langSlug'] == 'cpp'), None)
        return problem_content, code_snippet
    print("Error fetching problem details.")
    return None, None

def solve_with_gemini(problem_content, code_snippet, api_key):
    """Uses Gemini to generate a solution for the problem with robust error handling."""
    print("Asking Gemini for a solution...")
    genai.configure(api_key=api_key)

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    try:
        model = genai.GenerativeModel('gemini-2.0-flash-001', safety_settings=safety_settings)
        
        prompt = f"""
        You are an expert LeetCode solver. Your task is to solve the following programming problem in C++.
        Read the problem description carefully and provide a correct and efficient solution.
        **Problem Description:**
        {problem_content}
        **Your task is to complete the following C++ code snippet:**
        ```cpp
        {code_snippet}
        ```
        **Instructions:**
        1.  Provide only the complete, runnable C++ code for the solution.
        2.  Do NOT include any explanations, comments, or markdown formatting like ```cpp.
        3.  Your code should be implemented within the provided class and method structure.
        """
        
        response = model.generate_content(prompt)

        if not response.parts:
            block_reason = response.prompt_feedback.block_reason
            print(f"Error: Gemini API blocked the prompt. Reason: {block_reason}")
            return None

        cleaned_code = re.sub(r'```cpp\n|```', '', response.text).strip()
        return cleaned_code

    except Exception as e:
        print(f"An unexpected error occurred with the Gemini API: {e}")
        return None
    
def submit_solution(question_id, question_slug, solution_code, leetcode_session, csrf_token):
    """Submits the generated solution to LeetCode."""
    print("Submitting the solution to LeetCode...")
    submit_url = f"{LEETCODE_BASE_URL}/problems/{question_slug}/submit/"
    headers = {
        'x-csrftoken': csrf_token,
        'Referer': submit_url,
    }
    cookies = {
        'LEETCODE_SESSION': leetcode_session,
        'csrftoken': csrf_token
    }
    payload = {
        "question_id": question_id,
        "lang": "cpp",
        "typed_code": solution_code
    }
    
    response = scraper.post(submit_url, headers=headers, cookies=cookies, json=payload)
    
    if response.status_code == 200:
        submission_id = response.json().get('submission_id')
        print(f"Successfully submitted solution. Submission ID: {submission_id}")
        return True
    else:
        print(f"Error submitting solution: {response.status_code} - {response.text}")
        return False

# --- Main Execution Logic ---
def main():
    load_dotenv()

    leetcode_username = os.environ.get('LEETCODE_USERNAME')
    leetcode_password = os.environ.get('LEETCODE_PASSWORD')
    gemini_api_key = os.environ.get('GEMINI_API_KEY')

    if not all([leetcode_username, leetcode_password, gemini_api_key]):
        print("One or more environment variables are missing.")
        return
    leetcode_session, csrf_token = get_leetcode_cookies(leetcode_username, leetcode_password)
    if not leetcode_session or not csrf_token:
        print("Failed to retrieve session tokens. Aborting workflow.")
        return
    print("Fetching daily challenge...")
    challenge_title, challenge_slug, challenge_id, _ = get_daily_challenge()
    
    if not challenge_slug:
        print("Could not retrieve daily challenge. Exiting.")
        return
        
    print(f"Today's challenge: {challenge_title}")
    
    print("Checking submission status...")
    is_solved = check_if_solved(challenge_slug, leetcode_session, csrf_token)
    
    if is_solved:
        print("Congratulations! You have already solved the daily challenge.")
    else:
        print("Challenge not solved. Initiating auto-solve workflow...")
        problem_content, code_snippet = get_problem_details(challenge_slug)
        if not problem_content or not code_snippet:
            print("Failed to get problem details or C++ snippet was not found.")
            return

        solution_code = solve_with_gemini(problem_content, code_snippet, gemini_api_key)
        if not solution_code: return
            
        print("--- Generated Code ---\n" + solution_code + "\n----------------------")
        
        submit_solution(challenge_id, challenge_slug, solution_code, leetcode_session, csrf_token)

if __name__ == "__main__":
    main()