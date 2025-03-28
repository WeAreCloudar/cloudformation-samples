# Roles Anywhere with a Belgian eID
This templates accompagnie a blog post on the Cloudar blog: https://cloudar.be/awsblog/sign-in-with-your-eid-using-aws-iam-roles-anywhere-with-a-smartcard-reader/

They go a little bit furhter than the explanation there by also supporting the "Foreigner CA", but that does not change any of the functionality.

## Remarks:
- We trust Belgium Root CA 4 and Belgium Root CA 6.
  - 1 and 2 are expired
  - 3 uses sha1WithRSAEncryption, which is not supported by Roles Anywhere
  - 5 does not seem to exist
- CRLS fail to parse, but probably do not make sense to manage here anyway
  - There are a lot of revocation on the CRLs for the Citizen CA / Foreigner CA.
  - Even lost/stolen eIDs are still protected by a PIN.

## Links:
- Belgium Root CA:
  - Root CA 1-4: https://repository.eid.belgium.be/certificates.php?cert=Root&lang=nl
  - Root CA 6: https://repository.eidpki.belgium.be/#/download
