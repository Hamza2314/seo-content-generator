
# 🧠 AI-Powered SEO Landing Page Generator

This project automates the creation of SEO-optimized landing pages for law firms using AI. It generates high-quality content based on a user-defined topic by leveraging OpenAI's GPT models and (soon) SEMrush for keyword analysis.

---

## 🚀 Project Goals

- Generate SEO-optimized content for legal topics
- Match or exceed the quality of top-ranking Google pages
- Produce human-like, undetectable AI content
- Automate content formatting, image generation, and export
- Provide an easy-to-use frontend for law firms or admins

---

## ✅ Current Features (MVP Stage 1)

1. **Keyword Generation**
   - Input: A topic (e.g., *"Scheidung Anwalt Berlin"*)
   - Output: Top 10 localized keywords (via GPT, SEMrush planned)

2. **Outline Generator**
   - Creates a structured H2/H3 outline for the landing page
   - Uses keywords to ensure SEO alignment

3. **Section Content Generator**
   - Iterates over each outline point
   - Writes persuasive, SEO-rich content (100–150 words/section)

4. **PDF/Word Export** *(planned)*
   - Compiles generated content into a downloadable document

---

## 🧰 Tech Stack

- **Language**: Python
- **AI API**: OpenAI GPT-4o
- **Environment**: `dotenv`, local dev via VS Code
- **Framework (planned)**: Streamlit or Flask for UI
- **Other integrations (planned)**:
  - SEMrush (API)
  - DALL·E (image generation)
  - AI content detection tool (e.g., GPTZero)

---

## 🧩 Folder Structure

```
├── main.py               # Main pipeline (runs end-to-end)
├── ai_utils.py           # Functions: keyword, outline, section generation
├── .env                  # OpenAI API key
├── requirements.txt      # Python dependencies
└── output/               # (planned) Stores exported documents
```

---

## 🛠️ Next Development Steps

1. **🔑 Integrate SEMrush**
   - Replace GPT keyword generator with SEMrush keyword API
   - Accept access credentials from client

2. **📃 Section Generator Upgrade**
   - Add paragraph style, anchor link hints, and optional references
   - Add optional PDF/URL input for tone/structure mirroring

3. **🧪 AI Detection + Rewriting**
   - Integrate AI detection (simulated or real)
   - Rewrite flagged content iteratively

4. **🖼 Image Generator**
   - Use DALL·E or similar to embed 1–2 visuals per topic

5. **📤 Export & Delivery**
   - Output content as DOCX and PDF
   - Save structured file with H2/H3 sections and embedded images

6. **🖥 Streamlit Interface**
   - Input: Topic, tone example (optional), custom keywords (optional)
   - Output: Display + Download SEO-optimized landing page

7. **📦 Deployment**
   - Initial version hosted externally (Streamlit Cloud or VPS)
   - Optional migration to Hostinger server if needed

---

## 📄 License

To be defined after client agreement (likely proprietary under work contract).
