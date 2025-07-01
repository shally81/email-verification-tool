import os, re, asyncio, requests, aiosmtplib, dns.asyncresolver
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
ZB_API_KEY = os.getenv("ZB_API_KEY")
NB_API_KEY = os.getenv("NB_API_KEY")

def _zb_call(email):
    url = "https://api.zerobounce.net/v2/validate"
    params = {"api_key": ZB_API_KEY, "email": email}
    try:
        return requests.get(url, params=params, timeout=10).json()
    except Exception:
        return {}

def _nb_call(email):
    url = "https://api.neverbounce.com/v4/single/check"
    params = {"key": NB_API_KEY, "email": email}
    try:
        return requests.get(url, params=params, timeout=10).json()
    except Exception:
        return {}

async def verify_email(address: str):
    if not EMAIL_REGEX.match(address):
        return False, "invalid-syntax"
    if ZB_API_KEY:
        data = await asyncio.to_thread(_zb_call, address)
        status = data.get("status")
        if status in ("valid", "catch-all", "unknown"):
            return True, f"zb-{status}"
        return False, f"zb-{status or 'error'}"
    if NB_API_KEY:
        data = await asyncio.to_thread(_nb_call, address)
        status = data.get("result")
        if status in ("valid", "catchall", "unknown"):
            return True, f"nb-{status}"
        return False, f"nb-{status or 'error'}"
    domain = address.split("@", 1)[1]
    try:
        answers = await dns.asyncresolver.resolve(domain, "MX")
    except Exception:
        return False, "no-mx"
    mx = str(sorted(answers, key=lambda r: r.preference)[0].exchange).rstrip('.')
    try:
        smtp = aiosmtplib.SMTP(hostname=mx, timeout=8)
        await smtp.connect()
        await smtp.helo("example.com")
        await smtp.mail("<verify@example.com>")
        code, _ = await smtp.rcpt(f"<{address}>")
        await smtp.quit()
        if code in (250, 451, 452):
            return True, "smtp-accepted"
        return False, f"smtp-code-{code}"
    except Exception:
        return True, "mx-valid-no-smtp"

def get_message_for_reason(status: bool, reason: str) -> str:
    if not status:
        return {
            "invalid-syntax": "Invalid email format.",
            "no-mx": "Domain has no MX record (cannot receive emails).",
        }.get(reason, f"Failed verification: {reason}")
    if "zb-" in reason:
        tag = reason.split("zb-", 1)[1]
        return f"ZeroBounce says: {tag.replace('-', ' ').capitalize()}"
    if "nb-" in reason:
        tag = reason.split("nb-", 1)[1]
        return f"NeverBounce says: {tag.replace('-', ' ').capitalize()}"
    if reason == "smtp-accepted":
        return "SMTP handshake succeeded. Email is deliverable."
    if reason == "mx-valid-no-smtp":
        return "Domain accepts mail but SMTP check was skipped."
    return f"Valid: {reason}"