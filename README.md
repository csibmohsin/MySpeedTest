# ⚡ MySpeedTest — Professional Python Internet Speed Test

A complete, high-precision commercial internet speed test platform built **100% in Python**. Inspired by Ookla Speedtest, **MySpeedTest** features a modern cyber-dark glassmorphic user interface with a real-time circular speedometer, live bandwidth telemetry curves, multi-threaded real network transfers, RFC 3550 standard jitter analysis, client IP/ISP topology detection, and SQLite persistence.

---

## 🌟 Key Features

### 1. 🎯 Circular Speedometer Dashboard
- **Ookla-Inspired Dial:** Large, beautiful circular gauge with neon cyan, purple, and amber accents.
- **Dynamic Scale Auto-Ranging:** Intelligently scales from 25 Mbps to 1000 Mbps based on connection speed.
- **Granular Live Updates:** Smooth real-time gauge needle and arc motion as network packets stream.

### 2. ⚡ Real Multi-Threaded Speed Engine
- **Download Speed:** Concurrent chunk streaming saturates the connection to measure true peak and average bandwidth (Mbps).
- **Upload Speed:** Real network uploads tracking raw bytes sent across multiple sockets to measure true peak and average upload speed (Mbps).
- **Sub-Millisecond Ping:** Multi-probe TCP connection handshake round-trip latency (ms).
- **RFC 3550 Standard Jitter:** Latency variance calculated using the official RFC 3550 standard equation:
  $$J = \frac{1}{N - 1} \sum_{i=1}^{N - 1} |L_{i+1} - L_i|$$
- **100% Real Transfers:** Zero mocked, fake, or hardcoded speed values.

### 3. 🌐 Client & Network Diagnostics
- **Public IP Detection:** Automatically detects public IPv4 address without hardcoding.
- **ISP & Autonomous System (ASN):** Identifies your Internet Service Provider and routing network.
- **Geographic Location:** City, region, and country detection.
- **Edge Server Matrix:** Live round-trip latency testing across distributed CDN edge nodes with auto-detection of the lowest-latency node.

### 4. 📈 Real-Time Telemetry & Historical Trends
- **Live Bandwidth Graphs:** Interactive Plotly area chart plotting real-time Download (Cyan) and Upload (Purple) curves during test execution.
- **SQLite History (`speedtest.db`):** Persistent storage of all tests including date/time, speeds, latency, jitter, ISP, and testing server.
- **Individual Record Deletion:** Remove individual records or clear history.
- **CSV Data Export:** One-click download of full history or single-test summaries.
- **Application Readiness Ratings:** Automated assessment for 4K UHD Streaming, Competitive Gaming, Zoom/Teams Video Conferencing, and Cloud Backups.

---

## 🏗️ Project Architecture

```
MySpeedTest/
│
├── app.py                  # Main Streamlit web application & Ookla-inspired dark UI
├── speed_engine.py         # Multi-threaded download/upload streaming & ping/jitter engine
├── network_info.py         # Client IP, ISP, location detection & edge server registry
├── history_manager.py      # SQLite database manager (CRUD, stats, CSV export)
├── requirements.txt        # Python dependency declarations
├── README.md               # Project documentation & deployment guides
└── speedtest.db            # Local SQLite database (auto-created on first run)
```

---

## 🚀 Getting Started Locally

### 1. Prerequisites
- Python 3.11 or higher
- `pip` package manager

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Application
Run the Streamlit application with:
```bash
streamlit run app.py
```

The application will start immediately and open in your default browser at:
`http://localhost:8501`

---

## ☁️ Deployment Instructions

> **Note:** GitHub Pages only hosts static HTML/JS and cannot execute Python backends. Use one of the Python-compatible hosting platforms below.

### Option 1: Streamlit Community Cloud (Recommended & Free)
1. Push your repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
3. Click **"New app"**, select your repository, branch (`main`), and set Main file path to `app.py`.
4. Click **"Deploy"** — your live speed test will be available at a public `*.streamlit.app` URL.

### Option 2: Render.com
1. Create a free account at [render.com](https://render.com).
2. Create a new **Web Service** linked to your GitHub repo.
3. Configure settings:
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
4. Deploy service.

### Option 3: Railway.app
1. Go to [railway.app](https://railway.app) and create a new project from your GitHub repo.
2. Under **Variables**, add `PORT=8501`.
3. Set Start Command to: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.
4. Generate domain and deploy.

### Option 4: Docker Container
Build and run the containerized application:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
```bash
docker build -t myspeedtest .
docker run -p 8501:8501 myspeedtest
```

---

## 🔒 Accuracy & Quality Standards
- **Zero Simulation:** Does not generate synthetic speeds; measures physical byte arrival/departure over the network.
- **Fail-Safe Networking:** Automatic fallback endpoints and error handling for slow or lossy connections.
- **RFC 3550 Compliance:** Industry-standard jitter calculations matching commercial telecom benchmarks.

