import os
import re
import requests
import json
import google.generativeai as genai
import cloudscraper # MODIFICATION: Import cloudscraper

# MODIFICATION: Create a scraper instance to handle all requests
scraper = cloudscraper.create_scraper()

# --- LeetCode API and GraphQL Details ---
LEETCODE_API_URL = "https://leetcode.com/graphql"
LEETCODE_BASE_URL = "https://leetcode.com"

# --- Queries (No changes here) ---
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
    # MODIFICATION: Use scraper instead of requests
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
    # MODIFICATION: Use scraper instead of requests
    response = scraper.post(LEETCODE_API_URL, json=payload, cookies=cookies)
    if response.status_code == 200:
        data = response.json()
        submissions = json.loads(data['data']['questionSubmissionList']['submissions'])
        return any(sub['statusDisplay'] == 'Accepted' for sub in submissions)
    return False

# --- Gemini and Auto-Submission Functions ---
def get_problem_details(title_slug):
    """Gets the full problem description and Python code snippet."""
    variables = {'titleSlug': title_slug}
    payload = {'query': QUESTION_DETAILS_QUERY, 'variables': variables}
    # MODIFICATION: Use scraper instead of requests
    response = scraper.post(LEETCODE_API_URL, json=payload)
    if response.status_code == 200:
        question_data = response.json()['data']['question']
        problem_content = question_data['content']
        python_snippet = next((cs['code'] for cs in question_data['codeSnippets'] if cs['langSlug'] == 'python3'), None)
        return problem_content, python_snippet
    print("Error fetching problem details.")
    return None, None

def solve_with_gemini(problem_content, code_snippet, api_key):
    """Uses Gemini to generate a solution for the problem."""
    print("Asking Gemini for a solution...")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    You are an expert LeetCode solver. Your task is to solve the following programming problem in Python 3.
    Read the problem description carefully and provide a correct and efficient solution.
    **Problem Description:**
    {problem_content}
    **Your task is to complete the following Python code snippet:**
    ```python
    {code_snippet}
    ```
    **Instructions:**
    1.  Provide only the complete, runnable Python code for the solution.
    2.  Do NOT include any explanations, comments, or markdown formatting like ```python.
    3.  Your code should be implemented within the provided class and method structure.
    """
    try:
        response = model.generate_content(prompt)
        cleaned_code = re.sub(r'```python\n|```', '', response.text).strip()
        return cleaned_code
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
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
        "lang": "python3",
        "typed_code": solution_code
    }
    
    # MODIFICATION: Use scraper instead of requests
    response = scraper.post(submit_url, headers=headers, cookies=cookies, json=payload)
    
    if response.status_code == 200:
        submission_id = response.json().get('submission_id')
        print(f"Successfully submitted solution. Submission ID: {submission_id}")
        return True
    else:
        # This will now show the actual error if cloudscraper also fails.
        print(f"Error submitting solution: {response.status_code} - {response.text}")
        return False

# --- Main Execution Logic (No changes here) ---
def main():
    leetcode_session = os.environ.get('LEETCODE_SESSION')
    csrf_token = os.environ.get('CSRF_TOKEN')
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    
    if not all([leetcode_session, csrf_token, gemini_api_key]):
        print("One or more environment variables are missing.")
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
        if not problem_content or not code_snippet: return

        solution_code = solve_with_gemini(problem_content, code_snippet, gemini_api_key)
        if not solution_code: return
            
        print("--- Generated Code ---\n" + solution_code + "\n----------------------")
        
        submit_solution(challenge_id, challenge_slug, solution_code, leetcode_session, csrf_token)

if __name__ == "__main__":
    main()