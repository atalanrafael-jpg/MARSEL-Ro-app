# ReadMe + Auth0 SAML SSO

Status: configuration runbook; no credentials are stored in this repository.

## Scope

This configures Auth0 as the SAML 2.0 Identity Provider for ReadMe Teammate SSO. ReadMe documents Auth0 SSO as an Enterprise feature.

Official ReadMe procedure: https://docs.readme.com/ent/docs/auth0

## 1. ReadMe values

In the ReadMe Enterprise Group dashboard:

1. Open **Teammates**.
2. Select **SAML** from **Single Sign-On**.
3. Click **Configure**.
4. Record the generated:
   - **Single Sign-On URL**
   - **Entity ID**

Do not commit these values if the project treats them as confidential configuration; store them in the identity-provider/admin configuration instead.

## 2. Auth0 application

In Auth0:

1. Go to **Applications → Applications → Create Application**.
2. Use a clear name such as `ReadMe SSO`.
3. Select **Regular Web Application**.
4. Create the application.
5. Open the application and go to **Addons**.
6. Enable **SAML2 Web App**.
7. In the SAML2 Web App **Settings**:
   - Set **Application Callback URL** to the ReadMe **Single Sign-On URL**.
   - Set the SAML **audience** to the ReadMe **Entity ID**, using the JSON-object format required by Auth0.
8. Enable the SAML addon.

## 3. Return IdP values to ReadMe

In Auth0 SAML2 Web App → **Usage**:

1. Download the Auth0 certificate.
2. Copy the **Identity Provider Login URL**.
3. Return to ReadMe SAML configuration.
4. Put the Auth0 Identity Provider Login URL into ReadMe's **Single Sign-on URL** field.
5. Paste the complete Auth0 certificate contents into **Public Key Certificate**.
6. Save the SAML configuration, then save/exit the ReadMe configuration.

## 4. Claims / attribute mappings

Auth0 must send at minimum:

- `email`
- `name`
- `username`

ReadMe requires these values to sign a teammate into the project. Configure the SAML `mappings` object in Auth0 accordingly.

## 5. Access assignment

In Auth0:

1. Go to **User Management → Roles**.
2. Create a role such as `ReadMe Teammates`.
3. Assign the intended users to that role.

Only users assigned to the Auth0 application/role should be granted access.

## 6. Validation gate

Before enabling SSO for production users, verify:

- ReadMe SAML configuration saves successfully.
- Auth0 SAML addon is enabled.
- Callback URL exactly matches ReadMe's generated SSO URL.
- Audience exactly matches ReadMe's Entity ID.
- Auth0 certificate in ReadMe matches the active Auth0 certificate.
- `email`, `name`, and `username` claims are present.
- A test user can authenticate successfully.
- A non-assigned user cannot access the ReadMe project.
- Logout/redirect behavior is acceptable.

## Security

Never commit Auth0 client secrets, private keys, certificates containing private material, session tokens, or other credentials to this repository. Use protected configuration/secrets storage.

## Limitation

The Auth0 tenant and ReadMe Enterprise Group are external administrative systems. Repository automation can document and validate the configuration, but it cannot create the Auth0 application or enter ReadMe SSO settings unless the corresponding authenticated administrative connector is available.
