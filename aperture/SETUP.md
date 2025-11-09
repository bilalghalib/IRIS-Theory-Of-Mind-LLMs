# Aperture Setup Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Supabase Setup

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project (choose any region)
3. Wait for the project to initialize (~2 minutes)
4. Go to **SQL Editor** in the left sidebar
5. Click **+ New Query**
6. Copy the entire contents of `aperture/db/schema.sql`
7. Paste and click **Run**
8. Verify tables were created: Go to **Table Editor** and you should see:
   - users
   - conversations
   - messages
   - assessments
   - evidence
   - constructs
   - response_tracking

### Step 2: Get Your API Keys

#### Supabase Keys
1. In your Supabase project, go to **Settings** → **API**
2. Copy these values:
   - **URL**: Under "Project URL"
   - **anon public**: Under "Project API keys" → "anon public"
   - **service_role**: Under "Project API keys" → "service_role" (click "Reveal")

#### LLM Provider Key (choose one)

**Option A: OpenAI**
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create account / sign in
3. Go to API keys
4. Create new secret key
5. Copy it (starts with `sk-`)

**Option B: Anthropic**
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create account / sign in
3. Go to API keys
4. Create new key
5. Copy it (starts with `sk-ant-`)

### Step 3: Configure Environment

```bash
cd aperture
cp .env.example .env
nano .env  # or use your favorite editor
```

Fill in these values:

```env
# Supabase (from Step 2)
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=your-anon-public-key
SUPABASE_SERVICE_KEY=your-service-role-key

# LLM Provider (from Step 2)
OPENAI_API_KEY=sk-your-openai-key
# OR
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Aperture API Key (choose any secure string)
APERTURE_API_KEY=your-secret-api-key-for-testing

# Other settings (can leave as defaults)
ENVIRONMENT=development
SHORT_LINK_DOMAIN=localhost:8000
DEFAULT_ASSESSMENT_MODEL=gpt-4o-mini
ASSESSMENT_TEMPERATURE=0.3
```

### Step 4: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Run the Server

```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 6: Test It!

Open a new terminal and run:

```bash
python example_client.py
```

You should see a demo conversation with assessments being extracted!

## ✅ Verify Setup

1. Open browser: http://localhost:8000
2. You should see: `{"name": "Aperture API", ...}`
3. Open docs: http://localhost:8000/docs
4. You should see interactive API documentation

## 🐛 Troubleshooting

### "Connection refused" or "Cannot connect to Supabase"
- Check your `SUPABASE_URL` is correct
- Make sure you're using the service_role key (not anon key) for `SUPABASE_SERVICE_KEY`

### "Invalid API key" from OpenAI/Anthropic
- Make sure key starts with `sk-` (OpenAI) or `sk-ant-` (Anthropic)
- Check you have credits/billing set up in the provider dashboard

### "Table doesn't exist"
- Go back to Supabase SQL Editor
- Re-run the schema.sql file
- Check for any error messages in the SQL output

### Dependencies won't install
- Make sure you're using Python 3.9+: `python --version`
- Try upgrading pip: `pip install --upgrade pip`
- On Mac with M1/M2, you may need: `brew install postgresql` first

### Assessment extraction not working
- Check your `OPENAI_API_KEY` is set in .env
- Assessments extract in background (wait ~3 seconds)
- Check server logs for errors

## 🎯 Next Steps

1. Modify `example_client.py` to test different conversations
2. Check the "Why this response?" links in your browser
3. Try the user correction flow
4. Integrate into your own application!

## 📚 Documentation

- Full API docs: http://localhost:8000/docs
- Main README: [README.md](README.md)
- Database schema: [db/schema.sql](db/schema.sql)

## 💬 Need Help?

Open an issue on GitHub or check the README for more details.

Happy building! 🚀
