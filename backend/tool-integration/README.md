# VidSage User Management Service

Production-ready Node.js + TypeScript + Express REST API for Google Docs integration via OAuth 2.0.

## Features

✅ **Google OAuth 2.0** - Authorization Code flow with offline access  
✅ **Google Drive API** - Create and manage documents  
✅ **Google Docs API** - Write AI-generated content to docs  
✅ **Clerk Integration** - Token storage linked to Clerk user IDs  
✅ **Auto Token Refresh** - Automatic access token renewal  
✅ **TypeScript** - Full type safety  
✅ **Security** - Helmet, CORS, rate limiting  
✅ **Production Ready** - Error handling, logging, graceful shutdown

## Prerequisites

- Node.js 18+ and npm
- Google Cloud Project with OAuth 2.0 credentials
- Clerk account (for user authentication)

## Setup

### 1. Install Dependencies

```bash
cd backend/usermng
npm install
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
PORT=4000
NODE_ENV=development

# Google OAuth 2.0 Credentials
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:4000/auth/google/callback

# Frontend URL (for CORS and redirects)
FRONTEND_URL=http://localhost:5173
```

### 3. Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Drive API** and **Google Docs API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Authorized redirect URIs: `http://localhost:4000/auth/google/callback`
7. Copy Client ID and Client Secret to `.env`

### 4. Run the Server

**Development mode (with auto-reload):**

```bash
npm run dev
```

**Production build:**

```bash
npm run build
npm start
```

Server runs on: `http://localhost:4000`

## API Endpoints

### 1. **Initiate Google OAuth**

```http
GET /auth/google?userId={clerkUserId}
```

Redirects user to Google consent screen.

**Parameters:**
- `userId` (query) - Clerk user ID

**Response:** 302 redirect to Google

---

### 2. **OAuth Callback** (Handled automatically)

```http
GET /auth/google/callback?code={code}&state={state}
```

Google redirects here after user consent. Exchanges code for tokens and stores them.

**Response:** 302 redirect to frontend success/error page

---

### 3. **Create Google Doc**

```http
POST /google/docs
Content-Type: application/json

{
  "userId": "clerk_user_id",
  "content": "AI-generated summary text here...",
  "title": "My Summary",  // Optional
  "folderId": "drive_folder_id"  // Optional
}
```

Creates a Google Doc with the provided content.

**Response:**

```json
{
  "success": true,
  "document": {
    "documentId": "1abc...",
    "documentUrl": "https://docs.google.com/document/d/1abc.../edit",
    "title": "My Summary"
  }
}
```

---

### 4. **Check OAuth Status**

```http
GET /google/status?userId={clerkUserId}
```

Check if user has authorized Google access.

**Response:**

```json
{
  "authorized": true,
  "hasRefreshToken": true,
  "tokenExpired": false
}
```

---

### 5. **Revoke Google Access**

```http
DELETE /google/revoke
Content-Type: application/json

{
  "userId": "clerk_user_id"
}
```

Deletes stored tokens and revokes access.

---

### 6. **List User's Google Docs** (Optional)

```http
GET /google/docs/list?userId={clerkUserId}&pageSize=10
```

List documents created by this app.

---

### 7. **Health Check**

```http
GET /health
```

Service health status.

## Frontend Integration

### Step 1: Redirect to OAuth

```typescript
// When user clicks "Connect Google"
const userId = 'clerk_user_id'; // From Clerk
window.location.href = `http://localhost:4000/auth/google?userId=${userId}`;
```

### Step 2: Handle OAuth Success

```typescript
// On /oauth/success page
const isAuthorized = true;
// Show success message and enable "Save to Google Docs" button
```

### Step 3: Create Google Doc

```typescript
const createGoogleDoc = async (content: string) => {
  const response = await fetch('http://localhost:4000/google/docs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      userId: clerkUserId,
      content: content,
      title: 'AI Video Summary',
    }),
  });

  const data = await response.json();
  
  if (data.success) {
    // Open document in new tab
    window.open(data.document.documentUrl, '_blank');
  }
};
```

## Security Considerations

### ⚠️ Production Checklist

- [ ] **Store tokens in database** (MongoDB, PostgreSQL)
- [ ] **Encrypt tokens** before storing
- [ ] **Implement Clerk token verification** in middleware
- [ ] **Use HTTPS** in production
- [ ] **Add rate limiting** (Redis-based)
- [ ] **Set up proper CORS** origins
- [ ] **Add request validation** and sanitization
- [ ] **Implement logging** (Winston, Pino)
- [ ] **Set up monitoring** (Sentry, DataDog)
- [ ] **Add API authentication** (API keys for backend-to-backend)

### Token Storage

**Current:** In-memory Map (development only)

**Production:** Replace with encrypted database storage

See `src/services/token.service.ts` for MongoDB implementation example.

### Environment Variables

Never commit `.env` file. Use secrets management:
- **Development:** `.env` file (gitignored)
- **Production:** Environment variables or secrets manager (AWS Secrets Manager, etc.)

## Project Structure

```
src/
├── index.ts                    # Express app entry point
├── config/
│   └── googleOAuth.ts          # OAuth client configuration
├── middleware/
│   ├── auth.middleware.ts      # Clerk auth validation
│   └── errorHandler.ts         # Global error handler
├── routes/
│   └── google.routes.ts        # Google OAuth & Docs routes
├── services/
│   ├── google.service.ts       # Google API business logic
│   └── token.service.ts        # Token storage (in-memory/DB)
└── types/
    └── index.ts                # TypeScript interfaces
```

## OAuth Flow Diagram

```
User → Frontend → /auth/google?userId=X
                    ↓
              Google Consent Screen
                    ↓
              /auth/google/callback
                    ↓
          Store tokens + userId
                    ↓
         Redirect → Frontend Success
                    ↓
    User clicks "Save to Docs"
                    ↓
        POST /google/docs
                    ↓
      Create Doc → Return URL
```

## Automatic Token Refresh

The service automatically refreshes expired access tokens using the refresh token:

1. Check if `access_token` is expired
2. If expired and `refresh_token` exists, refresh automatically
3. Update stored tokens
4. Proceed with API request

No manual intervention needed!

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Unauthorized",
  "message": "User has not authorized Google access",
  "requiresAuth": true
}
```

HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized (requires OAuth)
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

## Development

**Watch mode:**
```bash
npm run dev
```

**Build:**
```bash
npm run build
```

**Lint:**
```bash
npm run lint
```

**Format:**
```bash
npm run format
```

## Testing with cURL

**Initiate OAuth:**
```bash
curl -L "http://localhost:4000/auth/google?userId=test_user_123"
```

**Create Doc:**
```bash
curl -X POST http://localhost:4000/google/docs \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test_user_123",
    "content": "This is an AI-generated summary.",
    "title": "Test Document"
  }'
```

**Check Status:**
```bash
curl "http://localhost:4000/google/status?userId=test_user_123"
```

## Google OAuth Verification

This implementation follows Google's best practices for OAuth verification:

✅ Uses Authorization Code flow (not implicit)  
✅ Requests `offline` access for refresh tokens  
✅ Uses `consent` prompt to ensure refresh token  
✅ Minimal scopes (`drive.file` only creates files, not full access)  
✅ Secure token storage (when using database)  
✅ Proper error handling  
✅ User can revoke access  

## License

ISC

## Support

For issues, please check:
1. Environment variables are set correctly
2. Google APIs are enabled in Cloud Console
3. Redirect URI matches exactly
4. User has granted consent

---

**Built with ❤️ for VidSage**
