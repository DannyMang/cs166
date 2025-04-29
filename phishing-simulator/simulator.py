import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import argparse
import os
import json
import random
from datetime import datetime

class PhishingSimulator:
    def __init__(self, config_file=None):
        self.config = {
            "smtp_server": "localhost",
            "smtp_port": 1025,  # Default to Python's debugging server
            "sender_email": "security@company.com",
            "templates_dir": "templates"
        }
        
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config.update(json.load(f))
        
        # Ensure templates directory exists
        os.makedirs(self.config["templates_dir"], exist_ok=True)
        
    def load_template(self, template_name):
        """Load an email template from file"""
        template_path = os.path.join(self.config["templates_dir"], f"{template_name}.html")
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template {template_name} not found")
        
        with open(template_path, 'r') as f:
            return f.read()
    
    def personalize_template(self, template, recipient_data):
        """Replace placeholders in template with recipient data"""
        personalized = template
        
        for key, value in recipient_data.items():
            placeholder = f"{{{{{key}}}}}"
            personalized = personalized.replace(placeholder, str(value))
        
        # Add some randomization to make each email unique
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        personalized = personalized.replace("{{current_time}}", current_time)
        
        # Add a random ID
        random_id = ''.join(random.choices('0123456789ABCDEF', k=8))
        personalized = personalized.replace("{{random_id}}", random_id)
        
        return personalized
    
    def send_email(self, recipient_email, subject, body_html, sender_name=None):
        """Send a phishing email"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        
        if sender_name:
            msg['From'] = f"{sender_name} <{self.config['sender_email']}>"
        else:
            msg['From'] = self.config['sender_email']
            
        msg['To'] = recipient_email
        
        # Attach HTML content
        msg.attach(MIMEText(body_html, 'html'))
        
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"])
            
            # For real SMTP servers, you would use:
            # server.starttls()
            # server.login(username, password)
            
            # Send email
            server.sendmail(self.config['sender_email'], recipient_email, msg.as_string())
            server.quit()
            
            print(f"Phishing email sent to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def run_campaign(self, campaign_file):
        """Run a phishing campaign from a configuration file"""
        if not os.path.exists(campaign_file):
            raise FileNotFoundError(f"Campaign file {campaign_file} not found")
        
        with open(campaign_file, 'r') as f:
            campaign = json.load(f)
        
        template_name = campaign.get("template")
        subject = campaign.get("subject", "Important Information")
        sender_name = campaign.get("sender_name")
        
        if not template_name:
            raise ValueError("Campaign must specify a template")
        
        template = self.load_template(template_name)
        
        success_count = 0
        for recipient in campaign.get("recipients", []):
            email = recipient.get("email")
            if not email:
                continue
                
            personalized_template = self.personalize_template(template, recipient)
            
            if self.send_email(email, subject, personalized_template, sender_name):
                success_count += 1
        
        print(f"Campaign completed. {success_count} emails sent successfully.")
        return success_count

def main():
    parser = argparse.ArgumentParser(description='Phishing Simulator for Educational Purposes')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--campaign', help='Path to campaign file')
    parser.add_argument('--template', help='Template to use')
    parser.add_argument('--email', help='Single recipient email')
    parser.add_argument('--subject', default='Important Information', help='Email subject')
    
    args = parser.parse_args()
    
    simulator = PhishingSimulator(args.config)
    
    if args.campaign:
        simulator.run_campaign(args.campaign)
    elif args.template and args.email:
        template = simulator.load_template(args.template)
        personalized = simulator.personalize_template(template, {"name": args.email.split('@')[0]})
        simulator.send_email(args.email, args.subject, personalized)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 