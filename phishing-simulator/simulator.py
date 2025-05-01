import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PhishingSimulator:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')

        # Local server configuration
        self.local_server = "http://localhost:5001"

    def load_template(self, template_name):
        """Load an HTML email template"""
        return self.env.get_template(f'{template_name}.html')

    def send_phishing_email(self, recipient_email, template_name, template_data):
        """Send a phishing simulation email"""
        try:
            # Add local server URL to template data
            if template_name == 'password_reset':
                template_data['reset_link'] = f"{self.local_server}/fake-reset"
            elif template_name == 'account_verification':
                template_data['verification_link'] = f"{self.local_server}/fake-verify"

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = template_data.get('subject', 'Important Account Update')
            msg['From'] = self.sender_email
            msg['To'] = recipient_email

            # Load and render template
            template = self.load_template(template_name)
            html_content = template.render(**template_data)
            
            # Attach HTML content
            msg.attach(MIMEText(html_content, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True, "Email sent successfully"
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"

def main():
    # Example usage
    simulator = PhishingSimulator()
    
    # Example phishing scenarios
    scenarios = [
        {
            'name': 'password_reset',
            'data': {
                'subject': 'Urgent: Password Reset Required',
                'company_name': 'Your Bank',
                'expiry_hours': 24
            }
        },
        {
            'name': 'account_verification',
            'data': {
                'subject': 'Verify Your Account',
                'company_name': 'Online Store',
                'account_id': 'ACC123456'
            }
        }
    ]

    # Send test emails
    test_email = input("Enter recipient email for testing: ")
    for scenario in scenarios:
        success, message = simulator.send_phishing_email(
            test_email,
            scenario['name'],
            scenario['data']
        )
        print(f"Scenario {scenario['name']}: {message}")

if __name__ == '__main__':
    main() 