# MARSEL — Integration Architecture

Status: READY FOR CONTROLLED DEPLOYMENT

## Systems
- Wix: public storefront, forms, invoices, catalog.
- Ro App: operational records and workshop accounting.
- OpenAI: AI processing and automation layer.
- GitHub: source control, audit trail and CI/CD.

## Data flow
Wix -> Integration API -> Ro App
Ro App -> Integration API -> Wix
Wix/Ro App -> OpenAI -> normalized content, classification and analysis
All integration code/configuration -> GitHub

## Safety gates
1. READ-only discovery and API inventory.
2. Full export/backup of every writable Ro App entity that the API permits.
3. Schema mapping and duplicate detection.
4. Dry-run diff with zero writes.
5. Small controlled write test.
6. Verification of created/updated records.
7. Enable scheduled synchronization only after successful verification.

## Required secrets
- ROAPP_API_KEY
- WIX credentials/token required by the selected Wix API integration
- OPENAI_API_KEY

Secrets must be stored only in GitHub Actions/host secret storage and environment variables. Never commit secrets.

## Current limitation
The ChatGPT session has GitHub access, but it does not itself expose a generic outbound runtime capable of executing arbitrary live HTTP calls to Ro App. Therefore this repository can contain and validate the integration architecture, while production synchronization requires the deployment runtime to have ROAPP_API_KEY and Wix/OpenAI credentials.

## Production policy
Do not enable destructive operations or mass synchronization until backup, dry-run and verification gates have passed.
