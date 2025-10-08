# 🔐 Authentication Setup Guide

Complete guide to set up OAuth authentication with GitHub, Google, and xAI.

---

## 📦 Step 1: Install NextAuth.js

```bash
npm install next-auth
```

---

## 🔑 Step 2: Generate NextAuth Secret

```bash
openssl rand -base64 32
```

Add to `.env.local`:
```
NEXTAUTH_SECRET=<your_generated_secret>
NEXTAUTH_URL=http://localhost:3000
```

---

## 🐙 Step 3: GitHub OAuth Setup

### Create GitHub OAuth App

1. Go to https://github.com/settings/developers
2. Click **"New OAuth App"**
3. Fill in:
   - **Application name**: `old.new.rev0`
   - **Homepage URL**: `http://localhost:3000`
   - **Authorization callback URL**: `http://localhost:3000/api/auth/callback/github`
4. Click **"Register application"**
5. Copy the **Client ID**
6. Generate a **Client Secret**

### Add to `.env.local`:

```bash
GITHUB_ID=your_github_client_id_here
GITHUB_SECRET=your_github_client_secret_here
```

---

## 🌐 Step 4: Google OAuth Setup

### Create Google OAuth Credentials

1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Go to **APIs & Services** → **Credentials**
4. Click **"Create Credentials"** → **"OAuth Client ID"**
5. Configure consent screen if needed
6. Choose **"Web application"**
7. Add authorized redirect URI:
   ```
   http://localhost:3000/api/auth/callback/google
   ```
8. Copy **Client ID** and **Client Secret**

### Add to `.env.local`:

```bash
GOOGLE_ID=your_google_client_id_here
GOOGLE_SECRET=your_google_client_secret_here
```

---

## ✨ Step 5: xAI OAuth (Coming Soon)

xAI OAuth is not yet publicly available. When it is, add:

```bash
XAI_ID=your_xai_client_id
XAI_SECRET=your_xai_client_secret
```

---

## 📧 Step 6: Email Provider (Optional)

For magic link emails, add SMTP credentials:

```bash
EMAIL_SERVER_HOST=smtp.gmail.com
EMAIL_SERVER_PORT=587
EMAIL_SERVER_USER=your_email@gmail.com
EMAIL_SERVER_PASSWORD=your_app_password
EMAIL_FROM=noreply@old.new.com
```

**Gmail Users**: Use App Password, not regular password
- https://myaccount.google.com/apppasswords

---

## 🎯 Step 7: Test Authentication

1. Start your dev server:
   ```bash
   npm run dev
   ```

2. Open http://localhost:3000

3. Click the **user icon** in sidebar (top-left)

4. Try signing in with:
   - GitHub
   - Google  
   - Email

---

## 🔗 GitHub Integration Scopes

The GitHub provider requests these scopes:
- `read:user` - Read user profile
- `user:email` - Access email
- `repo` - Access repositories (for GitHub panel)

To modify scopes, edit:
```typescript
// app/api/auth/[...nextauth]/route.ts
authorization: {
  params: {
    scope: 'read:user user:email repo'
  }
}
```

---

## 🛡️ Production Deployment

### Update Callback URLs

For production (e.g., Vercel):

1. **GitHub OAuth**: Add callback
   ```
   https://your-domain.com/api/auth/callback/github
   ```

2. **Google OAuth**: Add authorized redirect URI
   ```
   https://your-domain.com/api/auth/callback/google
   ```

3. **Update `.env` on hosting**:
   ```bash
   NEXTAUTH_URL=https://your-domain.com
   ```

---

## 🔍 Troubleshooting

### "Invalid Callback URL"
- Double-check callback URL matches exactly in OAuth app settings
- Ensure `NEXTAUTH_URL` is correct in `.env.local`

### "Client ID Not Found"
- Verify environment variables are set correctly
- Restart dev server after changing `.env.local`

### GitHub Scopes Not Working
- Re-authorize the app to get new scopes
- Check scope configuration in `route.ts`

---

## ✅ Complete Environment File

Your `.env.local` should look like:

```bash
# Grok API
XAI_API_KEY=your_grok_api_key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/old_new_db

# NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_secret_from_openssl

# GitHub OAuth
GITHUB_ID=abc123xyz
GITHUB_SECRET=secret_key_here

# Google OAuth  
GOOGLE_ID=123456789.apps.googleusercontent.com
GOOGLE_SECRET=gocspx-abc123xyz

# Email (Optional)
EMAIL_SERVER_HOST=smtp.gmail.com
EMAIL_SERVER_PORT=587
EMAIL_SERVER_USER=you@gmail.com
EMAIL_SERVER_PASSWORD=your_app_password
EMAIL_FROM=noreply@old.new.com

# App
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

## 🎉 You're Ready!

Authentication is now fully configured! Users can:
- Sign in with GitHub, Google, or Email
- Access GitHub repos and commits
- Customize their profile
- Join the #old.new public channel

**Next Steps:**
- Test each OAuth provider
- Customize profile settings
- Explore GitHub integration panel

---

**Last Updated**: 2025-10-08  
**Version**: 1.0  
**Author**: chainnew
