# Đề tài thực tập AI Engineer — 10 tuần

> Dành cho 2 thực tập sinh AI Engineer  
> Mentor: [Tên bạn]  
> Thời gian: 10 tuần

---

## MỤC LỤC

1. [Đề tài 1 — AI Scrum Master (Jimbo)](#đề-tài-1--ai-scrum-master-jimbo)
2. [Đề tài 2 — HR Knowledge Bot](#đề-tài-2--hr-knowledge-bot)
3. [Roadmap 10 tuần chung](#roadmap-10-tuần-chung)
4. [Tiêu chí đánh giá](#tiêu-chí-đánh-giá)
5. [Appendix — Các đề tài mở rộng](#appendix--các-đề-tài-mở-rộng)
   - A1. Auto Code Review
   - A2. Research Assistant
   - A3. Chatbot Chăm sóc KH 24/7
   - A4. Phân loại & Điều hướng yêu cầu
   - A5. Trích xuất Báo cáo Tài chính
   - A6. Rà soát Hợp đồng
   - A7. Phát hiện Gian lận AML
   - A8. Sàng lọc CV Ứng viên
   - A9. Predictive Maintenance
   - A10. Tối ưu Kho bãi

---

# Đề tài 1 — AI Scrum Master (Jimbo)

## 1. Ý nghĩa bài toán

### Vấn đề thực tế
Trong một team phần mềm, Scrum Master / Project Manager phải thực hiện thủ công:

- Đọc email/message yêu cầu từ khách hàng — thường mơ hồ, thiếu thông tin
- Hỏi lại khách hàng để làm rõ yêu cầu
- Tự viết User Stories theo đúng format
- Ước tính Story Points
- Tạo task trên Jira/Trello và assign cho đúng người
- Cập nhật tiến độ sprint

Quá trình này tốn **2–4 giờ mỗi sprint**, lặp đi lặp lại và dễ thiếu sót khi khối lượng yêu cầu lớn.

### Tại sao không dùng ML/DL thuần?
ML/DL thuần túy chỉ giải quyết **một bước** trong quy trình:

| Phương pháp | Làm được | Không làm được |
|---|---|---|
| NLP Classifier | Phân loại loại yêu cầu | Viết User Story hoàn chỉnh |
| Text Summarization | Tóm tắt email | Hỏi thêm khi thiếu thông tin |
| Rule-based Automation | Tạo task theo template cố định | Xử lý yêu cầu mơ hồ, đa dạng |

**AI Agent giải quyết cả quy trình**:
```
Đọc email mơ hồ
→ Nhận ra thiếu thông tin
→ Tra tài liệu kỹ thuật nội bộ để bổ sung ngữ cảnh
→ Viết User Story đúng format của team
→ Tự kiểm tra lại chất lượng
→ Tạo task trên Jira
→ Thông báo cho dev qua Slack
```

---

## 2. Định nghĩa rõ Input / Output

### Input
```
Nguồn 1 — Email/message từ khách hàng:
"Chúng tôi muốn người dùng có thể đăng nhập bằng tài khoản Google 
thay vì phải tạo tài khoản mới. Cần nhanh vì tuần sau demo investor."

Nguồn 2 — Tài liệu kỹ thuật nội bộ (có sẵn trong RAG):
- Stack: Node.js + PostgreSQL + React
- Auth hiện tại: JWT local
- API docs: Swagger nội bộ
```

### Output
```
USER STORY #1
─────────────────────────────────────────────
Title: Google OAuth Login
Priority: High | Story Points: 5 | Sprint: Sprint 12

User Story:
As a new user, I want to login with my Google account,
so that I don't need to create a separate account.

Acceptance Criteria:
✓ Given user clicks "Login with Google"
  When they authorize on Google popup
  Then they are redirected back and logged in within 3s

✓ Given user logs in for the first time
  When OAuth completes successfully
  Then a user profile is auto-created with Google info

✓ Given Google token is invalid or expired
  When login fails
  Then show error message: "Login failed. Please try again."

✓ Given existing user logs in with Google
  When email matches existing account
  Then accounts are merged automatically

Tasks tạo tự động trên Jira:
  [BE-001] Setup Google OAuth2 credentials in GCP Console — 2h
  [BE-002] Implement /auth/google endpoint — 4h  
  [BE-003] Handle token verification & user creation — 3h
  [FE-001] Add "Login with Google" button component — 2h
  [FE-002] Handle OAuth callback redirect — 2h
  [QA-001] Write integration tests for OAuth flow — 3h

Assigned: BE → @backend_dev | FE → @frontend_dev | QA → @qa_engineer
Due: 2025-05-23
─────────────────────────────────────────────
```

---

## 3. Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────────────┐
│                        INPUT                                │
│   Email KH / Slack message / Jira comment                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   RESEARCHER AGENT                          │
│   Query ChromaDB → lấy: stack tech, API docs, DoD,         │
│   các User Story cũ tương tự, quy trình team               │
└────────────────────────┬────────────────────────────────────┘
                         │ Context đầy đủ
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    PLANNER AGENT                            │
│   - Phân rã yêu cầu thành User Stories                     │
│   - Viết Acceptance Criteria                                │
│   - Ước tính Story Points                                   │
│   - Phân chia Tasks theo BE/FE/QA                          │
└────────────────────────┬────────────────────────────────────┘
                         │ Draft User Stories
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   EVALUATOR AGENT                           │
│   - AC có đủ Given/When/Then không?                        │
│   - Story Points có hợp lý không?                          │
│   - Task có bị thiếu hoặc chồng chéo không?               │
│   - Có vi phạm Definition of Done không?                   │
└────────────────────────┬────────────────────────────────────┘
                         │ Approved / Revision needed
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               HUMAN APPROVAL (30 giây)                      │
│   PM review → approve hoặc chỉnh sửa nhỏ                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      ACTION                                 │
│   → Tạo Issues trên Jira/GitLab tự động                    │
│   → Gửi thông báo Slack cho team                           │
│   → Cập nhật Sprint Board                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Tại sao cần AI Agent (không phải chỉ LLM đơn thuần)

| Tình huống | LLM đơn thuần | AI Agent |
|---|---|---|
| Email thiếu thông tin stack tech | Đoán mò hoặc hỏi user | Tự tra tài liệu kỹ thuật trong RAG |
| Story Points ước tính sai | Không biết | Evaluator kiểm tra lại, yêu cầu revision |
| Jira API lỗi 401 | Dừng lại | Tự retry với token mới |
| Yêu cầu quá lớn, cần chia sprint | Xử lý 1 lần | Tự chia thành nhiều US nhỏ hơn |
| Tạo task xong cần thông báo Slack | Không làm được | Tool use → gọi Slack API |

---

## 5. Dữ liệu cần thiết

### 5.1 Dữ liệu nạp vào RAG (Knowledge Base)

| Tài liệu | Mục đích | Link / Nguồn |
|---|---|---|
| Scrum Guide 2020 PDF | Agent hiểu đúng định nghĩa US, Sprint, AC | scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf |
| Atlassian — Cách viết User Story | Format và ví dụ mẫu | atlassian.com/agile/project-management/user-stories |
| Atlassian — Sprint Planning | Quy trình lên kế hoạch | atlassian.com/agile/scrum/sprint-planning |
| Tài liệu kỹ thuật dự án (nội bộ) | Agent biết stack, DB, kiến trúc | Wiki / README nội bộ |
| API Docs (Swagger) | Ước tính task BE chính xác | Swagger nội bộ / export JSON |
| Definition of Done | Biết task nào cần test, review | Team tự viết |
| User Stories cũ đã approve | Học style viết của team | Export từ Jira (CSV) |

**Tải Scrum Guide:**
```bash
curl -L "https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf" -o data/scrum_guide.pdf
```

**Crawl Atlassian docs:**
```python
from langchain_community.document_loaders import WebBaseLoader

urls = [
    "https://www.atlassian.com/agile/project-management/user-stories",
    "https://www.atlassian.com/agile/scrum/sprint-planning",
    "https://www.atlassian.com/agile/scrum/user-stories",
]
docs = WebBaseLoader(urls).load()
```

### 5.2 Dữ liệu mẫu / Training Reference

| Dataset | Mô tả | Link |
|---|---|---|
| SWE-bench | 2,294 GitHub Issues thật + resolution | huggingface.co/datasets/princeton-nlp/SWE-bench |
| Jira Issues dataset | Issues thật từ các dự án mã nguồn mở | huggingface.co/datasets/nvdimchuk/jira-issues-dataset |
| Agile Stories dataset | User Stories mẫu đa dạng lĩnh vực | Tổng hợp từ GitHub public repos |

```bash
python -c "
from datasets import load_dataset
ds = load_dataset('princeton-nlp/SWE-bench', split='test[:50]')
ds.to_json('data/swe_bench_sample.jsonl')
print('Done:', len(ds), 'samples')
"
```

### 5.3 Ground Truth (tự tạo — quan trọng nhất)

Tạo **30 cặp** theo cấu trúc:
```json
{
  "id": "GT-001",
  "input_email": "Chúng tôi muốn thêm tính năng đặt lại mật khẩu qua email...",
  "context": {
    "stack": "Node.js + PostgreSQL",
    "current_auth": "JWT",
    "sprint": "Sprint 12"
  },
  "expected_output": {
    "user_story": "As a registered user, I want to reset my password via email...",
    "story_points": 3,
    "acceptance_criteria": ["Given...", "When...", "Then..."],
    "tasks": ["[BE] Setup email service", "[BE] Create reset token endpoint", "..."]
  }
}
```

---

## 6. Tech Stack

```
LLM (Local):        deepseek-r1:7b qua Ollama
Embedding:          nomic-embed-text qua Ollama  
Vector DB:          ChromaDB (local)
Agent Framework:    CrewAI
Tool Integration:   Jira REST API / GitLab API
Notification:       Slack Webhook
Interface:          Streamlit (demo) hoặc Slack Bot
Monitoring:         Langfuse (self-hosted)
Package:            Docker
```

### Yêu cầu phần cứng tối thiểu
```
RAM:  16GB
GPU:  NVIDIA 8GB VRAM (RTX 3060 trở lên)
      Hoặc chạy CPU với model gemma3:4b (chậm hơn)
Disk: 20GB trống cho models
```

---

## 7. Cấu trúc thư mục dự án

```
jimbo/
├── data/
│   ├── raw/                    # Tài liệu gốc (PDF, DOCX)
│   ├── processed/              # Sau khi chunk + clean
│   └── ground_truth.json       # 30 cặp test thủ công
├── knowledge/
│   ├── ingest.py               # Nạp tài liệu vào ChromaDB
│   └── chroma_db/              # Vector store
├── agents/
│   ├── researcher.py           # Query RAG lấy context
│   ├── planner.py              # Viết User Stories
│   └── evaluator.py            # Kiểm tra chất lượng
├── tools/
│   ├── jira_tool.py            # Tạo/cập nhật Jira issues
│   ├── slack_tool.py           # Gửi thông báo Slack
│   └── search_tool.py          # Tìm kiếm trong ChromaDB
├── crew.py                     # Điều phối toàn bộ agents
├── evaluate.py                 # Chạy đánh giá với ground truth
├── app.py                      # Streamlit UI
├── Dockerfile
└── requirements.txt
```

---

## 8. Code mẫu

### 8.1 Nạp dữ liệu vào RAG
```python
# knowledge/ingest.py
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

def ingest(docs_path: str = "data/raw", persist_dir: str = "knowledge/chroma_db"):
    # Load PDF
    pdf_loader = PyPDFLoader(f"{docs_path}/scrum_guide.pdf")
    
    # Load web
    web_loader = WebBaseLoader([
        "https://www.atlassian.com/agile/project-management/user-stories",
    ])
    
    docs = pdf_loader.load() + web_loader.load()
    
    # Chunk
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    
    # Embed và lưu
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    Chroma.from_documents(chunks, embeddings, persist_directory=persist_dir)
    print(f"Ingested {len(chunks)} chunks")

if __name__ == "__main__":
    ingest()
```

### 8.2 Định nghĩa Agents
```python
# agents/planner.py
from crewai import Agent
from langchain_community.llms import Ollama

llm = Ollama(model="deepseek-r1:7b", temperature=0.1)

planner = Agent(
    role="Senior Scrum Master",
    goal="Phân rã yêu cầu khách hàng thành User Stories rõ ràng, có thể thực hiện được",
    backstory="""Bạn là Scrum Master với 10 năm kinh nghiệm trong các team Agile.
    Bạn luôn viết User Stories theo format chuẩn:
    'As a [user], I want [goal], so that [reason]'
    Mỗi US phải có Acceptance Criteria đầy đủ theo format Given/When/Then.
    Story Points theo thang Fibonacci: 1, 2, 3, 5, 8, 13.
    Tasks phải được phân chia rõ theo BE/FE/QA.""",
    llm=llm,
    verbose=True
)
```

```python
# agents/evaluator.py
from crewai import Agent
from langchain_community.llms import Ollama

llm = Ollama(model="deepseek-r1:7b", temperature=0)

evaluator = Agent(
    role="QA Lead & Scrum Coach",
    goal="Đảm bảo User Stories đạt chất lượng trước khi đưa vào sprint",
    backstory="""Bạn là người review nghiêm khắc. Checklist bắt buộc:
    1. User Story có đủ As a / I want / So that không?
    2. Mỗi AC có đủ Given / When / Then không?
    3. Story Points có hợp lý với độ phức tạp không?
    4. Tasks có bị thiếu hoặc chồng chéo không?
    5. Definition of Done có được đề cập không?
    Nếu thiếu bất kỳ điểm nào → trả về REVISION NEEDED + lý do cụ thể.""",
    llm=llm,
    verbose=True
)
```

### 8.3 Crew điều phối
```python
# crew.py
from crewai import Crew, Task
from agents.researcher import researcher
from agents.planner import planner
from agents.evaluator import evaluator

def run(requirement: str, project_context: dict = None) -> str:
    context_str = ""
    if project_context:
        context_str = f"\nStack: {project_context.get('stack', 'Unknown')}"
        context_str += f"\nSprint: {project_context.get('sprint', 'Next Sprint')}"

    research_task = Task(
        description=f"""Tìm kiếm trong knowledge base các thông tin liên quan đến:
        Yêu cầu: {requirement}
        {context_str}
        
        Cần tìm: stack kỹ thuật, các US tương tự đã làm, ràng buộc kỹ thuật.""",
        agent=researcher,
        expected_output="Tóm tắt context kỹ thuật và các US liên quan từ knowledge base"
    )

    planning_task = Task(
        description=f"""Dựa trên context từ Researcher, viết User Stories cho:
        {requirement}
        
        Bắt buộc bao gồm: User Story, Acceptance Criteria (Given/When/Then), 
        Story Points, danh sách Tasks chia theo BE/FE/QA.""",
        agent=planner,
        context=[research_task],
        expected_output="User Stories hoàn chỉnh theo format chuẩn"
    )

    eval_task = Task(
        description="Review User Stories từ Planner theo checklist chất lượng. Trả về APPROVED hoặc REVISION NEEDED.",
        agent=evaluator,
        context=[planning_task],
        expected_output="APPROVED hoặc REVISION NEEDED với danh sách vấn đề cụ thể"
    )

    crew = Crew(
        agents=[researcher, planner, evaluator],
        tasks=[research_task, planning_task, eval_task],
        verbose=True
    )

    return crew.kickoff()
```

### 8.4 Tạo Issue trên Jira
```python
# tools/jira_tool.py
import requests
from crewai.tools import tool

JIRA_BASE_URL = "https://your-company.atlassian.net"
JIRA_EMAIL = "your-email@company.com"
JIRA_TOKEN = "your-api-token"  # Lấy từ Atlassian account settings
PROJECT_KEY = "PROJ"

@tool("Create Jira Issue")
def create_jira_issue(summary: str, description: str, story_points: int, assignee: str = None) -> str:
    """Tạo một issue mới trên Jira"""
    url = f"{JIRA_BASE_URL}/rest/api/3/issue"
    
    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc", "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
            },
            "issuetype": {"name": "Story"},
            "story_points": story_points,
        }
    }
    
    response = requests.post(
        url,
        json=payload,
        auth=(JIRA_EMAIL, JIRA_TOKEN),
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        issue_key = response.json()["key"]
        return f"Created: {JIRA_BASE_URL}/browse/{issue_key}"
    else:
        return f"Error {response.status_code}: {response.text}"
```

---

## 9. Metrics đánh giá

### 9.1 Chất lượng User Story (tự build)
```python
# evaluate.py
def score_user_story(generated: str, expected: str) -> dict:
    scores = {}
    
    # Format score — có đủ As a / I want / So that không
    has_format = all(kw in generated for kw in ["As a", "I want", "so that"])
    scores["format"] = 1.0 if has_format else 0.0
    
    # AC score — có đủ Given/When/Then không
    ac_count = generated.count("Given") + generated.count("When") + generated.count("Then")
    scores["ac_completeness"] = min(ac_count / 9, 1.0)  # Tối thiểu 3 AC
    
    # Story points — có trong range hợp lý không
    has_points = any(str(p) in generated for p in [1, 2, 3, 5, 8, 13])
    scores["story_points"] = 1.0 if has_points else 0.0
    
    # Task breakdown — có chia BE/FE/QA không
    has_tasks = all(tag in generated for tag in ["[BE]", "[FE]", "[QA]"])
    scores["task_breakdown"] = 1.0 if has_tasks else 0.0
    
    scores["total"] = sum(scores.values()) / len(scores)
    return scores
```

### 9.2 RAGAS cho RAG pipeline
```bash
pip install ragas
```
```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall

results = evaluate(
    dataset=test_dataset,
    metrics=[faithfulness, answer_relevancy, context_recall]
)
print(results)
```

### 9.3 Target metrics cho v1
| Metric | Target |
|---|---|
| Format correctness | ≥ 90% |
| AC completeness | ≥ 85% |
| Task breakdown accuracy | ≥ 80% |
| Jira API success rate | ≥ 95% |
| End-to-end latency | ≤ 60 giây |

---

---

# Đề tài 2 — HR Knowledge Bot

## 1. Ý nghĩa bài toán

### Vấn đề thực tế
Nhân viên trong công ty thường xuyên gặp các câu hỏi lặp đi lặp lại về chính sách nội bộ:

- "Tôi được nghỉ bao nhiêu ngày phép năm?"
- "Quy trình xin tăng lương như thế nào?"
- "Nếu đi công tác thì được hoàn ứng bao nhiêu tiền/ngày?"
- "Thời hạn nộp chấm công tháng này là ngày mấy?"

HR phải trả lời các câu hỏi này **hàng chục lần/tuần**, trong khi câu trả lời đã có sẵn trong các tài liệu nội bộ. Nhân viên thì phải đợi HR online mới có câu trả lời.

### Tại sao không dùng FAQ tĩnh hoặc chatbot rule-based?
| Phương pháp | Giới hạn |
|---|---|
| FAQ tĩnh | Không tìm được câu hỏi tương tự, phải hỏi đúng từ khoá |
| Rule-based chatbot | Phải lập trình từng câu hỏi, không handle câu hỏi mới |
| Search engine nội bộ | Trả về cả đoạn văn, nhân viên phải tự đọc và hiểu |

**HR Knowledge Bot** hiểu **ý định** của câu hỏi, tra đúng tài liệu liên quan và **trả lời trực tiếp** bằng ngôn ngữ tự nhiên + trích dẫn nguồn.

---

## 2. Định nghĩa rõ Input / Output

### Input
```
Câu hỏi từ nhân viên (qua Slack / Web UI):
"Mình muốn xin nghỉ phép dài hạn 2 tuần để chăm sóc người thân ốm. 
Cần làm thủ tục gì và gửi cho ai?"
```

### Output
```
Bot trả lời:
─────────────────────────────────────────────
Để xin nghỉ phép dài hạn (từ 5 ngày trở lên), bạn cần thực hiện theo quy trình sau:

📋 CÁC BƯỚC THỰC HIỆN:
1. Điền Form xin nghỉ phép dài hạn (HR-FORM-003) — tải tại: [link nội bộ]
2. Gửi cho Quản lý trực tiếp phê duyệt — trước ít nhất 5 ngày làm việc
3. CC email cho phòng HR (hr@company.com) để theo dõi
4. Nếu nghỉ từ 10 ngày trở lên → cần thêm chữ ký của Giám đốc bộ phận

📌 LƯU Ý:
- Nghỉ chăm người thân ốm nặng được tính vào phép có hưởng lương (tối đa 3 ngày)
- Phần còn lại tính vào phép năm hoặc nghỉ không lương theo thỏa thuận

📄 NGUỒN: Chính sách Nghỉ phép — Mục 4.2, phiên bản cập nhật 01/2025

Bạn có cần mình giải thích thêm điều gì không?
─────────────────────────────────────────────
```

---

## 3. Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────────────┐
│                        INPUT                                │
│   Câu hỏi nhân viên (Slack / Web / Teams)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               INTENT CLASSIFICATION                         │
│   Phân loại: Nghỉ phép / Lương thưởng / Tuyển dụng /      │
│              Công tác / Đánh giá / Khác                     │
└────────────────────────┬────────────────────────────────────┘
                         │ Intent + Entities
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   RAG RETRIEVAL                             │
│   Query ChromaDB → Lấy đoạn tài liệu liên quan nhất        │
│   (Sổ tay nhân viên, Chính sách, Quy trình, Forms)         │
└────────────────────────┬────────────────────────────────────┘
                         │ Relevant chunks + metadata
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  ANSWER GENERATION                          │
│   LLM tổng hợp câu trả lời từ context                      │
│   → Thêm trích dẫn nguồn                                   │
│   → Format thân thiện (emoji, bullet points)               │
│   → Nếu không tìm thấy → escalate lên HR thật              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   CONFIDENCE CHECK                          │
│   Score cao (≥0.8) → Trả lời trực tiếp                     │
│   Score thấp (<0.8) → "Mình không chắc, để mình kết nối   │
│                         với HR nhé"                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Tại sao cần AI Agent (không phải chỉ RAG thuần)

| Tình huống | RAG thuần | AI Agent |
|---|---|---|
| Câu hỏi đơn giản, rõ ràng | Trả lời được | Trả lời được |
| Câu hỏi mơ hồ, thiếu context | Trả về sai chunk | Hỏi lại để làm rõ |
| Câu hỏi kết hợp 2 policy | Chỉ lấy 1 | Kết hợp nhiều nguồn |
| "Mình có được làm vậy không?" | Không hiểu intent | Phân tích, so sánh với policy |
| Không có câu trả lời trong tài liệu | Hallucinate | Escalate lên HR thật |
| Hỏi follow-up liên quan | Mất context | Nhớ conversation history |

---

## 5. Dữ liệu cần thiết

### 5.1 Tài liệu nạp vào RAG

| Tài liệu | Mục đích | Định dạng |
|---|---|---|
| Sổ tay nhân viên (Employee Handbook) | Nguồn chính của mọi chính sách | PDF / DOCX |
| Chính sách nghỉ phép chi tiết | Quy định ngày phép, loại phép | PDF |
| Quy trình thanh toán công tác | Mức hoàn ứng, thủ tục | PDF |
| Chính sách lương thưởng | Kỳ đánh giá, tăng lương | PDF |
| Quy trình onboarding | Dành cho nhân viên mới | PDF |
| Danh sách Forms + link tải | Nhân viên biết dùng form nào | Excel / Google Sheet |
| FAQ HR đã có sẵn | Tăng tốc retrieval | Q&A pairs |

**Nếu chưa có tài liệu nội bộ** → Dùng tài liệu mẫu:
```bash
# HR Policy dataset mẫu
python -c "
from datasets import load_dataset
ds = load_dataset('pirocheto/hr-policy-qa', split='train')
ds.to_json('data/hr_qa_sample.jsonl')
print(ds[0])
"
```

### 5.2 Dataset tham khảo

| Dataset | Mô tả | Link |
|---|---|---|
| HR Policy QA | Hỏi đáp chính sách nhân sự tiếng Anh | huggingface.co/datasets/pirocheto/hr-policy-qa |
| Banking77 | 7,700 câu hỏi, 77 intents — tham khảo intent classification | huggingface.co/datasets/banking77 |
| Bitext Customer Support | 27k cặp Q&A hỗ trợ — tham khảo cách trả lời | huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset |
| MultiWOZ | Hội thoại đa lượt có context — học cách duy trì conversation | huggingface.co/datasets/multi_woz_v22 |

```bash
python -c "
from datasets import load_dataset

# HR Policy QA
ds = load_dataset('pirocheto/hr-policy-qa', split='train')
ds.to_json('data/hr_policy.jsonl')

# Intent reference
ds2 = load_dataset('banking77', split='train[:200]')
ds2.to_json('data/intent_ref.jsonl')

print('Done')
"
```

### 5.3 Ground Truth (tự tạo)

Cần **30–50 cặp** do HR thật cung cấp:
```json
{
  "id": "HR-GT-001",
  "question": "Tôi được nghỉ bao nhiêu ngày phép năm?",
  "expected_answer": "Nhân viên được 12 ngày phép năm có hưởng lương...",
  "expected_source": "Sổ tay nhân viên, Mục 5.1",
  "expected_escalate": false
}
```

```json
{
  "id": "HR-GT-030",
  "question": "Quy trình khiếu nại khi bị đánh giá không công bằng là gì?",
  "expected_answer": null,
  "expected_source": null,
  "expected_escalate": true,
  "escalate_reason": "Thông tin nhạy cảm, cần HR xử lý trực tiếp"
}
```

---

## 6. Tech Stack

```
LLM (Local):        qwen2.5:7b hoặc deepseek-r1:7b qua Ollama
Embedding:          nomic-embed-text qua Ollama
Vector DB:          ChromaDB
Framework:          LangChain (RAG pipeline + conversation memory)
Memory:             ConversationBufferWindowMemory (5 lượt gần nhất)
Interface:          Slack Bot (ưu tiên) hoặc Streamlit
Monitoring:         Langfuse (self-hosted)
Package:            Docker
```

---

## 7. Cấu trúc thư mục dự án

```
hr-bot/
├── data/
│   ├── raw/                    # Tài liệu HR gốc (PDF, DOCX)
│   ├── processed/              # Sau khi chunk + clean
│   └── ground_truth.json       # 30-50 cặp Q&A thủ công
├── knowledge/
│   ├── ingest.py               # Nạp tài liệu vào ChromaDB
│   └── chroma_db/              # Vector store
├── bot/
│   ├── retriever.py            # Query ChromaDB
│   ├── generator.py            # Tổng hợp câu trả lời
│   ├── classifier.py           # Phân loại intent
│   └── memory.py               # Lưu conversation history
├── guardrails/
│   └── checker.py              # Kiểm tra confidence, filter câu trả lời
├── interface/
│   ├── slack_bot.py            # Slack integration
│   └── streamlit_app.py        # Web UI demo
├── evaluate.py
├── Dockerfile
└── requirements.txt
```

---

## 8. Code mẫu

### 8.1 Nạp tài liệu HR vào RAG
```python
# knowledge/ingest.py
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

def ingest_hr_docs(docs_path: str = "data/raw", persist_dir: str = "knowledge/chroma_db"):
    # Load tất cả PDF trong thư mục
    loader = DirectoryLoader(docs_path, glob="**/*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()
    
    # Giữ metadata: tên file, số trang — quan trọng để trích dẫn nguồn
    for doc in docs:
        doc.metadata["source_display"] = (
            f"{doc.metadata.get('source', 'Unknown')}, "
            f"trang {doc.metadata.get('page', '?')}"
        )
    
    # Chunk nhỏ hơn vì HR policy cần chính xác từng điều khoản
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", "•"]
    )
    chunks = splitter.split_documents(docs)
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma.from_documents(chunks, embeddings, persist_directory=persist_dir)
    print(f"Ingested {len(chunks)} chunks from {len(docs)} pages")
    return db
```

### 8.2 RAG Pipeline với Memory
```python
# bot/generator.py
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory

def build_hr_bot(persist_dir: str = "knowledge/chroma_db"):
    llm = Ollama(model="qwen2.5:7b", temperature=0)
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})
    
    memory = ConversationBufferWindowMemory(
        k=5,  # Nhớ 5 lượt hội thoại gần nhất
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )
    
    system_prompt = """Bạn là HR Assistant của công ty, thân thiện và chính xác.
    
    Quy tắc bắt buộc:
    1. Chỉ trả lời dựa trên tài liệu được cung cấp — không tự suy đoán
    2. Luôn trích dẫn nguồn ở cuối câu trả lời
    3. Nếu không tìm thấy thông tin → nói: "Mình chưa có thông tin về vấn đề này. Bạn có thể liên hệ HR qua hr@company.com để được hỗ trợ nhé."
    4. Câu trả lời ngắn gọn, dùng bullet points khi liệt kê nhiều điểm
    5. Không tiết lộ thông tin lương/thưởng của người khác
    
    Context từ tài liệu HR:
    {context}
    
    Lịch sử hội thoại:
    {chat_history}
    """
    
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        verbose=True
    )
    
    return chain

def ask(chain, question: str) -> dict:
    result = chain({"question": question})
    
    sources = list(set([
        doc.metadata.get("source_display", "Tài liệu nội bộ")
        for doc in result.get("source_documents", [])
    ]))
    
    return {
        "answer": result["answer"],
        "sources": sources,
        "confidence": len(result.get("source_documents", [])) / 4  # proxy score
    }
```

### 8.3 Guardrails — Kiểm tra confidence
```python
# guardrails/checker.py

SENSITIVE_TOPICS = [
    "lương của", "thu nhập của", "thưởng của", "mức lương anh", "mức lương chị"
]

ESCALATE_TOPICS = [
    "khiếu nại", "tranh chấp lao động", "sa thải", "kỷ luật", "kiện"
]

def check_response(question: str, answer: str, confidence: float) -> dict:
    question_lower = question.lower()
    
    # Kiểm tra câu hỏi về lương người khác
    if any(topic in question_lower for topic in SENSITIVE_TOPICS):
        return {
            "action": "BLOCK",
            "message": "Mình không thể cung cấp thông tin lương/thưởng cá nhân. Vui lòng liên hệ HR trực tiếp."
        }
    
    # Kiểm tra chủ đề nhạy cảm cần HR thật
    if any(topic in question_lower for topic in ESCALATE_TOPICS):
        return {
            "action": "ESCALATE",
            "message": "Đây là vấn đề cần được HR xử lý trực tiếp. Mình sẽ kết nối bạn với HR ngay."
        }
    
    # Confidence thấp → cảnh báo
    if confidence < 0.5:
        return {
            "action": "WARN",
            "message": f"{answer}\n\n⚠️ Lưu ý: Mình không hoàn toàn chắc chắn về câu trả lời này. Bạn nên xác nhận lại với HR."
        }
    
    return {"action": "OK", "message": answer}
```

### 8.4 Slack Bot Integration
```python
# interface/slack_bot.py
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from bot.generator import build_hr_bot, ask
from guardrails.checker import check_response

app = App(token="xoxb-your-bot-token")
chain = build_hr_bot()

@app.event("app_mention")
def handle_mention(event, say):
    question = event["text"].replace("<@bot_id>", "").strip()
    
    result = ask(chain, question)
    checked = check_response(question, result["answer"], result["confidence"])
    
    if checked["action"] in ["BLOCK", "ESCALATE"]:
        say(checked["message"])
        return
    
    response_text = checked["message"]
    if result["sources"]:
        response_text += f"\n\n📄 *Nguồn:* {', '.join(result['sources'])}"
    
    say(response_text)

if __name__ == "__main__":
    SocketModeHandler(app, "xapp-your-app-token").start()
```

---

## 9. Metrics đánh giá

### 9.1 Accuracy trên Ground Truth
```python
# evaluate.py
import json
from bot.generator import build_hr_bot, ask
from guardrails.checker import check_response

def evaluate(ground_truth_path: str = "data/ground_truth.json"):
    with open(ground_truth_path) as f:
        test_cases = json.load(f)
    
    chain = build_hr_bot()
    results = []
    
    for case in test_cases:
        result = ask(chain, case["question"])
        checked = check_response(case["question"], result["answer"], result["confidence"])
        
        # Kiểm tra escalation
        escalate_correct = (checked["action"] == "ESCALATE") == case["expected_escalate"]
        
        # Kiểm tra source citation
        source_found = any(
            case.get("expected_source", "") in src
            for src in result["sources"]
        ) if not case["expected_escalate"] else True
        
        results.append({
            "id": case["id"],
            "escalate_correct": escalate_correct,
            "source_found": source_found,
            "confidence": result["confidence"]
        })
    
    total = len(results)
    print(f"Escalation accuracy:  {sum(r['escalate_correct'] for r in results)/total:.1%}")
    print(f"Source citation rate: {sum(r['source_found'] for r in results)/total:.1%}")
    print(f"Avg confidence:       {sum(r['confidence'] for r in results)/total:.2f}")

if __name__ == "__main__":
    evaluate()
```

### 9.2 Target metrics cho v1

| Metric | Target |
|---|---|
| Answer accuracy (vs ground truth) | ≥ 80% |
| Escalation precision | ≥ 95% (không được miss) |
| Source citation rate | ≥ 90% |
| Sensitive info blocking | 100% |
| Response latency | ≤ 10 giây |
| Hallucination rate | ≤ 5% |

---

---

# Roadmap 10 tuần chung

| Tuần | Intern 1 (Jimbo) | Intern 2 (HR Bot) | Deliverable |
|---|---|---|---|
| 1 | Đọc SWE-bench, Scrum Guide. Setup Ollama + deepseek-r1:7b | Đọc HR Policy dataset. Setup Ollama + qwen2.5:7b | Môi trường chạy được, model pull về xong |
| 2 | Ingest Scrum Guide + Atlassian docs vào ChromaDB. Test retrieval | Ingest HR Handbook vào ChromaDB. Test retrieval với 10 câu hỏi | RAG pipeline cơ bản hoạt động |
| 3 | Viết Planner Agent, test với 5 requirements mẫu | Viết RAG chain với conversation memory | Agent đơn lẻ trả lời được |
| 4 | Viết Researcher + Evaluator Agent. Kết nối thành Crew | Viết Intent Classifier + Guardrails cơ bản | Multi-component pipeline |
| 5 | Kết nối Jira API, test tạo issue tự động | Kết nối Slack Bot, test nhận và trả lời message | Tool use / Integration |
| 6 | End-to-end test: email → User Stories → Jira | End-to-end test: câu hỏi → trả lời → cite nguồn | E2E pipeline hoàn chỉnh |
| 7 | Tạo 30 Ground Truth samples, chạy evaluate.py | Tạo 30 Ground Truth samples, chạy evaluate.py | Baseline metrics |
| 8 | Tune prompt dựa trên kết quả đánh giá. Fix lỗi | Tune prompt, cải thiện chunking strategy | Improved metrics |
| 9 | Hoàn thiện Guardrails, kiểm tra bảo mật, Dockerize | Hoàn thiện Guardrails, kiểm tra Sensitive topics, Dockerize | Production-ready |
| 10 | Demo + viết báo cáo kỹ thuật | Demo + viết báo cáo kỹ thuật | Final presentation |

---

# Tiêu chí đánh giá

## Tiêu chí kỹ thuật (70%)

| Hạng mục | Điểm | Mô tả |
|---|---|---|
| Pipeline hoạt động E2E | 20 | Input → Output → Action không bị lỗi |
| Chất lượng output | 20 | Đạt target metrics theo bảng trên |
| Code quality | 15 | Clean code, có docstring, có error handling |
| Evaluation | 15 | Có ground truth, có script đánh giá |

## Tiêu chí phi kỹ thuật (30%)

| Hạng mục | Điểm | Mô tả |
|---|---|---|
| Báo cáo kỹ thuật | 15 | Mô tả kiến trúc, kết quả, hạn chế |
| Demo | 10 | Demo live, xử lý được câu hỏi thực tế |
| Chủ động học hỏi | 5 | Đề xuất cải tiến, tự nghiên cứu |

---

## Tài liệu tham khảo

- Scrum Guide 2020: scrumguides.org
- LangChain Docs: python.langchain.com
- CrewAI Docs: docs.crewai.com
- Ollama: ollama.com
- ChromaDB: docs.trychroma.com
- RAGAS (Evaluation): docs.ragas.io
- Jira REST API: developer.atlassian.com/cloud/jira/platform/rest/v3
- Slack Bolt Python: slack.dev/bolt-python

---

---

# Appendix — Các đề tài mở rộng

> Các đề tài dưới đây phù hợp cho các khóa thực tập tiếp theo hoặc mở rộng scope nếu 2 intern hoàn thành sớm.

---

## A1. Auto Code Review

### Ý nghĩa
Dev review PR thủ công mất 30–60 phút/PR, dễ bỏ sót lỗi bảo mật, code smell và vi phạm convention. Agent tự động review và comment trực tiếp lên PR trong vài giây.

### Tại sao cần Agent (không dùng linter/SonarQube thuần)?
Linter phát hiện lỗi cú pháp. Agent hiểu **ngữ nghĩa**: logic sai, thiếu edge case, security vulnerability, đặt tên biến khó hiểu, và giải thích **tại sao** cần sửa bằng ngôn ngữ tự nhiên.

### Input / Output

**Input:**
```
Git diff của Pull Request:
- diff --git a/auth/login.py b/auth/login.py
+ def login(username, password):
+     query = f"SELECT * FROM users WHERE username='{username}'"
+     result = db.execute(query)
```

**Output:**
```
🚨 [CRITICAL] SQL Injection — auth/login.py, dòng 3
Câu query đang nối chuỗi trực tiếp với input người dùng.
Hacker có thể nhập: username = "admin' OR '1'='1" để bypass auth.

Sửa lại:
  query = "SELECT * FROM users WHERE username = %s"
  result = db.execute(query, (username,))

📖 Tham khảo: OWASP Top 10 — A03:2021 Injection

⚠️ [WARNING] Thiếu xử lý khi user không tồn tại — dòng 5
Nếu result trả về None, code sẽ crash ở bước tiếp theo.

✅ [STYLE] Tên biến 'result' quá chung chung → đổi thành 'user_record'
```

### Data

| Dataset | Link | Dùng để |
|---|---|---|
| CodeReviewer (Microsoft) | `huggingface.co/datasets/microsoft/codereview` | Cặp code diff → review comment |
| GitHub PRs public | `api.github.com/repos/facebook/react/pulls` | Real PR data |
| CWE Weakness Database | `cwe.mitre.org/data/downloads.html` | Danh sách lỗ hổng bảo mật |
| OWASP Top 10 | `owasp.org/Top10` | Kiến thức security cho RAG |

```bash
python -c "
from datasets import load_dataset
ds = load_dataset('microsoft/codereview', split='train[:100]')
ds.to_json('data/codereview_sample.jsonl')
"
```

### Kiến trúc
```
GitHub Webhook → nhận PR event
      ↓
Security Agent   → quét SQL injection, XSS, hardcoded secrets
Style Agent      → convention, naming, complexity
Logic Agent      → edge cases, null handling, error handling
      ↓
Aggregator       → tổng hợp, loại bỏ false positive
      ↓
GitHub API       → post comments lên PR
```

### Tech Stack
```
Framework:  LangGraph (stateful review flow)
Model:      deepseek-r1:7b (Ollama)
RAG:        ChromaDB chứa OWASP + coding guidelines nội bộ
Integration: GitHub Webhooks + GitHub REST API
```

### Target Metrics
| Metric | Target |
|---|---|
| True positive rate (real bugs) | ≥ 75% |
| False positive rate | ≤ 20% |
| Security issue detection | ≥ 90% |
| Latency per PR | ≤ 30 giây |

---

## A2. Research Assistant

### Ý nghĩa
Researcher / engineer cần đọc 10–20 papers để nắm xu hướng mới, mỗi paper mất 1–2 giờ. Agent tự tìm, tải, đọc và tổng hợp các papers liên quan theo câu hỏi nghiên cứu.

### Tại sao cần Agent?
Search engine trả về danh sách link. Agent **đọc nội dung**, so sánh phương pháp giữa các papers, chỉ ra điểm mạnh/yếu và trả lời câu hỏi nghiên cứu cụ thể.

### Input / Output

**Input:**
```
"So sánh các phương pháp RAG hiện tại. 
Phương pháp nào tốt nhất cho domain-specific QA?"
```

**Output:**
```
Tổng hợp từ 8 papers (2023–2025):

📊 SO SÁNH PHƯƠNG PHÁP RAG:

1. Naive RAG (Lewis et al., 2020)
   - Ưu: Đơn giản, dễ implement
   - Nhược: Retrieval kém với câu hỏi phức tạp, multi-hop

2. HyDE (Gao et al., 2022)  
   - Ưu: Cải thiện retrieval 15-20% bằng hypothetical document
   - Nhược: Thêm 1 LLM call → tăng latency

3. Self-RAG (Asai et al., 2023)
   - Ưu: Agent tự quyết định khi nào cần retrieve → tốt nhất cho domain-specific
   - Nhược: Cần fine-tuning model, phức tạp hơn

🏆 KHUYẾN NGHỊ cho domain-specific QA: Self-RAG
Lý do: Precision cao hơn 12% so với Naive RAG trên medical/legal benchmarks

📄 Nguồn: [danh sách 8 papers với link ArXiv]
```

### Data

| Dataset | Link | Dùng để |
|---|---|---|
| ArXiv dataset | `huggingface.co/datasets/arxiv_dataset` | Corpus papers để search |
| ArXiv API | `export.arxiv.org/api/query?search_query=cat:cs.AI&max_results=50` | Search real-time |
| S2ORC | `huggingface.co/datasets/allenai/s2orc` | Full-text papers |
| QASPER | `huggingface.co/datasets/allenai/qasper` | QA trên nội dung papers |

```bash
# Lấy papers về RAG từ ArXiv
curl "https://export.arxiv.org/api/query?search_query=ti:RAG+retrieval+augmented&max_results=30&sortBy=submittedDate" -o arxiv_rag.xml
```

### Kiến trúc
```
Câu hỏi nghiên cứu
      ↓
Search Agent   → query ArXiv API, Google Scholar
      ↓
Download Agent → tải PDF, extract text
      ↓
Read Agent     → đọc Abstract + Conclusion + Results của từng paper
      ↓
Synthesis Agent → so sánh, tổng hợp, trả lời câu hỏi
      ↓
Report         → markdown với citations
```

### Tech Stack
```
Framework:  LangGraph
Model:      deepseek-r1:7b (cần reasoning tốt)
RAG:        ChromaDB (lưu papers đã đọc để tái sử dụng)
Tools:      ArXiv API, PyMuPDF (đọc PDF)
Output:     Markdown report
```

---

## A3. Chatbot Chăm sóc KH 24/7

### Ý nghĩa
Nhân viên CSKH không làm việc ngoài giờ hành chính. Khách hàng hỏi ngoài giờ phải đợi đến sáng hôm sau. Agent trả lời 24/7, xử lý 70–80% câu hỏi phổ biến, chỉ escalate các trường hợp phức tạp.

### Tại sao cần Agent (không dùng chatbot rule-based)?
Rule-based chatbot chỉ xử lý đúng câu hỏi đã lập trình. Agent hiểu **ý định** dù khách hàng diễn đạt khác nhau, duy trì **context** qua nhiều lượt hội thoại, và biết khi nào cần **chuyển sang người thật**.

### Input / Output

**Input:**
```
Khách: "Mình đặt hàng hôm qua mà chưa thấy email xác nhận, 
        kiểm tra giúp mình với. Mã đơn là HD-20250517-001"
```

**Output:**
```
Bot: Mình đã kiểm tra đơn hàng HD-20250517-001 của bạn.

📦 TRẠNG THÁI ĐƠN HÀNG:
- Ngày đặt: 17/05/2025 lúc 14:32
- Trạng thái: Đã xác nhận ✅ (email gửi lúc 14:35)
- Giao hàng dự kiến: 19/05/2025

📧 Email xác nhận đã gửi đến: tr***@gmail.com
Bạn có thể kiểm tra trong thư mục Spam/Junk nhé.

Bạn cần mình hỗ trợ thêm điều gì không?
```

### Data

| Dataset | Link | Dùng để |
|---|---|---|
| Bitext Customer Support | `huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset` | 27k cặp Q&A CSKH |
| MultiWOZ | `huggingface.co/datasets/multi_woz_v22` | Hội thoại đa lượt |
| ATIS | `huggingface.co/datasets/tuetschek/atis` | Intent + entity extraction |
| Banking77 | `huggingface.co/datasets/banking77` | 77 intents phân loại |

```bash
python -c "
from datasets import load_dataset
ds = load_dataset('bitext/Bitext-customer-support-llm-chatbot-training-dataset', split='train[:300]')
ds.to_json('data/customer_support.jsonl')
"
```

### Kiến trúc
```
Tin nhắn khách
      ↓
Intent Classifier  → đặt hàng / tra cứu / khiếu nại / hoàn tiền
      ↓
Entity Extractor   → mã đơn, tên sản phẩm, ngày
      ↓
[Nếu cần data] → gọi Order API / CRM API lấy thông tin thật
[Nếu hỏi policy] → query RAG (chính sách đổi trả, vận chuyển)
      ↓
Response Generator → trả lời thân thiện + đầy đủ thông tin
      ↓
[Nếu phức tạp] → "Để mình kết nối bạn với CSKH nhé"
```

### Tech Stack
```
Framework:  LangChain + ConversationBufferMemory
Model:      qwen2.5:7b (Ollama)
RAG:        ChromaDB (FAQ, chính sách)
Tools:      Order Management API, CRM API
Interface:  Zalo OA / Facebook Messenger / Web Widget
```

---

## A4. Phân loại & Điều hướng yêu cầu

### Ý nghĩa
Email/ticket gửi vào hòm thư chung của công ty, nhân viên trực phải đọc từng cái và chuyển đúng bộ phận — tốn 1–2 giờ/ngày, dễ nhầm và delay.

### Tại sao cần Agent?
Classifier ML chỉ gán nhãn. Agent **đọc kỹ**, trích xuất thông tin quan trọng (mức độ khẩn, khách VIP, deadline), **soạn email chuyển tiếp** kèm tóm tắt, và **tự động assign** vào đúng queue.

### Input / Output

**Input:**
```
Subject: Lỗi thanh toán khẩn cấp - cần xử lý trước 5pm hôm nay
From: nguyen.van.a@bigclient.com (VIP Customer - hợp đồng 500M)

"Hệ thống báo lỗi khi tôi thanh toán hóa đơn tháng 5. 
Nếu không xử lý hôm nay, chúng tôi sẽ bị phạt hợp đồng."
```

**Output:**
```
[Tự động assign vào queue: PAYMENT_URGENT]
[Tag: VIP | Deadline: 17:00 hôm nay | Priority: P1]

Notification gửi cho Team Lead Payment:
"⚠️ P1 - Khách VIP cần hỗ trợ gấp
Khách: Nguyen Van A (BigClient - hợp đồng 500M)
Vấn đề: Lỗi thanh toán hóa đơn tháng 5
Deadline: 17:00 hôm nay
Action: Cần liên hệ khách trong 15 phút"
```

### Data

| Dataset | Link | Dùng để |
|---|---|---|
| Banking77 | `huggingface.co/datasets/banking77` | 77 loại intent phân loại |
| Customer Support Ticket | `kaggle.com/datasets/suraj520/customer-support-ticket-dataset` | Email ticket + category label |
| ATIS | `huggingface.co/datasets/tuetschek/atis` | Entity extraction |

```bash
python -c "
from datasets import load_dataset
ds = load_dataset('banking77', split='train')
ds.to_json('data/intent_classification.jsonl')
"
```

### Kiến trúc
```
Email/Ticket mới
      ↓
Classifier Agent  → loại yêu cầu (kỹ thuật/thanh toán/khiếu nại/sales)
Priority Agent    → mức độ khẩn, VIP detection, deadline extraction
      ↓
Routing Engine    → chọn đúng queue + người phụ trách
Summary Agent     → tóm tắt 3 dòng cho người nhận
      ↓
Action: Gửi notification + tạo ticket + assign
```

---

## A5. Trích xuất Báo cáo Tài chính

### Ý nghĩa
Analyst tài chính phải đọc các báo cáo PDF dày 100–200 trang để lấy các chỉ số KPI. Với hàng chục công ty cần theo dõi, việc này tốn nhiều ngày và dễ sai sót.

### Tại sao cần Agent (không dùng parser/regex)?
Báo cáo tài chính mỗi công ty có format khác nhau, số liệu nằm trong bảng phức tạp hoặc mô tả bằng văn xuôi. Agent **hiểu ngữ nghĩa**, tìm đúng con số dù format khác nhau và **giải thích** bối cảnh của con số đó.

### Input / Output

**Input:**
```
File: VCB_BaoCaoTaiChinh_Q1_2025.pdf (187 trang)
Yêu cầu: Trích xuất các chỉ số tài chính chính
```

**Output:**
```json
{
  "company": "Vietcombank",
  "period": "Q1 2025",
  "extracted_at": "2025-05-17",
  "metrics": {
    "total_revenue": {"value": 15234, "unit": "tỷ VND", "page": 12},
    "net_profit": {"value": 8921, "unit": "tỷ VND", "page": 12},
    "npm": {"value": "58.6%", "page": 13},
    "roe": {"value": "21.3%", "page": 45},
    "npl_ratio": {"value": "0.97%", "page": 67},
    "capital_adequacy": {"value": "14.2%", "page": 89}
  },
  "notable": "Lợi nhuận tăng 23% YoY, NPL giảm từ 1.2% xuống 0.97%",
  "confidence": 0.94
}
```

### Data

| Dataset | Link | Dùng để |
|---|---|---|
| FinanceBench | `huggingface.co/datasets/PatronusAI/financebench` | QA trên báo cáo tài chính thật |
| SEC EDGAR | `sec.gov/cgi-bin/browse-edgar?action=getcompany&type=10-K` | PDF báo cáo công ty Mỹ |
| Financial PhraseBank | `huggingface.co/datasets/financial_phrasebank` | Sentiment + entity tài chính |
| TAT-QA | `huggingface.co/datasets/next-tat/tat-qa` | QA kết hợp bảng + văn bản |

```bash
python -c "
from datasets import load_dataset
ds = load_dataset('PatronusAI/financebench', split='train[:50]')
ds.to_json('data/financebench.jsonl')
"
```

### Kiến trúc
```
PDF báo cáo
      ↓
PDF Parser     → extract text + tables (dùng pdfplumber hoặc pymupdf)
      ↓
Table Agent    → xử lý bảng số liệu phức tạp
Text Agent     → tìm số liệu trong văn xuôi
      ↓
Validation     → cross-check: Revenue - Expenses ≈ Net Profit
      ↓
Output JSON    → structured data + confidence score
```

### Tech Stack
```
PDF Parsing:  pdfplumber (bảng) + PyMuPDF (text)
Framework:    LangChain
Model:        deepseek-r1:7b
Validation:   Rule-based cross-check sau khi extract
Output:       JSON → có thể đẩy vào Excel / Database
```

---

## A6. Rà soát Hợp đồng

### Ý nghĩa
Luật sư/procurement phải đọc toàn bộ hợp đồng (50–200 trang) để tìm điều khoản bất lợi, phạt vi phạm ẩn, điều khoản độc quyền... Mỗi hợp đồng mất 2–4 giờ.

### Tại sao cần Agent?
NLP classifier gán nhãn điều khoản. Agent **hiểu ngữ nghĩa pháp lý**, so sánh với template chuẩn của công ty, phát hiện **sự vắng mặt** của điều khoản quan trọng (không chỉ phát hiện điều khoản xấu), và giải thích rủi ro bằng ngôn ngữ đơn giản.

### Input / Output

**Input:**
```
File: HopDong_MuaBan_CongTyABC_2025.pdf
```

**Output:**
```
BÁO CÁO RÀ SOÁT HỢP ĐỒNG
─────────────────────────────
🚨 RỦI RO CAO (cần đàm phán lại):

1. Điều 8.3 — Phạt vi phạm một chiều
   "Bên B chịu phạt 5% giá trị hợp đồng nếu giao hàng trễ"
   → Không có điều khoản phạt tương ứng cho Bên A nếu thanh toán trễ
   → Đề xuất: Thêm "Bên A chịu phạt tương tự nếu thanh toán sau 30 ngày"

2. Điều 12 — Điều khoản độc quyền
   "Bên B không được cung cấp dịch vụ tương tự cho đối thủ cạnh tranh"
   → Thời hạn: 3 năm sau khi hợp đồng chấm dứt — quá dài
   → Đề xuất: Giảm xuống còn 1 năm, định nghĩa rõ "đối thủ cạnh tranh"

⚠️ THIẾU ĐIỀU KHOẢN (cần bổ sung):
- Không có điều khoản Bảo mật thông tin (NDA)
- Không có điều khoản Giải quyết tranh chấp (Tòa án nào?)
- Không có điều khoản Bất khả kháng (Force Majeure)

✅ ĐIỀU KHOẢN ỔN:
- Điều 5: Thanh toán rõ ràng, đúng thông lệ
- Điều 9: Bảo hành đầy đủ

📊 ĐIỂM RỦI RO TỔNG THỂ: 6.5/10 (Trung bình-Cao)
```

### Data

| Dataset | Link | Dùng để |
|---|---|---|
| CUAD | `huggingface.co/datasets/cuad` | 510 hợp đồng thật, 41 loại điều khoản được gán nhãn |
| ContractNLI | `huggingface.co/datasets/kiddothe2b/contractnli` | NLI trên hợp đồng |
| LEDGAR (LexGLUE) | `huggingface.co/datasets/lex_glue` | Phân loại điều khoản pháp lý |
| Template hợp đồng chuẩn | Tự thu thập từ thư viện pháp luật | RAG knowledge base |

```bash
python -c "
from datasets import load_dataset
ds = load_dataset('cuad', split='train[:30]')
ds.to_json('data/contracts_sample.jsonl')
"
```

### Kiến trúc
```
PDF hợp đồng
      ↓
Clause Extractor   → chia hợp đồng thành từng điều khoản
      ↓
Risk Analyzer      → so sánh với template chuẩn trong RAG
Gap Detector       → tìm điều khoản quan trọng còn thiếu
      ↓
Risk Scorer        → chấm điểm từng vấn đề (High/Medium/Low)
      ↓
Report Generator   → tổng hợp báo cáo + đề xuất sửa đổi
```

---

## A7. Phát hiện Gian lận AML

### Ý nghĩa
Hệ thống ML phát hiện giao dịch nghi ngờ, nhưng compliance officer phải tự điều tra thủ công từng case, tra cứu lịch sử, viết báo cáo — mất 1–2 giờ/case.

### Tại sao cần Agent?
ML flag giao dịch. Agent **điều tra**: truy vết chuỗi giao dịch liên quan, tìm pattern rửa tiền (layering, smurfing), so sánh với hồ sơ rủi ro của khách hàng, và **tự viết báo cáo STR** (Suspicious Transaction Report) theo chuẩn pháp lý.

### Input / Output

**Input:**
```json
{
  "transaction_id": "TXN-20250517-9821",
  "amount": 498000000,
  "from_account": "ACC-001234",
  "to_account": "ACC-009876",
  "timestamp": "2025-05-17 02:34:11",
  "flag": "AMOUNT_THRESHOLD"
}
```

**Output:**
```
BÁO CÁO ĐIỀU TRA GIAO DỊCH NGHI NGỜ
─────────────────────────────────────
Giao dịch: TXN-20250517-9821

🔍 PHÂN TÍCH:
Pattern phát hiện: Structuring (Smurfing)
- Tài khoản ACC-001234 thực hiện 4 giao dịch trong 48h:
  498M + 497M + 499M + 496M = 1.99 tỷ VND
  (Mỗi giao dịch dưới ngưỡng báo cáo 500M)

- Tất cả giao dịch vào lúc 2-4 giờ sáng
- Tài khoản nhận (ACC-009876) mở cách đây 7 ngày, chưa có lịch sử

Hồ sơ khách hàng:
- ACC-001234: Cá nhân, thu nhập khai báo 15M/tháng
- Giao dịch 1.99 tỷ trong 48h = BẤT THƯỜNG

🚨 MỨC RỦI RO: RẤT CAO
Đề xuất: Đóng băng tài khoản + Nộp STR trong 24h

📄 Dự thảo STR: [báo cáo theo mẫu NHNN]
```

### Data

| Dataset | Link | Dùng để |
|---|---|---|
| Credit Card Fraud | `kaggle.com/datasets/mlg-ulb/creditcardfraud` | 284k giao dịch, labeled fraud |
| PaySim | `kaggle.com/datasets/ealaxi/paysim1` | Mô phỏng mobile money transactions |
| IEEE-CIS Fraud | `kaggle.com/competitions/ieee-fraud-detection` | E-commerce transactions |

```bash
# Cần Kaggle API key
kaggle datasets download -d mlg-ulb/creditcardfraud -p data/
```

### Kiến trúc
```
Giao dịch bị flag bởi ML model
      ↓
Investigation Agent  → tra cứu lịch sử 90 ngày của tài khoản
Pattern Agent        → nhận dạng: structuring, layering, smurfing
Profile Agent        → so sánh với hồ sơ KYC của khách
      ↓
Risk Scorer          → tổng hợp bằng chứng, chấm điểm rủi ro
Report Agent         → viết STR theo mẫu pháp lý
      ↓
Compliance Officer   → review và submit
```

---

## A8. Sàng lọc CV Ứng viên

### Ý nghĩa
HR đọc 100–300 CV cho mỗi vị trí tuyển dụng. Phần lớn thời gian để loại các CV không phù hợp, thay vì tập trung vào ứng viên tốt.

### Tại sao cần Agent (không dùng ATS thuần)?
ATS keyword matching bỏ sót ứng viên dùng từ đồng nghĩa. Agent **hiểu kinh nghiệm**, đánh giá **tiềm năng** (ứng viên junior nhưng đang học nhanh), giải thích **lý do** ranking, và hỏi thêm câu hỏi screening phù hợp.

### Input / Output

**Input:**
```
Job Description: Senior Python Backend Engineer
- 5+ năm Python
- Kinh nghiệm với FastAPI hoặc Django
- PostgreSQL, Redis
- Microservices, Docker, Kubernetes

CV: Nguyen_Thi_B_CV.pdf
```

**Output:**
```
ĐÁNH GIÁ ỨNG VIÊN: Nguyễn Thị B
─────────────────────────────────
⭐ ĐIỂM PHÙ HỢP: 82/100 — KHUYẾN NGHỊ MỜI PHỎNG VẤN

✅ ĐIỂM MẠNH:
- 6 năm Python (đủ yêu cầu)
- FastAPI 3 năm (match tốt)
- PostgreSQL + Redis (đủ)
- Docker/K8s tại 2 công ty trước (match tốt)

⚠️ ĐIỂM CẦN CONFIRM:
- CV ghi "microservices" nhưng không nêu scale cụ thể
  → Câu hỏi screening: "Hệ thống microservices bạn làm có bao nhiêu services? Traffic như thế nào?"

❌ THIẾU:
- Không có kinh nghiệm team lead (JD không yêu cầu nhưng có là điểm cộng)

💡 GỢI Ý PHỎNG VẤN:
1. Technical: Thiết kế API rate limiting với Redis
2. Behavioral: Kể về một incident production bạn xử lý
```

### Data

| Dataset | Link | Dùng để |
|---|---|---|
| Resume-JD Matching | `huggingface.co/datasets/cnamuangtoun/resume-job-description-fit` | Cặp CV-JD + fit label |
| Job Descriptions | `huggingface.co/datasets/jacob-hugging-face/job-descriptions` | JD thật từ LinkedIn |
| Resume Dataset (Kaggle) | `kaggle.com/datasets/gauravduttakiit/resume-datasets` | 2400 CVs phân loại theo ngành |

```bash
python -c "
from datasets import load_dataset
ds = load_dataset('cnamuangtoun/resume-job-description-fit', split='train[:100]')
ds.to_json('data/resume_jd_sample.jsonl')
"
```

### Kiến trúc
```
CV (PDF) + Job Description
      ↓
CV Parser         → extract: skills, experience, education, projects
JD Analyzer       → extract: requirements (must-have vs nice-to-have)
      ↓
Matching Agent    → so sánh từng yêu cầu với CV
Gap Analyzer      → tìm điểm thiếu, đề xuất câu hỏi làm rõ
      ↓
Scoring Agent     → tổng hợp điểm + giải thích
      ↓
Ranking + Report  → top candidates + lý do
```

---

## A9. Predictive Maintenance

### Ý nghĩa
Máy móc hỏng đột ngột gây dừng sản xuất (downtime) tốn hàng trăm triệu đến hàng tỷ đồng. Bảo trì định kỳ theo lịch cố định thì lãng phí (bảo trì khi chưa cần). Predictive Maintenance bảo trì đúng lúc, trước khi hỏng.

### Tại sao cần Agent (không dùng ML forecasting thuần)?
ML model dự đoán xác suất hỏng. Agent biến dự đoán thành **hành động**: kiểm tra kho phụ tùng có sẵn không, xem lịch sản xuất để chọn thời điểm bảo trì ít ảnh hưởng nhất, tự tạo work order và thông báo kỹ thuật viên.

### Input / Output

**Input:**
```
Sensor data (real-time từ IoT):
{
  "machine_id": "CNC-007",
  "temperature": 87.3,  // ngưỡng bình thường: 60-75°C
  "vibration": 4.2,     // ngưỡng bình thường: 0-2.5 mm/s
  "rpm": 2850,
  "timestamp": "2025-05-17 09:15:00"
}
```

**Output:**
```
⚠️ CẢNH BÁO BẢO TRÌ — Máy CNC-007
─────────────────────────────────────
Dự đoán: Khả năng hỏng bearing trong 3–5 ngày (confidence: 87%)

Bằng chứng:
- Nhiệt độ: 87.3°C (vượt ngưỡng 75°C, trend tăng 3 ngày qua)
- Rung động: 4.2 mm/s (vượt ngưỡng 2.5 mm/s, tăng đột biến từ sáng)
- Pattern giống 2 sự cố trước của CNC-005 (tháng 3/2025)

Kế hoạch bảo trì đề xuất:
📅 Thời điểm: Thứ 7, 18/05/2025, 6:00–10:00 sáng
   (Không có đơn hàng, downtime ảnh hưởng tối thiểu)

🔧 Phụ tùng cần:
   - SKF Bearing 6205-2Z × 2 (Kho: CÒN 3 CÁI ✅)
   - Grease Mobil SHC 460 × 1 hộp (Kho: CÒN ✅)

👤 Assign: Kỹ thuật viên Trần Văn C
📋 Work Order: WO-20250518-001 (đã tạo trên hệ thống)
```

### Data

| Dataset | Link | Dùng để |
|---|---|---|
| NASA CMAPSS | `kaggle.com/datasets/behrad3d/nasa-cmaps` | Sensor data máy bay, có RUL label |
| AI4I 2020 Maintenance | `archive.ics.uci.edu/dataset/601` | 10k records, labeled failure type |
| Azure Predictive Maintenance | `kaggle.com/datasets/arnabbiswas1/microsoft-azure-predictive-maintenance` | Dữ liệu máy công nghiệp |

```bash
kaggle datasets download -d arnabbiswas1/microsoft-azure-predictive-maintenance -p data/
```

### Kiến trúc
```
IoT Sensor Data (real-time)
      ↓
Anomaly Detection     → ML model phát hiện bất thường (Isolation Forest / LSTM)
RUL Prediction        → Ước tính Remaining Useful Life
      ↓
[Khi threshold vượt ngưỡng]
      ↓
Schedule Agent        → Kiểm tra lịch sản xuất, chọn thời điểm tối ưu
Inventory Agent       → Kiểm tra kho phụ tùng
Assign Agent          → Chọn kỹ thuật viên phù hợp
      ↓
Work Order Creation   → Tạo WO trên CMMS (Computerized Maintenance Management)
Notification          → Slack/Email cho kỹ thuật viên + manager
```

### Tech Stack
```
ML Model:    LSTM (time-series) hoặc Isolation Forest
Framework:   LangChain (Agent layer)
Model:       deepseek-r1:7b
Data:        InfluxDB hoặc TimescaleDB (time-series)
CMMS:        Limble CMMS API hoặc custom
```

---

## A10. Tối ưu Kho bãi

### Ý nghĩa
Tồn kho quá nhiều → đọng vốn, hàng hết hạn. Tồn kho quá ít → hết hàng, mất doanh thu. Cân bằng tồn kho tối ưu đòi hỏi phân tích nhiều yếu tố: seasonal demand, lead time, promotions, external events.

### Tại sao cần Agent?
ML forecasting dự đoán demand. Agent ra **quyết định mua hàng**: tính reorder point, lượng đặt tối ưu (EOQ), xem xét discount từ nhà cung cấp, cân nhắc sự kiện sắp tới (khuyến mãi, lễ tết), và **tự tạo Purchase Order**.

### Input / Output

**Input:**
```
Sản phẩm: Nước giặt OMO 3kg
- Tồn kho hiện tại: 150 thùng
- Tốc độ bán: 45 thùng/ngày (trung bình 30 ngày qua)
- Lead time nhà cung cấp: 3 ngày
- Sự kiện sắp tới: Khuyến mãi 11.11 (còn 14 ngày)
```

**Output:**
```
📊 PHÂN TÍCH TỒN KHO — Nước giặt OMO 3kg
─────────────────────────────────────────
Tình trạng: ⚠️ CẦN ĐẶT HÀNG NGAY

Dự báo:
- Nhu cầu thông thường: 45 thùng/ngày
- Nhu cầu dịp 11.11 (dự kiến): +180% → ~126 thùng/ngày (3 ngày)
- Tổng nhu cầu 14 ngày tới: 45×11 + 126×3 = 873 thùng
- Tồn kho hiện tại: 150 thùng → Thiếu 723 thùng

Đề xuất đặt hàng:
📦 Số lượng: 800 thùng
   (873 thiếu + 77 safety stock)
💰 Chi phí ước tính: 800 × 245,000đ = 196,000,000đ
📅 Đặt hàng: HÔM NAY để nhận trước 11.11

Lưu ý: Nhà cung cấp đang có chiết khấu 3% cho đơn ≥ 500 thùng
→ Tiết kiệm: ~5,880,000đ

✅ Purchase Order PO-20250517-088 đã được tạo, chờ phê duyệt.
```

### Data

| Dataset | Link | Dùng để |
|---|---|---|
| M5 Forecasting (Walmart) | `kaggle.com/competitions/m5-forecasting-accuracy` | 42k sản phẩm, 5 năm sales data |
| Retail Inventory Forecasting | `huggingface.co/datasets/Ammok/retail_store_inventory_forecasting` | Inventory + demand thực tế |
| Superstore Sales | `kaggle.com/datasets/vivek468/superstore-dataset-final` | Sales + returns + profit |

```bash
python -c "
from datasets import load_dataset
ds = load_dataset('Ammok/retail_store_inventory_forecasting', split='train[:200]')
ds.to_json('data/inventory_sample.jsonl')
"
```

### Kiến trúc
```
Historical Sales Data + Current Inventory
      ↓
Demand Forecasting    → ML model (SARIMA / Prophet / LightGBM)
Event Detection       → Lịch khuyến mãi, lễ tết, seasonality
      ↓
Reorder Agent         → Tính reorder point, EOQ
Supplier Agent        → So sánh giá, check discount, lead time
      ↓
PO Generation         → Tạo Purchase Order
Approval Workflow     → Gửi cho manager phê duyệt nếu > ngưỡng tiền
```

---

## Tổng hợp so sánh tất cả đề tài

| Đề tài | Độ khó | Dữ liệu | Impact | Phù hợp cho |
|---|---|---|---|---|
| AI Scrum Master | ⭐⭐⭐ | Dễ lấy | Cao | Tech team |
| HR Knowledge Bot | ⭐⭐ | Dễ lấy | Cao | Mọi công ty |
| Auto Code Review | ⭐⭐⭐ | Dễ lấy | Trung bình | Tech team |
| Research Assistant | ⭐⭐ | Dễ lấy | Cao | R&D, học thuật |
| Chatbot CSKH | ⭐⭐ | Trung bình | Rất cao | E-commerce, dịch vụ |
| Phân loại yêu cầu | ⭐ | Dễ lấy | Trung bình | Mọi công ty |
| Trích xuất báo cáo TC | ⭐⭐⭐ | Trung bình | Cao | Tài chính, đầu tư |
| Rà soát hợp đồng | ⭐⭐⭐⭐ | Khó | Cao | Pháp lý, procurement |
| Phát hiện gian lận AML | ⭐⭐⭐⭐ | Trung bình | Rất cao | Ngân hàng, fintech |
| Sàng lọc CV | ⭐⭐ | Dễ lấy | Cao | HR, recruitment |
| Predictive Maintenance | ⭐⭐⭐⭐ | Khó (IoT) | Rất cao | Sản xuất, logistics |
| Tối ưu kho bãi | ⭐⭐⭐ | Trung bình | Cao | Retail, logistics |

---

---

# Intern Implementation Guide

> Tài liệu này dành cho 2 thực tập sinh đọc và thực hiện trực tiếp.  
> Tech stack: **Python + LangGraph + Ollama (local) + ChromaDB**  
> Không cần API key trả phí.

---

## Môi trường chung (cả 2 intern cần setup)

```bash
# 1. Cài Ollama
# Windows: tải tại https://ollama.com/download
# Sau khi cài xong:
ollama pull deepseek-r1:7b
ollama pull nomic-embed-text

# 2. Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Cài thư viện
pip install langgraph langchain langchain-community \
            chromadb ollama streamlit \
            python-dotenv datasets requests \
            pypdf pdfplumber

# 4. Verify Ollama chạy được
python -c "import ollama; print(ollama.chat(model='deepseek-r1:7b', messages=[{'role':'user','content':'hello'}])['message']['content'])"
```

---

---

## Intern 1 — AI Scrum Master (Jimbo)

### Tổng quan bài toán

**Vấn đề**: PM tốn 2–4 giờ/sprint viết User Stories thủ công từ email yêu cầu mơ hồ của khách hàng.

**Giải pháp**: Agent tự đọc email → tra tài liệu kỹ thuật → viết User Stories chuẩn → tạo task trên Jira.

---

### Flow chi tiết

```
[INPUT] Email yêu cầu từ khách hàng (text)
        +
        Tài liệu kỹ thuật nội bộ (PDF/MD) ──► ChromaDB (đã index sẵn)
              │
              ▼
┌─────────────────────────────┐
│      RESEARCHER NODE        │  ← Query ChromaDB lấy: stack tech,
│  (LangGraph Node 1)         │    API docs, US cũ tương tự
└────────────┬────────────────┘
             │ context (stack, constraints, examples)
             ▼
┌─────────────────────────────┐
│       PLANNER NODE          │  ← Viết User Stories:
│  (LangGraph Node 2)         │    As a / I want / So that
└────────────┬────────────────┘    + AC (Given/When/Then)
             │ draft user stories  + Story Points
             ▼                     + Tasks (BE/FE/QA)
┌─────────────────────────────┐
│      EVALUATOR NODE         │  ← Kiểm tra: format đúng chưa?
│  (LangGraph Node 3)         │    AC đủ chưa? Points hợp lý?
└────────────┬────────────────┘
             │ APPROVED / REVISION
             ▼
      [REVISION LOOP] ──────────────────────► quay lại Planner nếu cần
             │ APPROVED
             ▼
┌─────────────────────────────┐
│      ACTION NODE            │  ← Gọi Jira REST API
│  (LangGraph Node 4)         │    tạo Issues tự động
└────────────┬────────────────┘
             │
             ▼
[OUTPUT] User Stories hoàn chỉnh + Jira Issues đã tạo
```

---

### Input / Output mẫu

**Input:**
```
"Khách hàng muốn thêm tính năng đặt lại mật khẩu qua email.
Backend đang dùng Node.js + JWT. Cần xong trước Sprint 13."
```

**Output mong đợi:**
```
USER STORY: Password Reset via Email
Priority: Medium | Points: 3 | Sprint: 13

As a registered user,
I want to reset my password via a link sent to my email,
so that I can regain access when I forget my password.

Acceptance Criteria:
- Given I click "Forgot Password" and enter my email,
  When the email exists in the system,
  Then I receive a reset link within 60 seconds.
- Given I click the reset link,
  When the link is still valid (< 1 hour),
  Then I can set a new password.
- Given the reset link has expired,
  When I try to use it,
  Then I see: "Link expired. Please request a new one."

Tasks:
  [BE-01] Create /auth/forgot-password endpoint — 3h
  [BE-02] Generate + store reset token (expires 1h) — 2h
  [BE-03] Send email via SendGrid/NodeMailer — 2h
  [BE-04] Create /auth/reset-password endpoint — 2h
  [FE-01] Build Forgot Password form — 2h
  [FE-02] Build Reset Password form — 2h
  [QA-01] Integration tests for full flow — 3h
```

---

### Sample Dataset & Repo

| Tài nguyên | Link | Dùng để |
|---|---|---|
| SWE-bench | `princeton-nlp/SWE-bench` (HuggingFace) | GitHub issues thật làm mẫu |
| Scrum Guide PDF | scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf | RAG knowledge base |
| Atlassian User Stories Guide | atlassian.com/agile/project-management/user-stories | RAG knowledge base |
| CrewAI Examples | github.com/crewAIInc/crewAI-examples | Tham khảo cách setup crew |
| LangGraph Examples | github.com/langchain-ai/langgraph/tree/main/examples | Tham khảo stateful graph |

```bash
# Tải sample data
python -c "
from datasets import load_dataset
ds = load_dataset('princeton-nlp/SWE-bench', split='test[:50]')
ds.to_json('data/swe_bench_sample.jsonl')
print('Sample:', ds[0]['problem_statement'][:200])
"

# Tải Scrum Guide
curl -L "https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf" -o data/scrum_guide.pdf
```

---

### Target theo tuần

| Tuần | Mục tiêu | Deliverable kiểm tra |
|---|---|---|
| 1 | Setup môi trường. Chạy được deepseek-r1:7b qua Ollama. Đọc 20 samples SWE-bench, hiểu cấu trúc. | `ollama run deepseek-r1:7b` trả lời được. Tóm tắt được 3 issues từ SWE-bench. |
| 2 | Ingest Scrum Guide + Atlassian docs vào ChromaDB. Test retrieval với 10 câu hỏi về Scrum. | Script `ingest.py` chạy thành công. Truy xuất đúng chunk khi hỏi "User Story format là gì?". |
| 3 | Viết Planner Node đơn lẻ. Cho input 5 requirements mẫu, xem output. | Planner trả ra User Story có đủ As a / I want / So that + ít nhất 2 AC. |
| 4 | Thêm Researcher Node + Evaluator Node. Kết nối thành LangGraph đầy đủ với revision loop. | Graph chạy end-to-end không crash. Evaluator detect được US thiếu AC. |
| 5 | Kết nối Jira API (hoặc mock). Test tạo issue tự động. | Một issue thật xuất hiện trên Jira board sau khi chạy pipeline. |
| 6 | End-to-end test với 10 requirements khác nhau. Fix lỗi phát sinh. | 8/10 trường hợp output đúng format. Log rõ lỗi 2 trường hợp còn lại. |
| 7 | Tạo 30 Ground Truth samples. Viết `evaluate.py`. Chạy baseline evaluation. | File `ground_truth.json` có 30 cặp. Script in ra: format_score, ac_score, points_score. |
| 8 | Tune prompt dựa trên kết quả tuần 7. Cải thiện ít nhất 10% so với baseline. | So sánh metrics tuần 7 vs tuần 8 trong file `evaluation_results.csv`. |
| 9 | Thêm Guardrails. Dockerize. Test bảo mật cơ bản (prompt injection). | `docker build` thành công. Agent không bị lừa bởi 5 adversarial prompts. |
| 10 | Viết báo cáo kỹ thuật. Chuẩn bị demo live. | File `report.md` + demo chạy được với 3 requirements mới chưa test. |

---

### WBS — Chia task chi tiết

#### Giai đoạn 1: Foundation (Tuần 1–2)

```
[TASK-1.1] Setup môi trường
  ├── Cài Ollama, pull deepseek-r1:7b + nomic-embed-text
  ├── Tạo project structure theo thư mục đã định
  └── Verify: chạy được LLM, embedding hoạt động
  Ước tính: 4h | Done khi: script test_setup.py pass

[TASK-1.2] Thu thập và hiểu dữ liệu
  ├── Tải SWE-bench 50 samples → phân tích cấu trúc
  ├── Tải Scrum Guide PDF
  ├── Crawl 3 trang Atlassian
  └── Viết note: "Tôi hiểu input/output của bài toán này là..."
  Ước tính: 6h | Done khi: note được mentor approve

[TASK-1.3] Build RAG pipeline
  ├── Viết ingest.py: load PDF + web → chunk → embed → lưu ChromaDB
  ├── Viết search.py: query → retrieve top-k chunks
  └── Test: 10 câu hỏi về Scrum, đánh giá kết quả thủ công
  Ước tính: 8h | Done khi: 8/10 câu retrieve đúng chunk
```

#### Giai đoạn 2: Core Agents (Tuần 3–4)

```
[TASK-2.1] Planner Node
  ├── Viết system prompt cho Planner
  ├── Test với 5 requirements mẫu
  ├── Đánh giá output thủ công theo checklist format
  └── Iterate prompt cho đến khi 4/5 đạt format chuẩn
  Ước tính: 10h | Done khi: 4/5 samples đúng format

[TASK-2.2] Researcher Node
  ├── Viết node query ChromaDB dựa trên requirement
  ├── Format context cho Planner dễ dùng
  └── Test: researcher có lấy đúng thông tin stack tech không
  Ước tính: 6h

[TASK-2.3] Evaluator Node
  ├── Viết checklist đánh giá (format, AC, points, tasks)
  ├── Viết prompt cho Evaluator
  ├── Test: cho Evaluator các US tốt và xấu → kiểm tra phân biệt được không
  └── Implement revision loop trong LangGraph
  Ước tính: 8h | Done khi: Evaluator reject US thiếu AC

[TASK-2.4] Kết nối LangGraph
  ├── Define StateGraph với 4 nodes
  ├── Define edges + conditional edge (approve/revise)
  ├── Test full graph end-to-end
  └── Giới hạn max 3 revision cycles để tránh infinite loop
  Ước tính: 8h
```

#### Giai đoạn 3: Integration (Tuần 5–6)

```
[TASK-3.1] Jira Tool
  ├── Đọc Jira REST API docs
  ├── Viết jira_tool.py: create_issue(), add_comment()
  ├── Test với Jira sandbox (free tier)
  └── Xử lý lỗi: auth fail, network timeout
  Ước tính: 8h

[TASK-3.2] End-to-end Testing
  ├── Chuẩn bị 10 requirements test cases đa dạng
  ├── Chạy pipeline, ghi lại kết quả
  ├── Identify top 3 failure modes
  └── Fix ít nhất 2 failure modes
  Ước tính: 10h
```

#### Giai đoạn 4: Evaluation & Polish (Tuần 7–8)

```
[TASK-4.1] Ground Truth Dataset
  ├── Viết 30 cặp (input requirement → expected US)
  ├── Đảm bảo đa dạng: BE-heavy, FE-heavy, full-stack, ambiguous
  └── Format JSON chuẩn
  Ước tính: 6h

[TASK-4.2] Evaluation Script
  ├── Viết evaluate.py
  ├── Metrics: format_score, ac_score, points_score, task_score
  ├── Chạy baseline, lưu results
  └── Visualize kết quả bằng bảng markdown
  Ước tính: 6h

[TASK-4.3] Prompt Tuning
  ├── Phân tích failure cases từ evaluation
  ├── Thử 3 phiên bản prompt khác nhau
  ├── Chọn phiên bản tốt nhất
  └── Document: tại sao prompt này tốt hơn
  Ước tính: 8h
```

#### Giai đoạn 5: Production & Demo (Tuần 9–10)

```
[TASK-5.1] Guardrails
  ├── List 5 failure scenarios cần handle
  ├── Implement input validation
  ├── Implement output validation
  └── Test adversarial prompts
  Ước tính: 6h

[TASK-5.2] Dockerize
  ├── Viết Dockerfile
  ├── Viết docker-compose.yml (app + ollama service)
  ├── Test: docker build + run thành công
  └── Viết README với hướng dẫn chạy
  Ước tính: 4h

[TASK-5.3] Báo cáo & Demo
  ├── Viết report.md: problem, architecture, results, limitations
  ├── Chuẩn bị 3 demo cases (easy/medium/hard)
  ├── Rehearse demo 1 lần trước khi present
  └── Chuẩn bị câu trả lời cho 5 câu hỏi khó
  Ước tính: 8h
```

---

---

## Intern 2 — HR Knowledge Bot

### Tổng quan bài toán

**Vấn đề**: Nhân viên hỏi HR cùng câu hỏi lặp lại hàng chục lần/tuần. HR mất thời gian trả lời thủ công. Ngoài giờ hành chính thì không có ai trả lời.

**Giải pháp**: Bot đọc toàn bộ tài liệu HR nội bộ, trả lời 24/7, trích dẫn nguồn chính xác, escalate khi không chắc.

---

### Flow chi tiết

```
[INPUT] Câu hỏi từ nhân viên (Slack / Web)
              │
              ▼
┌─────────────────────────────┐
│    INTENT CLASSIFIER        │  ← Phân loại: nghỉ phép / lương /
│    (LangChain Chain)        │    công tác / kỷ luật / khác
└────────────┬────────────────┘
             │ intent + entities
             ▼
┌─────────────────────────────┐
│    SENSITIVITY CHECK        │  ← Câu hỏi nhạy cảm (lương người khác,
│    (Rule-based)             │    khiếu nại)? → ESCALATE ngay
└────────────┬────────────────┘
             │ OK to proceed
             ▼
┌─────────────────────────────┐
│    RAG RETRIEVAL            │  ← Query ChromaDB với câu hỏi
│    (ChromaDB)               │    lấy top-4 chunks liên quan nhất
└────────────┬────────────────┘
             │ relevant chunks + source metadata
             ▼
┌─────────────────────────────┐
│    ANSWER GENERATOR         │  ← LLM tổng hợp câu trả lời
│    (Ollama + LangChain)     │    từ chunks, thêm trích dẫn nguồn
└────────────┬────────────────┘
             │ answer + sources
             ▼
┌─────────────────────────────┐
│    CONFIDENCE CHECK         │  ← Số chunks lấy được < 2?
│    (Rule-based)             │    → Thêm disclaimer hoặc escalate
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│    MEMORY UPDATE            │  ← Lưu lượt hội thoại này vào
│    (ConversationMemory)     │    window memory (5 lượt gần nhất)
└────────────┬────────────────┘
             │
             ▼
[OUTPUT] Câu trả lời + Nguồn trích dẫn
         hoặc "Kết nối với HR" nếu escalate
```

---

### Input / Output mẫu

**Input:**
```
"Mình đi công tác Hà Nội 3 ngày thì được thanh toán những khoản gì?
Mình có thể book khách sạn trước rồi thanh toán sau không?"
```

**Output mong đợi:**
```
Theo chính sách công tác của công ty, chuyến công tác Hà Nội của bạn
sẽ được thanh toán các khoản sau:

KHOẢN ĐƯỢC THANH TOÁN:
• Vé máy bay/tàu khứ hồi: theo giá thực tế (hạng Economy)
• Khách sạn: tối đa 800,000đ/đêm (Hà Nội thuộc nhóm đô thị loại 1)
• Phụ cấp ăn uống: 200,000đ/ngày (không cần hóa đơn)
• Taxi sân bay: theo hóa đơn thực tế

VỀ VIỆC BOOK TRƯỚC:
Bạn có thể book khách sạn trước và thanh toán bằng tiền cá nhân,
sau đó hoàn ứng theo quy trình: nộp hóa đơn + form HR-CT-002
cho kế toán trong vòng 5 ngày làm việc sau khi về.

📄 Nguồn: Quy chế Công tác phí — Mục 3.1 và 3.4, cập nhật 01/2025
```

---

### Sample Dataset & Repo

| Tài nguyên | Link | Dùng để |
|---|---|---|
| HR Policy QA | `pirocheto/hr-policy-qa` (HuggingFace) | Cặp Q&A HR mẫu |
| Banking77 | `banking77` (HuggingFace) | Tham khảo intent classification |
| Bitext Customer Support | `bitext/Bitext-customer-support-llm-chatbot-training-dataset` | Cách viết câu trả lời thân thiện |
| LangChain RAG Tutorial | github.com/langchain-ai/rag-from-scratch | Tham khảo RAG implementation |
| Slack Bolt Python | github.com/slackapi/bolt-python | Tích hợp Slack |

```bash
# Tải HR Policy dataset mẫu
python -c "
from datasets import load_dataset
ds = load_dataset('pirocheto/hr-policy-qa', split='train')
ds.to_json('data/hr_policy_qa.jsonl')
print(f'Total: {len(ds)} samples')
print('Sample:', ds[0])
"

# Tải intent reference
python -c "
from datasets import load_dataset
ds = load_dataset('banking77', split='train[:200]')
ds.to_json('data/intent_reference.jsonl')
"
```

**Tài liệu RAG mẫu nếu chưa có nội bộ:**
```bash
# Tải SHRM HR Guidelines (public)
curl -L "https://www.shrm.org/resourcesandtools/tools-and-samples/policies/pages/default.aspx" \
     -o data/shrm_policies.html

# Hoặc dùng Wikipedia HR policies làm placeholder
python -c "
from langchain_community.document_loaders import WikipediaLoader
docs = WikipediaLoader(query='Employee benefits paid leave policy', load_max_docs=3).load()
for i, d in enumerate(docs):
    open(f'data/wiki_hr_{i}.txt','w').write(d.page_content)
"
```

---

### Target theo tuần

| Tuần | Mục tiêu | Deliverable kiểm tra |
|---|---|---|
| 1 | Setup môi trường. Chạy được qwen2.5:7b qua Ollama. Đọc HR Policy dataset, hiểu cấu trúc Q&A. | Model trả lời được câu hỏi cơ bản. Tóm tắt 5 loại câu hỏi HR phổ biến. |
| 2 | Ingest tài liệu HR (ít nhất 2 PDF) vào ChromaDB. Test retrieval với 10 câu hỏi thật. | Retrieval trả đúng chunk khi hỏi "nghỉ phép năm được mấy ngày?". |
| 3 | Viết RAG chain cơ bản với ConversationMemory. Test hội thoại 3–4 lượt liên tiếp. | Bot nhớ context: hỏi "ngày phép" rồi hỏi "thế còn phép không lương?" → trả lời liên kết được. |
| 4 | Thêm Intent Classifier + Sensitivity Checker. Test các câu hỏi nhạy cảm. | Bot block câu hỏi về lương người khác. Bot escalate khi hỏi về khiếu nại. |
| 5 | Kết nối Slack Bot (hoặc Streamlit UI nếu chưa có Slack). Test nhận và trả lời message. | Gửi tin nhắn trên Slack → bot trả lời trong 10 giây. |
| 6 | End-to-end test với 20 câu hỏi đa dạng. Đánh giá thủ công. Fix lỗi. | Ghi lại: bao nhiêu câu trả lời đúng, sai, escalate không cần thiết. |
| 7 | Tạo 30 Ground Truth samples (nhờ HR thật viết expected answer). Chạy evaluate.py. | File ground_truth.json + baseline metrics in ra terminal. |
| 8 | Cải thiện chunking strategy. Thử chunk size 300/500/800, so sánh retrieval quality. | Bảng so sánh 3 chunk size theo Precision@4. |
| 9 | Hoàn thiện Guardrails. Dockerize. Test edge cases: câu hỏi tiếng Anh, câu hỏi mơ hồ. | docker-compose up chạy được. Bot handle được 5 edge cases định nghĩa sẵn. |
| 10 | Viết báo cáo. Demo live với câu hỏi do mentor đặt ngẫu nhiên. | Trả lời đúng ít nhất 4/5 câu hỏi ngẫu nhiên trong demo. |

---

### WBS — Chia task chi tiết

#### Giai đoạn 1: Foundation (Tuần 1–2)

```
[TASK-1.1] Setup môi trường
  ├── Cài Ollama, pull qwen2.5:7b + nomic-embed-text
  ├── Tạo project structure
  └── Verify: LLM + embedding chạy được
  Ước tính: 4h

[TASK-1.2] Thu thập tài liệu HR
  ├── Xin ít nhất 2 tài liệu PDF từ HR nội bộ
  │   (hoặc dùng HR Policy dataset + Wikipedia làm placeholder)
  ├── Đọc kỹ, tự trả lời 10 câu hỏi HR thường gặp
  └── Viết danh sách: 10 câu hỏi phổ biến + expected answer
  Ước tính: 6h | Done khi: danh sách được mentor approve

[TASK-1.3] Build RAG pipeline
  ├── Viết ingest.py: load PDF → chunk (500 chars, overlap 100) → embed → ChromaDB
  ├── Lưu metadata: tên file, số trang, section
  ├── Viết search.py: semantic search top-4
  └── Test: hỏi 10 câu, đánh giá retrieved chunks có liên quan không
  Ước tính: 8h | Done khi: 8/10 câu retrieve chunk đúng
```

#### Giai đoạn 2: Core Pipeline (Tuần 3–4)

```
[TASK-2.1] RAG Chain với Memory
  ├── Viết generator.py dùng ConversationalRetrievalChain
  ├── Thêm ConversationBufferWindowMemory (k=5)
  ├── System prompt: chỉ trả lời từ context, không suy đoán
  └── Test: hội thoại 5 lượt, kiểm tra memory hoạt động
  Ước tính: 10h | Done khi: bot nhớ được context từ lượt trước

[TASK-2.2] Intent Classifier
  ├── Định nghĩa 6 intent: leave/salary/travel/discipline/onboarding/other
  ├── Viết classifier (dùng LLM với few-shot examples)
  ├── Test với 20 câu hỏi đa dạng
  └── Đạt accuracy > 85%
  Ước tính: 6h

[TASK-2.3] Sensitivity & Guardrails
  ├── Viết danh sách BLOCK patterns (lương người khác, thông tin cá nhân)
  ├── Viết danh sách ESCALATE patterns (khiếu nại, tranh chấp, sa thải)
  ├── Viết checker.py
  └── Test: 10 câu nhạy cảm → 10/10 phải bị handle đúng
  Ước tính: 6h | Done khi: 100% sensitive cases handled
```

#### Giai đoạn 3: Integration (Tuần 5–6)

```
[TASK-3.1] Interface
  Option A — Slack Bot (khuyến nghị):
    ├── Tạo Slack App, lấy Bot Token + App Token
    ├── Viết slack_bot.py dùng Slack Bolt
    └── Test: gửi tin nhắn → bot reply trong 10s
  
  Option B — Streamlit (nếu chưa có Slack workspace):
    ├── Viết app.py với chat interface
    ├── Hiển thị sources bên dưới câu trả lời
    └── Test: chạy được trên localhost:8501
  Ước tính: 8h

[TASK-3.2] Source Citation
  ├── Đảm bảo mỗi câu trả lời kèm tên file + số trang
  ├── Format: "📄 Nguồn: [tên tài liệu], Mục [X.X]"
  └── Test: citation có khớp với nội dung trả lời không
  Ước tính: 4h

[TASK-3.3] End-to-end Testing
  ├── Test 20 câu hỏi đa dạng (5 loại intent)
  ├── Ghi kết quả: đúng / sai / escalate không cần / miss escalate
  ├── Identify top 3 failure modes
  └── Fix ít nhất 2
  Ước tính: 8h
```

#### Giai đoạn 4: Evaluation & Tuning (Tuần 7–8)

```
[TASK-4.1] Ground Truth Dataset
  ├── Nhờ HR viết expected answer cho 30 câu hỏi
  ├── Bao gồm: 20 câu trả lời được + 10 câu cần escalate
  └── Format JSON chuẩn với expected_answer + expected_source + expected_escalate
  Ước tính: 6h (bao gồm thời gian xin HR)

[TASK-4.2] Evaluation Script
  ├── Viết evaluate.py
  ├── Metrics: answer_accuracy, escalation_precision, citation_rate
  ├── Chạy baseline
  └── In report ra terminal + lưu CSV
  Ước tính: 6h

[TASK-4.3] Chunking Optimization
  ├── Thử 3 chunk sizes: 300, 500, 800
  ├── Đo Precision@4 cho mỗi config
  ├── Chọn config tốt nhất
  └── Document kết quả
  Ước tính: 6h
```

#### Giai đoạn 5: Production & Demo (Tuần 9–10)

```
[TASK-5.1] Edge Cases
  ├── Câu hỏi tiếng Anh → bot trả lời tiếng Việt
  ├── Câu hỏi mơ hồ → bot hỏi lại để làm rõ
  ├── Câu hỏi không liên quan HR → từ chối nhẹ nhàng
  ├── Câu hỏi kết hợp 2 chủ đề → trả lời cả 2
  └── Test 5 edge cases, đảm bảo handle được hết
  Ước tính: 6h

[TASK-5.2] Dockerize
  ├── Viết Dockerfile
  ├── Viết docker-compose.yml
  ├── Test build + run
  └── Viết README
  Ước tính: 4h

[TASK-5.3] Báo cáo & Demo
  ├── Viết report.md: problem, architecture, results, limitations
  ├── Chuẩn bị 5 câu hỏi demo (dễ → khó → nhạy cảm → edge case)
  ├── Rehearse
  └── Chuẩn bị câu trả lời cho 5 câu hỏi mentor có thể hỏi
  Ước tính: 8h
```

---

## Quy tắc chung cho cả 2 Intern

### Daily
- Cuối mỗi ngày: update task nào đang làm, blocker là gì vào group chat
- Nếu stuck > 2 tiếng: hỏi ngay, không tự ngồi đợi

### Weekly
- Đầu tuần: confirm mục tiêu tuần này
- Cuối tuần: demo deliverable cho mentor (dù chưa xong hoàn toàn)

### Code
- Commit code lên Git mỗi ngày
- Mỗi task = 1 branch, merge khi xong
- Không commit file `.env` chứa API keys

### Khi gặp khó khăn
1. Google + đọc docs chính thức (15 phút)
2. Hỏi ChatGPT/Claude để debug (15 phút)
3. Nếu vẫn không ra → hỏi mentor ngay, đừng đợi

### Tài liệu phải đọc trước tuần 1
- LangGraph Quickstart: python.langchain.com/docs/langgraph
- Ollama Python: github.com/ollama/ollama-python
- ChromaDB Getting Started: docs.trychroma.com/getting-started
