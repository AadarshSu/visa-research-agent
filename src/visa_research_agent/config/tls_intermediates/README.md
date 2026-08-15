# Intermediate certificates

Some government servers send only their own certificate and omit the intermediate that links it to
a trusted root. Browsers fetch the missing intermediate automatically; Python does not, so the
connection fails even though the certificate is genuine and the site is the real authority.

Supplying the intermediate here fixes that **without weakening verification**. Certificate checking
stays fully on: the site's certificate must still be signed by one of these intermediates, which
must itself be signed by a root already in the trust store.

## Adding one

Only add a certificate that passes this check, and record the result:

```bash
openssl verify -CAfile "$(python -c 'import certifi;print(certifi.where())')" new-intermediate.pem
```

If it does not verify, do not add it. A certificate that cannot be traced to a trusted root is
exactly what verification is meant to reject.

## What is here

| File | Subject | Issued by | Needed for |
| --- | --- | --- | --- |
| `globalsign-rsa-ov-ssl-ca-2018.pem` | GlobalSign RSA OV SSL CA 2018 | GlobalSign Root CA - R3 | `evisa.gov.vn`, Vietnam's official e-visa portal, which serves an organisation-validated certificate issued to Cục Quản lý xuất nhập cảnh (the Vietnam Immigration Department) but omits this intermediate |
