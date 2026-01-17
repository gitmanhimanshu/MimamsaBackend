"""
Email Service using Brevo API (Production Safe)
No SMTP connection issues on Render
Uses existing environment variable names: EMAIL_HOST_PASSWORD as Brevo API key
"""
import requests
from django.conf import settings


BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_otp_email(to_email, otp, user_name=None):
    """
    Send OTP email using Brevo API
    
    Args:
        to_email: Recipient email address
        otp: OTP code to send
        user_name: Optional user name
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Get API key from EMAIL_HOST_PASSWORD (existing variable)
        api_key = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
        if not api_key:
            print("⚠️ EMAIL_HOST_PASSWORD (Brevo API key) not configured")
            return False, "Email service not configured"
        
        # Get sender email from DEFAULT_FROM_EMAIL (existing variable)
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@mimanasa.com')
        
        # Prepare headers
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
        
        # Prepare recipient name
        name = user_name or "User"
        
        # Prepare email payload
        payload = {
            "sender": {
                "name": "Mimanasa",
                "email": from_email
            },
            "to": [
                {"email": to_email, "name": name}
            ],
            "subject": "Mimanasa - Password Reset OTP",
            "htmlContent": f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background: #4299e1; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                        .otp-box {{ background: white; border: 2px solid #4299e1; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px; }}
                        .otp-code {{ font-size: 32px; font-weight: bold; color: #4299e1; letter-spacing: 5px; }}
                        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Mimanasa</h1>
                        </div>
                        <div class="content">
                            <h2>Hello {name},</h2>
                            <p>You requested to reset your password for your Mimanasa account.</p>
                            <p>Your One-Time Password (OTP) is:</p>
                            <div class="otp-box">
                                <div class="otp-code">{otp}</div>
                            </div>
                            <p><strong>This OTP is valid for 10 minutes.</strong></p>
                            <p>If you didn't request this password reset, please ignore this email or contact support if you have concerns.</p>
                            <p>Best regards,<br>Mimanasa Team</p>
                        </div>
                        <div class="footer">
                            <p>This is an automated email. Please do not reply.</p>
                        </div>
                    </div>
                </body>
                </html>
            """
        }
        
        # Log email attempt
        print(f"📧 Sending OTP email via Brevo API")
        print(f"   To: {to_email}")
        print(f"   Name: {name}")
        print(f"   OTP: {otp}")
        print(f"   From: {from_email}")
        
        # Send email via Brevo API
        response = requests.post(BREVO_API_URL, json=payload, headers=headers, timeout=10)
        
        # Check response
        if response.status_code in [200, 201]:
            print(f"✓ Email sent successfully via Brevo API")
            print(f"   Response: {response.text}")
            return True, "Email sent successfully"
        else:
            error_msg = f"Brevo API error: {response.status_code} - {response.text}"
            print(f"⚠️ {error_msg}")
            return False, error_msg
            
    except requests.exceptions.Timeout:
        error_msg = "Email service timeout"
        print(f"⚠️ {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Email error: {type(e).__name__}: {str(e)}"
        print(f"⚠️ {error_msg}")
        return False, error_msg
