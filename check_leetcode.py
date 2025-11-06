import os
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- LeetCode API and GraphQL Details ---
LEETCODE_API_URL = "https://leetcode.com/graphql"
LEETCODE_BASE_URL = "https://leetcode.com"
DAILY_CHALLENGE_QUERY = """
query questionOfToday {
  activeDailyCodingChallengeQuestion {
    question {
      title
      titleSlug
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

# --- Function to programmatically get new tokens via login ---
def get_fresh_leetcode_tokens():
    username = os.environ.get('LEETCODE_USERNAME')  # set this in secrets
    password = os.environ.get('LEETCODE_PASSWORD')  # set this in secrets
    login_url = "https://leetcode.com/accounts/login/"
    session = requests.Session()
    # Step 1: Load login page to get CSRF token from cookies
    resp1 = session.get(login_url)
    if 'csrftoken' not in session.cookies:
        print("Failed to get initial CSRF token")
        return None, None
    csrf_token = session.cookies['csrftoken']
    # Step 2: Send login request
    login_payload = {
        'login': username,
        'password': password,
        'csrfmiddlewaretoken': csrf_token
    }
    headers = {
        'Referer': login_url,
        'User-Agent': 'Mozilla/5.0',
        'X-CSRFToken': csrf_token
    }
    resp2 = session.post(login_url, data=login_payload, headers=headers)
    if resp2.status_code != 200:
        print(f"Login failed with status {resp2.status_code}")
        return None, None
    if 'LEETCODE_SESSION' not in session.cookies:
        print("Login failed or session cookie missing")
        return None, None
    new_csrf_token = session.cookies.get('csrftoken')
    new_session = session.cookies.get('LEETCODE_SESSION')
    return new_session, new_csrf_token

# --- Function to get the daily challenge ---
def get_daily_challenge():
    response = requests.post(LEETCODE_API_URL, json={'query': DAILY_CHALLENGE_QUERY})
    if response.status_code == 200:
        data = response.json()
        question = data['data']['activeDailyCodingChallengeQuestion']['question']
        title = question['title']
        title_slug = question['titleSlug']
        url = f"{LEETCODE_BASE_URL}/problems/{title_slug}/"
        return title, title_slug, url
    else:
        print("Error fetching daily challenge.")
        return None, None, None

# --- Function to check if the challenge is solved ---
def check_if_solved(question_slug, leetcode_session, csrf_token):
    cookies = {
        'LEETCODE_SESSION': leetcode_session,
        'csrftoken': csrf_token
    }
    variables = {'questionSlug': question_slug}
    payload = {'query': SUBMISSION_STATUS_QUERY, 'variables': variables}
    response = requests.post(LEETCODE_API_URL, json=payload, cookies=cookies)
    if response.status_code == 200:
        data = response.json()
        submissions_str = data['data']['questionSubmissionList']['submissions']
        submissions = json.loads(submissions_str)
        for submission in submissions:
            if submission['statusDisplay'] == 'Accepted':
                return True
        return False
    else:
        print(f"Error checking submission status: {response.status_code}")
        print(response.text)
        return False

# --- Function to send an email alert ---
def send_email_alert(recipient_email, sender_email, sender_password, question_title, question_url):
    subject = "LeetCode Daily Challenge Reminder!"
    html_body = f"""
    <html>
      <body>
        <p>Hi there,</p>
        <p>This is a reminder that you haven't solved today's LeetCode daily challenge yet: <strong>{question_title}</strong>.</p>
        <p>Don't break your streak!</p>
        <p>You can find the problem here: <a href="{question_url}">{question_url}</a></p>
        <p>Best of luck!</p>
      </body>
    </html>
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg.attach(MIMEText(html_body, 'html'))
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender_email, sender_password)
            smtp_server.sendmail(sender_email, recipient_email, msg.as_string())
        print("Email alert sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# --- Main Execution Logic ---
def main():
    # Get fresh tokens via login before everything else
    leetcode_session, csrf_token = get_fresh_leetcode_tokens()
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    recipient_email = os.environ.get('RECIPIENT_EMAIL')
    if not all([leetcode_session, csrf_token, sender_email, sender_password, recipient_email]):
        print("One or more environment variables are missing or token refresh failed.")
        return
    print("Fetching daily challenge...")
    challenge_title, challenge_slug, challenge_url = get_daily_challenge()
    if not challenge_slug:
        print("Could not retrieve daily challenge slug. Exiting.")
        return
    print(f"Today's challenge: {challenge_title}")
    print(f"URL: {challenge_url}")
    print("Checking submission status...")
    is_solved = check_if_solved(challenge_slug, leetcode_session, csrf_token)
    if is_solved:
        print("Congratulations! You have already solved the daily challenge.")
    else:
        print("You have not solved the daily challenge yet. Sending a reminder.")
        send_email_alert(recipient_email, sender_email, sender_password, challenge_title, challenge_url)

if __name__ == "__main__":
    main()
