# DeployEcho Bot

## Overview

DeployEcho Bot automatically posts Jenkins automation results into the correct deployment thread in Slack.

### Current Process

Engineers manually copy automation results from:

- prod automation results

to the appropriate deployment thread in:

- prod deployment

### Automated Process

DeployEcho Bot performs this automatically.

---

## Architecture

```text
Jenkins
   ↓
prod automation results
   ↓
DeployEcho Bot
   ↓
Extract Environment
   ↓
Find Deployment Thread
   ↓
Post Thread Reply
   ↓
prod deployment
```

---

## Example

### Deployment Message

```text
🚀 26DCR2.2.0 digital-cloud-us-prem 🚀
```

### Automation Result

```text
md-mobile-automation (iOS): FAILED

Environment: digital-cloud-us-prem
PASSED: 1
FAILED: 3
```

### Result

DeployEcho Bot automatically replies within the deployment thread.

---

## Required Slack Permissions

### Public Channels

- channels:read
- channels:history

### Private Channels

- groups:read
- groups:history

### Posting

- chat:write

---

## Required Environment Variables

```env
SLACK_BOT_TOKEN=
SLACK_APP_TOKEN=
DEPLOYMENT_CHANNEL=
AUTOMATION_CHANNEL=
```

---

## Running Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python app/bot.py
```

---

## Running with Docker

Build:

```bash
docker build -t deployecho-bot .
```

Run:

```bash
docker run \
-e SLACK_BOT_TOKEN=xxx \
-e SLACK_APP_TOKEN=xxx \
-e DEPLOYMENT_CHANNEL=xxx \
-e AUTOMATION_CHANNEL=xxx \
deployecho-bot
```

---

## Deployment

Supported deployment targets:

- Kubernetes
- Azure App Service
- Linux VM
- Docker

---

## Logging

Example logs:

```text
Environment=digital-cloud-us-prem
Thread Found=1749973728.123456
Message Posted Successfully
```

---

## Future Enhancements

- Persistent cache
- Deployment status dashboard
- Metrics and monitoring
- Multiple deployment channels
- Release tracking