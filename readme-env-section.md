### Environment Setup

1. Create a copy of the environment example file:
```bash
# Copy the example environment file
cp env_template.sh .env.sh

# Make the environment file executable
chmod +x .env.sh
```

2. Edit `.env.sh` with your API keys:
```bash
DATABASE_CONNECTION = "your_database_connection"
GEMINI_API_KEY = "your_gemini_key"
OPENAI_API_KEY = "your_openai_key"
OPENAI_ORG = "your_openai_org"
MISTRAL_API_KEY = "your_mistral_key"
```

3. Load the environment variables:
```bash
# Source the environment file
source .env.sh
```

**Note**: Make sure to add `.env.sh` to your `.gitignore` file to prevent committing sensitive information.
