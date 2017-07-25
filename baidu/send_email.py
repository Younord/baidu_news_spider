from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send_ms(T):
    from_addr = "wemmaling@163.com"
    password = 'klldxmkj:"000'
    to_addr = 'wemmaling@163.com'
    smtp_server = 'smtp.163.com'
    msg = MIMEText(T, 'plain', 'utf-8')
    msg['From'] = _format_addr('Anyone')
    msg['To'] = _format_addr('Echo')
    msg['Subject'] = Header('The New Report', 'utf-8').encode()
    server = smtplib.SMTP_SSL(smtp_server, 465, timeout=10)
    server.set_debuglevel(0)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

# send_ms('测试测试测试')
