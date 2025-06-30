import aiosmtplib, re, dns.asyncresolver
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

async def verify_email(address: str):
    if not EMAIL_REGEX.match(address):
        return False, "invalid-syntax"
    domain = address.split("@", 1)[1]
    try:
        answers = await dns.asyncresolver.resolve(domain, "MX")
    except Exception:
        return False, "no-mx"

    mx_record = str(sorted(answers, key=lambda r: r.preference)[0].exchange).rstrip('.')
    try:
        smtp = aiosmtplib.SMTP(hostname=mx_record, timeout=8)
        await smtp.connect()
        await smtp.helo("example.com")
        code, _ = await smtp.mail("<verify@example.com>")
        code, _ = await smtp.rcpt(f"<{address}>")
        await smtp.quit()
        if code in (250, 451, 452):
            return True, "accepted"
        else:
            return False, f"smtp-code-{code}"
    except Exception as e:
        return True, "mx-valid-no-smtp"