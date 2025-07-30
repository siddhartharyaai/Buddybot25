# 🔐 SECURITY GUIDELINES

## ⚠️ CRITICAL: API Key Security

### NEVER COMMIT THESE FILES:
- `backend/.env` - Contains API keys
- `frontend/.env` - Contains environment variables
- Any file ending in `.env`

### SECURITY CHECKLIST:
- [ ] All `.env` files are in `.gitignore`
- [ ] API keys are never hardcoded in source code
- [ ] API keys have proper restrictions in Google Cloud Console
- [ ] Regular security audits of committed files

### IF API KEY IS EXPOSED:
1. **IMMEDIATELY** regenerate the API key in Google Cloud Console
2. Update the `.env` file with the new key
3. Remove the old key from Git history (see commands above)
4. Force push to overwrite GitHub history
5. Monitor Google Cloud billing for unauthorized usage

### EMERGENCY CONTACT:
- Google Cloud Console: https://console.cloud.google.com/
- Credentials Page: APIs & Services > Credentials

## 🛡️ BEST PRACTICES:
1. **Never paste API keys in chat/email**
2. **Always use environment variables**
3. **Restrict API keys to specific services**
4. **Set usage quotas and alerts**
5. **Regular security reviews**

---
**Remember: Security is everyone's responsibility!**