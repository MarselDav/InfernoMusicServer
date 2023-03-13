import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "marsel.corporation.usa@gmail.com"
receiver_email = "mrsldavletov@gmail.com"
password = "axhpncxcqhzngjhq"

message = MIMEMultipart("alternative")
message["Subject"] = "multipart test"
message["From"] = sender_email
message["To"] = receiver_email

# Create the plain-text and HTML version of your message
text = """\
QT_Musical_App
Hey mardeastroyer
Please verify your QT_Musical_App account.
You can also enter this verification code:
711350"""
html = """\
<html>
  <body>
    <div style="font-family: arial; margin: 0 auto; border-radius: 10px;
    background-color: ghostwhite; width: 50%; box-shadow: 4px 4px 8px 4px rgba(34, 60, 80, 0.2);">
        <h1 align="center">QT_Musical_App</h1>
        <h2 align="center" style="color: red;">Hey mardeastroyer</h2>
        <h3 align="center">Please verify your QT_Musical_App account.</h3>
        <p align="center">You can also enter this verification code:</p>
        <p style="text-align:center; background:#faf9fa;
        border:1px solid;border-style:solid;
        border-color:#dad8de;
        padding-bottom:5px;padding-left:5px;
        padding-right:5px;padding-top:5px">711350</p>
    </div>
  </body>
</html>
"""

# Turn these into plain/html MIMEText objects
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")

# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
message.attach(part1)
message.attach(part2)

# Create secure connection with server and send email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(
        sender_email, receiver_email, message.as_string()
)