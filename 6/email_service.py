"""Simple Email Service for Verification"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailService:
    """Send verification emails"""

    def __init__(self):
        # Email configuration from environment (baked into Docker image)
        self.smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_user = os.environ.get('SMTP_USER', '')
        self.smtp_pass = os.environ.get('SMTP_PASS', '')
        self.from_email = os.environ.get('FROM_EMAIL', self.smtp_user)
        self.base_url = os.environ.get('BASE_URL', 'http://localhost:5000')

    def send_verification_email(self, to_email, username, verification_token):
        """Send email verification link"""

        # For testing/demo: Just print the link if SMTP not configured
        if not self.smtp_user or not self.smtp_pass:
            verification_link = f"{self.base_url}/api/auth/verify?token={verification_token}"
            print("\n" + "="*70)
            print(f"📧 EMAIL VERIFICATION (SMTP not configured - showing link)")
            print("="*70)
            print(f"To: {to_email}")
            print(f"Subject: Verify your email")
            print(f"\nVerification link:")
            print(f"{verification_link}")
            print("="*70 + "\n")
            return {'success': True, 'message': 'Verification link printed to console'}

        # Production: Send actual email
        try:
            verification_link = f"{self.base_url}/api/auth/verify?token={verification_token}"

            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Verify your email - Master Teacher'
            msg['From'] = self.from_email
            msg['To'] = to_email

            text = f"""
Hi {username},

Thank you for signing up! Please verify your email address by clicking the link below:

{verification_link}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
Master Teacher Team
"""

            html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2>Welcome to Master Teacher, {username}!</h2>
    <p>Thank you for signing up. Please verify your email address to complete your registration.</p>
    <p style="margin: 30px 0;">
        <a href="{verification_link}"
           style="background-color: #4CAF50; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; display: inline-block;">
            Verify Email Address
        </a>
    </p>
    <p style="color: #666; font-size: 12px;">
        Or copy and paste this link into your browser:<br>
        {verification_link}
    </p>
    <p style="color: #666; font-size: 12px;">
        This link will expire in 24 hours.
    </p>
    <hr style="margin-top: 30px; border: none; border-top: 1px solid #eee;">
    <p style="color: #999; font-size: 11px;">
        If you didn't create an account, please ignore this email.
    </p>
</body>
</html>
"""

            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            return {'success': True, 'message': 'Verification email sent'}

        except Exception as e:
            print(f"❌ Email send error: {e}")
            # Fallback: print to console
            verification_link = f"{self.base_url}/api/auth/verify?token={verification_token}"
            print(f"\n📧 Verification link (email failed): {verification_link}\n")
            return {'success': False, 'error': str(e), 'verification_link': verification_link}
