def sendMail(subject, text):
    import os
    import smtplib
    import mimetypes
    import email
    gmailUser = 'weaselkeene@gmail.com'
    gmailPassword = 'weaselbotnet!'
    recipient = 'dangarant@gmail.com'
    msg = email.MIMEMultipart.MIMEMultipart()
    msg['From'] = gmailUser
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(email.MIMEText.MIMEText(text))
    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmailUser, gmailPassword)
    mailServer.sendmail(gmailUser, recipient, msg.as_string())
    mailServer.close()
    print('Sent email to %s' % recipient)

content = (
            "Dear Spam Recipient,\n\n"
            "I hope you are having a lovely day.\n\n"
            "Sincerely,\n"
            "Weasel\n"
          )

sendMail('Some Spam from Weasel', content)

