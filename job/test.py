import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body, to_email):
    # Email configurations
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'dilraj082@gmail.com'  # Your Gmail email address
    sender_password = 'quest2019'  # Your Gmail password

    # Create a MIMEText object for the email body
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = to_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # Connect to the SMTP server and send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)  # Log in to the email account
        server.send_message(message)  # Send the email

# Example usage:
subject = 'Test Email'
body = 'This is a test email sent from Python.'
to_email = 'dilrajs125@gmail.com'
send_email(subject, body, to_email)
