# LINE Bot with Google Gemini File Search

## Project Background

This project is a LINE bot that uses Google Gemini's File Search capabilities to analyze uploaded documents and images. Users can upload files (PDF, DOCX, images, etc.) to the bot, and then ask questions about the content. The bot maintains separate file search stores for each user or group conversation, enabling personalized document-based Q&A.

## Screenshot

![image](https://github.com/user-attachments/assets/2bcbd827-0047-4a3a-8645-f8075d996c10)

## Features

- **File Upload & Processing**: Upload documents and images through LINE
  - Supports document files (PDF, DOCX, TXT, etc.)
  - Supports image files (JPG, PNG, etc.)
  - Automatic file storage management per user/group
- **AI-Powered Document Q&A**: Ask questions about uploaded documents
  - Uses Google Gemini's File Search for accurate answers
  - Context-aware responses based on document content
- **Multi-Conversation Support**:
  - Separate file stores for 1-on-1 conversations (per user)
  - Shared file stores for group conversations (per group)
- **Built with FastAPI**: High-performance async processing
- **Containerized with Docker**: Easy deployment

## Technologies Used

- Python 3.9+
- FastAPI
- LINE Messaging API
- Google Gemini API (with File Search)
- Google VertexAI (optional alternative to Gemini API)
- Docker
- Google Cloud Run (for deployment)

## Setup

1. Clone the repository to your local machine.

2. Set the following environment variables:
   - `ChannelSecret`: Your LINE channel secret
   - `ChannelAccessToken`: Your LINE channel access token
   - For Google Gemini API:
     - `GOOGLE_API_KEY`: Your Google Gemini API key
   - For VertexAI (alternative to Gemini API):
     - `GOOGLE_GENAI_USE_VERTEXAI`: Set to "True" to use VertexAI
     - `GOOGLE_CLOUD_PROJECT`: Your Google Cloud Project ID
     - `GOOGLE_CLOUD_LOCATION`: Your Google Cloud region (e.g., "us-central1")

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI server:

   ```bash
   uvicorn main:app --reload
   ```

5. Set up your LINE bot webhook URL to point to your server's endpoint.

## Usage

### Uploading Files

1. Send a document file or image to the LINE bot
2. The bot will download and upload it to a file search store
3. You'll receive a confirmation message when the upload is complete

### Asking Questions

1. After uploading files, send any text message with your question
2. The bot will search through your uploaded documents
3. You'll receive an AI-generated answer based on the document content

### How File Stores Work

- **1-on-1 Chat**: Each user has their own file store (isolated)
- **Group Chat**: All members in a group share the same file store
- Files are automatically organized by conversation context

## Architecture

```
LINE User → Upload File → LINE Bot → Download → Upload to Gemini File Search Store
                                                          ↓
LINE User ← AI Response ← Query File Search ← Text Question
```

### Key Components

- **`get_store_name()`**: Determines the file search store name based on conversation type
- **`download_line_content()`**: Downloads files from LINE servers
- **`upload_to_file_search_store()`**: Uploads files to Gemini File Search
- **`query_file_search()`**: Queries uploaded documents using AI
- **`handle_file_message()`**: Processes file/image uploads
- **`handle_text_message()`**: Processes text queries

## Deployment Options

### Local Development

Use ngrok or similar tools to expose your local server to the internet for webhook access:

```bash
ngrok http 8000
```

### Docker Deployment

You can use the included Dockerfile to build and deploy the application:

```bash
docker build -t linebot-file-search .
# For Gemini API:
docker run -p 8000:8000 \
  -e ChannelSecret=YOUR_SECRET \
  -e ChannelAccessToken=YOUR_TOKEN \
  -e GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY \
  linebot-file-search

# For VertexAI:
docker run -p 8000:8000 \
  -e ChannelSecret=YOUR_SECRET \
  -e ChannelAccessToken=YOUR_TOKEN \
  -e GOOGLE_GENAI_USE_VERTEXAI=True \
  -e GOOGLE_CLOUD_PROJECT=YOUR_GCP_PROJECT \
  -e GOOGLE_CLOUD_LOCATION=YOUR_GCP_REGION \
  linebot-file-search
```

### Google Cloud Deployment

#### Prerequisites

1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Create a Google Cloud project and enable the following APIs:
   - Cloud Run API
   - Container Registry API or Artifact Registry API
   - Cloud Build API
   - Vertex AI API (if using VertexAI)

#### Steps for Deployment

1. Authenticate with Google Cloud:

   ```bash
   gcloud auth login
   ```

2. Set your Google Cloud project:

   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

3. Build and push the Docker image to Google Container Registry:

   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/linebot-file-search
   ```

4. Deploy to Cloud Run:

   For Gemini API:

   ```bash
   gcloud run deploy linebot-file-search \
     --image gcr.io/YOUR_PROJECT_ID/linebot-file-search \
     --platform managed \
     --region asia-east1 \
     --allow-unauthenticated \
     --set-env-vars ChannelSecret=YOUR_SECRET,ChannelAccessToken=YOUR_TOKEN,GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
   ```

   For VertexAI (recommended for production):

   ```bash
   gcloud run deploy linebot-file-search \
     --image gcr.io/YOUR_PROJECT_ID/linebot-file-search \
     --platform managed \
     --region asia-east1 \
     --allow-unauthenticated \
     --set-env-vars ChannelSecret=YOUR_SECRET,ChannelAccessToken=YOUR_TOKEN,GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=YOUR_GCP_PROJECT,GOOGLE_CLOUD_LOCATION=YOUR_GCP_REGION
   ```

   Note: For production, it's recommended to use Secret Manager for storing sensitive environment variables.

5. Get the service URL:

   ```bash
   gcloud run services describe linebot-file-search --platform managed --region asia-east1 --format 'value(status.url)'
   ```

6. Set the service URL as your LINE Bot webhook URL in the LINE Developer Console.

#### Setting Up Secrets in Google Cloud (Recommended)

For better security, store your API keys as secrets:

1. Create secrets for your sensitive values:

   ```bash
   echo -n "YOUR_SECRET" | gcloud secrets create line-channel-secret --data-file=-
   echo -n "YOUR_TOKEN" | gcloud secrets create line-channel-token --data-file=-

   # For Gemini API
   echo -n "YOUR_GOOGLE_API_KEY" | gcloud secrets create google-api-key --data-file=-
   ```

2. Give the Cloud Run service access to these secrets and deploy with them.

## Maintenance and Monitoring

After deployment, you can monitor your service through the Google Cloud Console:

1. View logs:

   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=linebot-file-search"
   ```

2. Check service metrics: Access the Cloud Run dashboard in Google Cloud Console

3. Set up alerts for error rates or high latency in Cloud Monitoring

## Limitations

- File search stores are persistent in Google Gemini backend
- Each conversation maintains its own file store
- Supported file types depend on Google Gemini File API capabilities

## License

This project is open source and available under the MIT License.
