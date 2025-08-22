# LeetCode Daily Challenge Auto-Solver

An automated Python script that checks if you've solved today's LeetCode daily challenge and automatically solves it using Google's Gemini AI if you haven't. This project runs automatically via GitHub Actions every day at 11:00 PM IST.

## Features

- 🤖 **Automated Daily Checking**: Runs daily to check if you've solved the LeetCode daily challenge
- 🧠 **AI-Powered Solutions**: Uses Google Gemini AI to generate C++ solutions
- 📊 **Submission Status Tracking**: Checks your submission history to verify if the problem is already solved
- ⚡ **Auto-Submission**: Automatically submits the generated solution to LeetCode
- 🔄 **GitHub Actions Integration**: Fully automated via GitHub Actions workflow
- 🔒 **Secure**: Uses environment variables for sensitive credentials

## How It Works

1. **Daily Trigger**: GitHub Actions runs the script daily at 11:00 PM IST
2. **Challenge Detection**: Fetches today's LeetCode daily challenge
3. **Status Check**: Checks if you've already solved the challenge
4. **AI Solution**: If not solved, uses Gemini AI to generate a C++ solution
5. **Auto-Submit**: Submits the solution to LeetCode automatically

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

#### 2.2 Google Gemini API Key

1. **GEMINI_API_KEY**: Your Google Gemini API key
   - Go to [Google AI Studio](https://aistudio.google.com/)
   - Create a new API key
   - Copy the API key value

### 3. Add Secrets to GitHub

1. Go to your forked repository on GitHub
2. Click on `Settings` → `Secrets and variables` → `Actions`
3. Click `New repository secret` and add each of the three secrets:
   - `LEETCODE_SESSION`
   - `CSRF_TOKEN`
   - `GEMINI_API_KEY`

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
GEMINI_API_KEY=your_gemini_api_key
```

5. Run the script:
```bash
python check_leetcode.py
```

## Dependencies

- `requests`: For HTTP requests to LeetCode API
- `google-generativeai`: Google Gemini AI SDK
- `cloudscraper`: For bypassing CloudFlare protection
- `python-dotenv`: For loading environment variables from .env file

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
- Installs dependencies and runs the script

## Troubleshooting

### Common Issues

1. **Script fails to authenticate**:
   - Check if your `LEETCODE_SESSION` and `CSRF_TOKEN` are still valid
   - These tokens expire periodically, so you may need to update them

2. **Gemini API errors**:
   - Verify your `GEMINI_API_KEY` is correct and has sufficient quota
   - Check if there are any safety filter blocks in the console output

3. **Solution submission fails**:
   - The generated solution might have syntax errors
   - LeetCode may have rate limiting in place

### Getting Fresh Cookies

LeetCode session cookies expire regularly. To get fresh cookies:
1. Clear your browser cache for leetcode.com
2. Log in again to LeetCode
3. Extract the new `LEETCODE_SESSION` and `csrftoken` values
4. Update your GitHub repository secrets

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Disclaimer

This tool is for educational purposes. While it automates LeetCode submissions, it's recommended to understand the solutions generated by AI and use this tool responsibly. The goal should be learning and improving your programming skills.

## Support

If you encounter any issues or have questions, please open an issue in the GitHub repository.

---

⭐ If you find this project helpful, please give it a star!
