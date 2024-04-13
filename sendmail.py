import asyncio
import smtplib

async def sendEmail(sender_email, receiver_email, subject, message):
    print("Attempting to send email.")
    sender_password = "2V3W7UH6"  # Replace this with the actual password
    smtp_server = "mail.gndec.ac.in"  # Replace this with the actual SMTP server
    smtp_port = 465
    try:
        session = smtplib.SMTP_SSL(smtp_server, smtp_port)
        session.login(sender_email, sender_password)
        msg = f'From: {sender_email}\r\nTo: {receiver_email}\r\nContent-Type: text/plain; charset="utf-8"\r\nSubject: {subject}\r\n\r\n{message}'
        session.sendmail(sender_email, receiver_email, msg.encode('utf8'))
        session.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error: {e}")
