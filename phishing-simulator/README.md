# Phishing Simulator

This is an educational tool designed to demonstrate how phishing attacks work through email. It simulates common phishing scenarios to help users recognize and avoid real phishing attempts.

## Features

- Simulates common phishing email scenarios:
  - Password reset requests
  - Account verification
- Uses realistic HTML email templates
- Configurable email settings
- Educational purpose only

## Prerequisites

- Python 3.7+
- SMTP server access (e.g., Gmail)
- Required Python packages (install via `pip install -r requirements.txt`):
  - python-dotenv
  - jinja2

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure email settings:
   - Copy `.env.example` to `.env`
   - Update the following variables in `.env`:
     - `SMTP_SERVER`: Your SMTP server (default: smtp.gmail.com)
     - `SMTP_PORT`: SMTP port (default: 587)
     - `SENDER_EMAIL`: Your email address
     - `SENDER_PASSWORD`: Your email password or app-specific password

## Usage

1. Run the simulator:
   ```bash
   python simulator.py
   ```

2. Enter the recipient's email address when prompted

3. The simulator will send two example phishing emails:
   - A password reset request
   - An account verification request

## Security Notice

This tool is for educational purposes only. Always:
- Use with explicit permission from recipients
- Clearly mark emails as simulations
- Never use for malicious purposes
- Follow ethical guidelines and local laws

## Contributing

Feel free to submit issues and enhancement requests! 