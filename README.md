# LeetCode Daily Challenge Reminder

An automated Python script that checks if you've solved today's LeetCode daily challenge and sends you an email reminder if you haven't. This project runs automatically via GitHub Actions every day at 11:00 PM IST to help you maintain your coding streak.

## Features

- 🤖 **Automated Daily Checking**: Runs daily to check if you've solved the LeetCode daily challenge
- 📧 **Email Reminders**: Sends HTML email notifications with clickable problem links
- 📊 **Submission Status Tracking**: Checks your submission history to verify if the problem is already solved
- ⏰ **Streak Maintenance**: Helps you maintain your LeetCode solving streak
- 🔄 **GitHub Actions Integration**: Fully automated via GitHub Actions workflow
- 🔒 **Secure**: Uses environment variables for sensitive credentials

## How It Works

1. **Daily Trigger**: GitHub Actions runs the script daily at 11:00 PM IST
2. **Challenge Detection**: Fetches today's LeetCode daily challenge
3. **Status Check**: Checks if you've already solved the challenge
4. **Email Reminder**: If not solved, sends an HTML email with the problem link
5. **Streak Motivation**: Helps you stay consistent with daily practice

## Setup Instructions

### 1. Fork this Repository

Fork this repository to your GitHub account.

### 2. Required Environment Variables

You need to set up the following secrets in your GitHub repository:

#### 2.1 LeetCode Credentials

1. **LEETCODE_SESSION**: Your LeetCode session cookie
   - Log into LeetCode in your browser
   - Open Developer Tools (F12)
   - Go to Application/Storage → Cookies → leetcode.com
   - Find `LEETCODE_SESSION` and copy its value

2. **CSRF_TOKEN**: Your LeetCode CSRF token
   - In the same cookies section, find `csrftoken` and copy its value

#### 2.2 Email Configuration

1. **SENDER_EMAIL**: Your Gmail address (the account that will send reminders)
2. **SENDER_PASSWORD**: Your Gmail app password (not your regular password)
   - Go to your Google Account settings
   - Enable 2-factor authentication
   - Generate an App Password for this application
3. **RECIPIENT_EMAIL**: The email address where you want to receive reminders (can be the same as sender)

### 3. Add Secrets to GitHub

1. Go to your forked repository on GitHub
2. Click on `Settings` → `Secrets and variables` → `Actions`
3. Click `New repository secret` and add each of the five secrets:
   - `LEETCODE_SESSION`
   - `CSRF_TOKEN`
   - `SENDER_EMAIL`
   - `SENDER_PASSWORD`
   - `RECIPIENT_EMAIL`

### 4. Enable GitHub Actions

1. Go to the `Actions` tab in your repository
2. Enable workflows if prompted
3. The workflow will now run automatically daily at 11:00 PM IST

## Local Development

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/leetcode-reminder.git
cd leetcode-reminder
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
LEETCODE_SESSION=your_leetcode_session_cookie
CSRF_TOKEN=your_csrf_token
SENDER_EMAIL=your_gmail_address
SENDER_PASSWORD=your_gmail_app_password
RECIPIENT_EMAIL=your_recipient_email
```

5. Run the script:
```bash
python check_leetcode.py
```

## Dependencies

- `requests`: For HTTP requests to LeetCode API

## File Structure

```
leetcode-reminder/
├── check_leetcode.py           # Main script
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .github/
│   └── workflows/
│       └── leetcode-checker.yml # GitHub Actions workflow
└── .env                        # Environment variables (create this locally)
```

## GitHub Actions Workflow

The workflow (`leetcode-checker.yml`) is configured to:
- Run daily at 11:00 PM IST (17:30 UTC)
- Can be manually triggered via `workflow_dispatch`
- Uses Ubuntu latest runner
- Sets up Python 3.10 environment
- Installs only the `requests` dependency and runs the script

## Troubleshooting

### Common Issues

1. **Script fails to authenticate**:
   - Check if your `LEETCODE_SESSION` and `CSRF_TOKEN` are still valid
   - These tokens expire periodically, so you may need to update them

2. **Email sending fails**:
   - Verify your Gmail credentials are correct
   - Make sure you're using an App Password, not your regular Gmail password
   - Ensure 2-factor authentication is enabled on your Gmail account

3. **No email received**:
   - Check your spam/junk folder
   - Verify the `RECIPIENT_EMAIL` is correct
   - Check if Gmail is blocking the app (check security settings)

### Getting Fresh Cookies

LeetCode session cookies expire regularly. To get fresh cookies:
1. Clear your browser cache for leetcode.com
2. Log in again to LeetCode
3. Extract the new `LEETCODE_SESSION` and `csrftoken` values
4. Update your GitHub repository secrets

### Setting up Gmail App Password

1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification
3. Enable 2-Step Verification if not already enabled
4. Go to Security → App passwords
5. Generate a new app password for "Mail"
6. Use this 16-character password as your `SENDER_PASSWORD`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Disclaimer

This tool is for educational purposes and personal motivation. It helps you stay consistent with your LeetCode practice by sending email reminders when you haven't solved the daily challenge. The goal is to support your learning journey and help maintain coding consistency.

## Support

If you encounter any issues or have questions, please open an issue in the GitHub repository.

---

⭐ If you find this project helpful, please give it a star!
