# Usage Guide

## Overview

The Social Support Application System automates the application process for social security support. This guide explains how to use the system.

## User Workflows

### 1. Submitting a New Application

1. **Access the Application Portal**
   - Open http://localhost:8501 in your browser
   - Navigate to "New Application"

2. **Upload Required Documents**
   - **Application Form** (Required): PDF or image of completed form
   - **Bank Statement** (Optional): PDF or image
   - **Emirates ID** (Optional): PDF or image
   - **Resume/CV** (Optional): PDF or DOCX
   - **Assets/Liabilities** (Optional): Excel file
   - **Credit Report** (Optional): PDF

3. **Submit Application**
   - Click "Submit Application"
   - Note your Application ID (format: APP-XXXXXXXXXXXX)
   - Processing begins automatically

4. **Wait for Processing**
   - Processing typically takes a few minutes
   - You can check status or chat with assistant

### 2. Checking Application Status

1. **Navigate to "Application Status"**
2. **Enter Application ID** (not auto-filled)
3. **View Status**
   - Status: pending, processing, completed, or failed
   - Eligibility Assessment: Score, income level, family size, recommendation
   - Final Decision & Explanation: Applicant-facing decision explanation with reasoning

### 3. Using the Chat Assistant

1. **Navigate to "Chat Assistant"**
2. **Enter or Edit Application ID** (editable field for context)
3. **Ask Questions**
   - "What documents do I need?"
   - "What is the status of my application?"
   - "What are the eligibility criteria?"
   - "What is my application ID?"

4. **Quick Actions**
   - Use quick action buttons for common questions

## API Usage

### Submit Application

```bash
curl -X POST "http://localhost:8000/api/v1/application/submit" \
  -F "application_form=@form.pdf" \
  -F "bank_statement=@statement.pdf" \
  -F "emirates_id=@id.jpg"
```

### Get Application Status

```bash
curl "http://localhost:8000/api/v1/application/APP-XXXXXXXXXXXX"
```

### Chat with Assistant

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What documents do I need?",
    "session_id": "session-123"
  }'
```

## Understanding Results

### Application Status

- **pending**: Application submitted, not yet processed
- **processing**: Currently being analyzed by AI agents
- **completed**: Processing finished, recommendation available
- **failed**: Error occurred during processing

### Eligibility Assessment

The system provides:
- **Eligibility Score**: 0-1 (higher is better)
- **Recommendation**: approve, conditional_approve, soft_decline, or decline
- **Reasoning**: Detailed explanation
- **Support Amount**: Recommended financial support (if approved)
- **Enablement Recommendations**: Upskilling, job matching, career counseling

### Data Quality

- **Quality Score**: 0-1 (higher is better)
- **Completeness**: Percentage of required documents
- **Consistency**: Cross-document validation results

## Best Practices

### Document Preparation

1. **Clear Scans**: Ensure documents are clearly scanned/photographed
2. **Complete Forms**: Fill out all required fields
3. **Recent Documents**: Use recent bank statements and reports
4. **Correct Format**: Use supported file formats

### Application Submission

1. **Complete Information**: Provide all available documents
2. **Save Application ID**: Keep your Application ID for reference
3. **Check Status**: Regularly check application status
4. **Use Chat**: Ask questions if unsure about anything

## Troubleshooting

### Application Stuck in Processing

1. Check API logs for errors
2. Verify Ollama is running
3. Check database connections
4. Review extracted data for issues

### Poor Extraction Results

1. Ensure documents are clear and readable
2. Use proper file formats
3. Check OCR quality for scanned documents
4. Verify document completeness

### Chat Assistant Not Responding

1. Check Ollama service is running
2. Verify model is downloaded
3. Check API connectivity
4. Review API logs

## Advanced Features

### Batch Processing

For processing multiple applications:

```python
import requests

applications = [
    {"application_form": "form1.pdf", ...},
    {"application_form": "form2.pdf", ...}
]

for app in applications:
    response = requests.post(
        "http://localhost:8000/api/v1/application/submit",
        files=app
    )
    print(response.json())
```

### Custom Integration

The API can be integrated into existing systems:

```python
from agents.orchestrator import MasterOrchestrator

orchestrator = MasterOrchestrator()
result = orchestrator.process_application(
    application_id="APP-123",
    documents={"application_form": "path/to/form.pdf"}
)
```

## Support

For issues or questions:
1. Check documentation in `docs/` directory
2. Review API documentation at http://localhost:8000/docs
3. Check logs in `logs/` directory
4. Review error messages in application status

