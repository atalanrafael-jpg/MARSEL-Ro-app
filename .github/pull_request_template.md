## MARSEL / ROAPP PR

### Change
- What changed?
- Why is the change required?

### Verification
- [ ] Relevant tests/CI run or reason documented
- [ ] Copilot review requested where available
- [ ] No production WRITE performed unless explicitly authorized and independently verified
- [ ] READ-ONLY evidence preserved where applicable
- [ ] No secrets, credentials, tokens, or personal data added
- [ ] API identifiers and contracts are confirmed, not guessed
- [ ] Security-sensitive changes received appropriate review
- [ ] Production gate remains enabled

### Compatibility
- [ ] Existing canonical implementation reused where applicable
- [ ] No duplicate/versioned implementation introduced without justification
- [ ] Backward compatibility checked for API/data-contract changes

### Safety
- Production mutation: `NO` unless explicitly authorized and independently verified.
- If evidence is incomplete: status must remain `REVIEW_REQUIRED`.
- Do not merge by bypassing required checks or reviews.
