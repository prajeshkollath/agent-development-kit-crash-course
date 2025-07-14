# Google Calendar Agent - Cloud Run Deployment Guide

## ✅ **What's New: Service Account Authentication**

Your calendar agent now uses **service account credentials** stored in the ADK session state (Supabase database), making it perfect for Cloud Run deployment without browser dependencies!

## **🚀 Deployment Steps**

### **1. Deploy to Cloud Run**
```bash
cd 18-api-agent-auth-memory
adk deploy cloud_run \
  --project=720678319427 \
  --region=asia-south1 \
  --service-name=calendar-agent \
  --app-name=calendar-app \
  --session-db-url="postgresql://your-supabase-url" \
  tool_agent
```

### **2. Create Service Account** ⚠️ **DO THIS FIRST**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Enable **Google Calendar API**
4. Go to **IAM & Admin** → **Service Accounts**
5. Click **Create Service Account**
6. Name it "calendar-agent" and click **Create and Continue**
7. **Grant Permissions**: 
   - Click **Select a role**
   - Search for "Calendar" or "Calendar API"
   - Choose **"Calendar API Admin"** (for full access) OR
   - Choose **"Editor"** (if Calendar roles aren't available)
   - Click **Continue** and **Done**
8. Click on the created service account name
9. Go to **Keys** tab → **Add Key** → **Create new key** → **JSON**
10. Download the JSON key file and copy the entire content

### **3. Set Up Service Account Credentials in Agent** ⚠️ **DO THIS AFTER STEP 2**

After deployment and creating your service account, configure it in session state:

#### **Option A: Via API Call**
```bash
curl -X POST "https://your-cloud-run-url/run" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "session_id": "session123",
    "new_message": {
      "role": "user",
      "parts": [{"text": "Set up Google Calendar service account credentials with service_account_json={\"type\":\"service_account\",\"project_id\":\"your-project-id\",\"private_key_id\":\"abc123\",\"private_key\":\"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n\",\"client_email\":\"calendar-agent@your-project-id.iam.gserviceaccount.com\",\"client_id\":\"123456789\",\"auth_uri\":\"https://accounts.google.com/o/oauth2/auth\",\"token_uri\":\"https://oauth2.googleapis.com/token\",\"auth_provider_x509_cert_url\":\"https://www.googleapis.com/oauth2/v1/certs\",\"client_x509_cert_url\":\"https://www.googleapis.com/robot/v1/metadata/x509/calendar-agent%40your-project-id.iam.gserviceaccount.com\"}"}]
    }
  }'
```

#### **Option B: Via Web UI**
1. Open your deployed agent URL
2. Send message: "Set up Google Calendar service account credentials with service_account_json=YOUR_SERVICE_ACCOUNT_JSON_CONTENT"

## **🔧 How It Works**

### **Service Account Storage**
- **Service Account JSON**: Stored in `google_calendar_service_account` key
- **Base64 Encoded**: All sensitive data is encoded for security
- **Persistent**: Survives Cloud Run restarts via Supabase
- **No Browser Required**: Works in headless Cloud Run environments

### **Authentication Flow**
1. **First Request**: Agent checks for stored service account credentials
2. **No Credentials**: Returns setup instructions
3. **Setup Complete**: Uses service account for API calls
4. **Subsequent Requests**: Uses stored credentials automatically

## **🛠️ Available Tools**

### **1. Calendar Events Tool**
- **Function**: `get_calendar_events`
- **Purpose**: Fetch upcoming calendar events
- **Authentication**: Service account (no browser required)

### **2. Setup Credentials Tool**
- **Function**: `setup_calendar_credentials`
- **Purpose**: Configure service account credentials in session state
- **Parameters**: `service_account_json` (full JSON content)

## **📝 Example Usage**

### **Setup Service Account**
```
User: "Set up Google Calendar service account credentials with service_account_json={\"type\":\"service_account\",\"project_id\":\"your-project-id\",\"private_key_id\":\"abc123\",\"private_key\":\"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n\",\"client_email\":\"calendar-agent@your-project-id.iam.gserviceaccount.com\",\"client_id\":\"123456789\",\"auth_uri\":\"https://accounts.google.com/o/oauth2/auth\",\"token_uri\":\"https://oauth2.googleapis.com/token\",\"auth_provider_x509_cert_url\":\"https://www.googleapis.com/oauth2/v1/certs\",\"client_x509_cert_url\":\"https://www.googleapis.com/robot/v1/metadata/x509/calendar-agent%40your-project-id.iam.gserviceaccount.com\"}"
```

### **Get Calendar Events**
```
User: "Get my upcoming calendar events"
```

## **🔒 Security Features**

- ✅ **Base64 Encoding**: Sensitive data encoded in session state
- ✅ **Service Account**: No browser authentication required
- ✅ **Session Isolation**: Each user has separate credentials
- ✅ **No Local Files**: No sensitive files in Cloud Run container
- ✅ **Cloud Run Compatible**: Works in headless environments

## **🚨 Troubleshooting**

### **"Service account credentials not configured"**
- Run the setup credentials tool first
- Ensure service account JSON is complete and valid

### **"Invalid service account JSON"**
- Check that the JSON contains all required fields
- Ensure `type` field is set to `"service_account"`

### **"Failed to fetch calendar events"**
- Verify service account has Calendar API permissions
- Check if the service account email has access to the calendar

## **🎉 Benefits of Service Account Approach**

1. **Cloud Run Compatible**: No browser dependencies
2. **Multi-User Support**: Each user can have separate service accounts
3. **Persistent Storage**: Credentials survive container restarts
4. **Secure**: Encoded storage in Supabase
5. **Scalable**: Works with multiple Cloud Run instances
6. **No OAuth Flow**: Direct API access without user interaction

Your calendar agent is now ready for production deployment with service account authentication! 🚀 