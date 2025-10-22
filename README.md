# FanSense

FanSense: AI-Powered Fan Sentiment Analysis  
A serverless NLP platform that collects fan discussions from Reddit, processes them using AWS Comprehend, and generates AI-driven summaries through a Bedrock Agent trained on S3 data using Retrieval-Augmented Generation (RAG).

---

### ⚙️ Overview  
FanSense automates large-scale fan sentiment analysis across sports communities.  
It scrapes Reddit posts, performs NLP analysis with Comprehend, and summarizes results using a Bedrock-based AI Agent trained directly on its own dataset stored in Amazon S3.  
The system runs fully serverlessly on AWS, achieving scalable orchestration with Lambda triggers and event-based workflows.

---

### 🧩 Architecture  
| Component | Description |
|------------|--------------|
| **scrape_reddit.py** | Collects Reddit posts/comments from r/NFL using PRAW and uploads them to S3. |
| **comprehend_scheduler.py** | Orchestrates batch entity and sentiment detection jobs with Amazon Comprehend. |
| **box.py** | Processes and organizes Comprehend output into structured summaries. |
| **bedrock_summary.py** | Generates team-level insights using an Amazon Bedrock Agent that applies RAG over the S3 dataset. |
| **kb_sync.py** | Keeps the Bedrock knowledge base continuously updated with new S3 data. |
| **lib/fan_sense.ts** | Defines AWS CDK infrastructure for Lambdas, S3, and DynamoDB. |
| **lib/constants.ts** | Loads AWS account and region via environment variables. |
| **bin/fan_sense.ts** | CDK entry point that deploys the full stack. |

---

### ☁️ AWS Infrastructure  
| Service | Role |
|----------|------|
| **Lambda** | Runs all Python and TypeScript microservices. |
| **S3** | Stores raw Reddit data and processed Comprehend output. |
| **DynamoDB** | Maintains team sentiment rankings and summaries. |
| **Comprehend** | Performs sentiment and entity recognition at scale. |
| **Bedrock (RAG Agent)** | Generates contextual insights trained on S3 data through retrieval-augmented prompting. |
| **IAM** | Controls secure service-to-service access. |

---

### 🛠 Setup Instructions  
1. **Install dependencies**
   ```
   npm install
   ```
2. **Create environment file**
   ```
   cp .env.template .env
   ```
   Fill in:
   ```
   REDDIT_CLIENT_ID=
   REDDIT_CLIENT_SECRET=
   REDDIT_USERNAME=
   REDDIT_PASSWORD=
   USER_AGENT=
   AWS_ACCOUNT_ID=
   AWS_REGION=us-east-1
   DOCUMENT_BUCKET_NAME=
   RANKINGS_TABLE_NAME=
   KB_ID=
   DATA_SOURCE_ID=
   ```
3. **Deploy**
   ```
   npm run build
   cdk deploy
   ```

---

### 📦 Technologies  
Python · TypeScript · AWS CDK · Lambda · S3 · DynamoDB · Comprehend · Bedrock (RAG) · PRAW

---

### 🧠 Purpose  
Automate Reddit-based fan sentiment analysis using an AI Agent trained on S3-stored data through Retrieval-Augmented Generation (RAG), enabling intelligent, context-aware summaries with minimal manual analysis.
