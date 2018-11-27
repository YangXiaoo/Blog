# coding:UTF-8
from smtplib import SMTP, SMTP_SSL, SMTPAuthenticationError, SMTPConnectError, SMTPSenderRefused

mail_port = 465
mail_host = "smtp.qq.com"
mail_addr = "1593606228@qq.com"
mail_pass = "xx"
if mail_port == 465:
    smtp = SMTP_SSL(mail_host, port=mail_port, timeout=2)
else:
    smtp = SMTP(mail_host, port=mail_port, timeout=2)
smtp.login(mail_addr, mail_pass)
smtp.sendmail(mail_addr, (mail_addr, ),
              '''From:%s\r\nTo:%s\r\nSubject:myweb Mail Test!\r\n\r\n  Mail test passed!\r\n''' %
              (mail_addr, mail_addr))
smtp.quit()
