import os
import re
import requests
import json
import google.generativeai as genai
import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Selenium Login Function ---
def get_leetcode_cookies(username, password):
    """Logs into LeetCode using a headless browser to get fresh cookies."""
    print("Launching headless browser to log into LeetCode...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://leetcode.com/accounts/login/")
        
        # Wait for the username field and type credentials
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_login"))
        ).send_keys(username)
        
        driver.find_element(By.ID, "id_password").send_keys(password)
        driver.find_element(By.ID, "signin_btn").click()
        
        # Wait for a successful login by checking for the user avatar link
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.user-avatar-link"))
        )
        print("Login successful! Extracting cookies.")
        
        cookies = driver.get_cookies()
        
        leetcode_session = next((c['value'] for c in cookies if c['name'] == 'LEETCODE_SESSION'), None)
        csrf_token = next((c['value'] for c in cookies if c['name'] == 'csrftoken'), None)
        
        if leetcode_session and csrf_token:
            print("Successfully extracted LEETCODE_SESSION and csrftoken.")
        
        return leetcode_session, csrf_token
        
    except Exception as e:
        print(f"An error occurred during automated login: {e}")
        driver.save_screenshot('login_error.png') # Helps debug in GitHub Actions
        return None, None
    finally:
        driver.quit()
        
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