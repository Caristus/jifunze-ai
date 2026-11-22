import base64, hashlib, hmac, os, struct, time
def gen_secret():
    return base64.b32encode(os.urandom(10)).decode().rstrip("=")
def _key(secret):
    return base64.b32decode(secret + "=" * (-len(secret) % 8))
def totp(secret, step=30, digits=6, counter=None):
    if counter is None:
        counter = int(time.time() // step)
    h = hmac.new(_key(secret), struct.pack(">Q", counter), hashlib.sha1).digest()
    o = h[-1] & 0x0F
    code = (struct.unpack(">I", h[o:o+4])[0] & 0x7FFFFFFF) % (10 ** digits)
    return str(code).zfill(digits)
def verify(secret, code):
    if not secret or not code:
        return False
    c = int(time.time() // 30)
    return any(hmac.compare_digest(totp(secret, counter=c + d), str(code).strip()) for d in (-1, 0, 1))
def otpauth_uri(secret, username, issuer="JIFUNZE AI"):
    from urllib.parse import quote
    return "otpauth://totp/%s:%s?secret=%s&issuer=%s" % (quote(issuer), quote(username), secret, quote(issuer))
