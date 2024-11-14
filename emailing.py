import os
import smtplib
from email.message import EmailMessage
import mimetypes

# Email credentials
sender = "ikedichukwu1993@gmail.com"
password = os.getenv("PASSWORD")
receiver = "nwaikukutv@gmail.com"


def send_email(image_path):
    print("sent email function started")
    # Create an EmailMessage object
    email_message = EmailMessage()
    email_message["Subject"] = "New customer showed up!"
    email_message["From"] = sender
    email_message["To"] = receiver
    email_message.set_content("Hey, we just saw a new customer!")

    # Read the image file and get the MIME type
    with open(image_path, "rb") as file:
        content = file.read()
        mime_type, _ = mimetypes.guess_type(image_path)
        main_type, sub_type = mime_type.split('/')

        # Add the image as an attachment
        email_message.add_attachment(content, maintype=main_type, subtype=sub_type)

    # Connect to Gmail and send the email
    with smtplib.SMTP("smtp.gmail.com", 587) as gmail:
        gmail.ehlo()
        gmail.starttls()
        gmail.login(sender, password)
        gmail.send_message(email_message)
        print("sent email function ended")


if __name__ == "__main__":
    send_email(image_path="images/19.png")
