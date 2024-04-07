import smtplib

def send_email(subject, body, address_list):
    # Set up the SMTP server
    smtp_server = "smtp.gmail.com"
    smtp_username = "ichmail.home@gmail.com"
    smtp_password = "srjd vlje aeug hrzw"

    # Send the message
    for mail in address_list:
        with smtplib.SMTP(smtp_server) as connection:
            connection.starttls()
            connection.login(user=smtp_username, password=smtp_password)
            connection.sendmail(from_addr=smtp_username, to_addrs=mail, msg=f"Subject:{subject}\n\n{body}")

