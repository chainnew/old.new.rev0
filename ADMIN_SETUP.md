# 🛡️ Admin Panel Documentation

Complete administrator dashboard with security, user management, and system monitoring.

---

## 🎯 Features

### 1. **User Management** 👥
- View all registered users (1,247 total)
- Filter by role (Admin, Premium, User)
- Check user status (Active, Suspended, Banned)
- Export user data to CSV
- Edit user permissions
- Ban/suspend users

**Stats Tracked**:
- Total Users
- Active Today
- Premium Members
- Banned Users

---

### 2. **Security & 2FA** 🔒

#### Two-Factor Authentication
- ✅ Enforce 2FA for all admins
- ✅ SMS 2FA support
- ✅ Authenticator app support (Google Authenticator, Authy)
- ✅ Security keys (WebAuthn)

#### Security Methods
- **Security Keys**: YubiKey 5C, Google Titan
- **Phone Numbers**: SMS verification
- **Admin PIN**: 6-digit PIN for extra security
- **Backup Codes**: Recovery codes for lost devices

#### How to Enable 2FA:
1. Click **Admin Panel** in sidebar (🛡️ Shield icon)
2. Go to **Security & 2FA** tab
3. Enable your preferred method
4. Scan QR code or add phone number
5. Verify with test code

---

### 3. **Analytics & Tokenomics** 📊

**Key Metrics**:
- Total Revenue: $47,239 (+18%)
- API Calls: 2.4M (+23%)
- Tokens Used: 15.7B (+31%)
- Avg Response Time: 1.2s (-5%)

**Charts** (coming soon):
- Revenue over time
- Usage trends
- Token consumption
- API performance

---

### 4. **AI Agent Configuration** 🤖

**Adjustable Parameters**:
- **Temperature**: 0-1 (creativity level)
- **Top P**: 0-1 (nucleus sampling)
- **Max Tokens**: 100-4000 (response length)
- **Frequency Penalty**: 0-2 (repetition control)

**Presets**:
- Creative (temp: 0.9, top_p: 0.95)
- Balanced (temp: 0.7, top_p: 0.9)
- Precise (temp: 0.3, top_p: 0.7)

---

### 5. **Database Viewer** 💾

**Connected Database**: PostgreSQL

**Tables**:
- `users` - 1,247 rows
- `conversations` - 8,942 rows
- `messages` - 124,531 rows
- `subscriptions` - 89 rows
- `api_keys` - 156 rows

**Actions**:
- View table schemas
- Run SQL queries
- Export data
- Backup database

---

### 6. **Error Logs** 🚨

**Recent Errors**:
- `ERR_API_TIMEOUT` - API request timeout after 30s
- `ERR_DB_CONNECTION` - Database connection pool exhausted
- `ERR_RATE_LIMIT` - User exceeded rate limit

**Error Levels**:
- 🔴 **Critical**: System-breaking errors
- 🟡 **Warning**: Potential issues
- 🔵 **Info**: Normal operations

**Auto-alerts**: Email admins on critical errors

---

### 7. **Support Tickets** 📧

**Ticket System**:
- Open tickets: 8
- In Progress: 3
- Resolved today: 12

**Ticket Management**:
- Assign to team members
- Add internal notes
- Set priority (Low, Medium, High, Urgent)
- Close with resolution
- Auto-response templates

**Common Issues**:
- Login problems
- Billing issues
- API integration help
- Feature requests

---

### 8. **System Settings** ⚙️

**Toggles**:
- ✅ Maintenance Mode
- ✅ New User Registration
- ✅ Email Notifications
- ✅ API Rate Limiting

**Advanced**:
- SMTP configuration
- Webhook endpoints
- CDN settings
- Cache management

---

## 🚀 Quick Start

### Accessing Admin Panel

1. **Click Shield Icon** (🛡️) in left sidebar
2. **Authenticate** with admin credentials
3. **Browse sections** using left navigation
4. **Make changes** as needed

### Default Admin Login

```
Email: admin@old.new.com
Password: [Set during setup]
2FA: Required
```

---

## 🔐 Security Best Practices

### For Admins:
1. ✅ Enable 2FA (required)
2. ✅ Use security key (YubiKey recommended)
3. ✅ Set strong password (16+ characters)
4. ✅ Enable admin PIN
5. ✅ Save backup codes securely
6. ✅ Review access logs monthly

### For System:
1. ✅ Enforce 2FA for all admins
2. ✅ Log all admin actions
3. ✅ Rate limit admin API
4. ✅ Session timeout: 30 minutes
5. ✅ IP whitelist (optional)
6. ✅ Auto-logout on suspicious activity

---

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  role VARCHAR(50) DEFAULT 'user',
  status VARCHAR(50) DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP,
  two_factor_enabled BOOLEAN DEFAULT FALSE,
  phone_number VARCHAR(20),
  security_key_id VARCHAR(255)
);
```

### Audit Logs
```sql
CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  admin_id INTEGER REFERENCES users(id),
  action VARCHAR(255) NOT NULL,
  target_user_id INTEGER REFERENCES users(id),
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🎨 UI Sections

### Navigation Sidebar
- 👥 User Management
- 🔒 Security & 2FA
- 📊 Analytics
- ⚡ Agent Config
- 💾 Database
- 🚨 Error Logs
- 📧 Support Tickets
- ⚙️ Settings

### Color Coding
- 🟢 Green: Active/Success
- 🟡 Yellow: Warning/Pending
- 🔴 Red: Error/Critical
- 🟣 Purple: Admin/Premium
- ⚪ Gray: Inactive/Default

---

## 🔧 API Endpoints

### Admin API (Protected)

```typescript
// Get all users
GET /api/admin/users
Headers: { Authorization: Bearer <admin_token> }

// Update user role
PATCH /api/admin/users/:id/role
Body: { role: 'admin' | 'premium' | 'user' }

// Ban user
POST /api/admin/users/:id/ban
Body: { reason: string }

// Get analytics
GET /api/admin/analytics
Query: { from: date, to: date }

// Get error logs
GET /api/admin/errors
Query: { level: 'critical' | 'warning' | 'info', limit: number }
```

---

## 🛠️ Setup Checklist

### Initial Setup:
- [ ] Create admin user account
- [ ] Enable 2FA
- [ ] Add security key
- [ ] Set admin PIN
- [ ] Configure SMTP for emails
- [ ] Set up database backups
- [ ] Configure error alerting
- [ ] Test support ticket system
- [ ] Review user permissions
- [ ] Set rate limits

### Maintenance:
- [ ] Weekly: Review error logs
- [ ] Weekly: Check support tickets
- [ ] Monthly: User audit
- [ ] Monthly: Security review
- [ ] Quarterly: Database optimization
- [ ] Yearly: Security key rotation

---

## 🚨 Emergency Actions

### If Compromised:
1. Enable Maintenance Mode
2. Force logout all users
3. Reset admin passwords
4. Review audit logs
5. Contact security team
6. Patch vulnerabilities
7. Notify affected users

### If Database Down:
1. Check error logs
2. Verify connection pool
3. Restart database service
4. Check disk space
5. Review slow queries
6. Scale if needed

---

## 📞 Support

**Admin Support**: admin@old.new.com  
**Emergency**: Call security team  
**Documentation**: /docs/admin  

---

**Last Updated**: 2025-10-08  
**Version**: 1.0  
**Author**: old.new team
