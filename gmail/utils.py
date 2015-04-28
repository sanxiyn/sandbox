import email.utils

def from_domain(message):
    addr = message['From']
    mail = email.utils.parseaddr(addr)[1]
    domain = mail.rpartition('@')[-1]
    domain = domain.lower()
    return domain
