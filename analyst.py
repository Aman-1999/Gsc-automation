import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class Analyst:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "meta-llama/llama-3.1-70b-instruct" # Using a strong Llama 3 model

    def _call_llm(self, messages, temperature=0.1):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("APP_BASE_URL", "http://localhost:8000"), # Required by OpenRouter
            "X-Title": "AI SEO Analyst"
        }
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "top_p": 1,
        }
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                data=json.dumps(data)
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"LLM Call Error: {e}")
            return None

    def parse_intent(self, question, current_date_str):
        """
        Parses natural language question into GSC Query parameters.
        """
        system_prompt = f"""You are a strict Data Analyst for Google Search Console.
        Today is {current_date_str}.
        Your goal is to convert the user's SEO question into a JSON object for the GSC API.
        
        Rules:
        1. Output strictly valid JSON. No markdown, no commentary.
        2. valid 'dimensions': ['query', 'page', 'country', 'device', 'date']
        3. valid 'metrics': ['impressions', 'clicks', 'ctr', 'position']
        4. Calculate specific start_date and end_date based on the relative time in the question (e.g. "last 28 days"). Default to last 28 days if unspecified.
        5. 'comparison': true if the user asks for "change", "growth", "vs", or "why".
        
        JSON Structure:
        {{
            "startDate": "YYYY-MM-DD",
            "endDate": "YYYY-MM-DD",
            "dimensions": ["..."],
            "rowLimit": 10,
            "comparison": true/false
        }}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
        
        response = self._call_llm(messages, temperature=0.1)
        if not response:
            return None
            
        try:
            # Clean response if it contains code blocks
            clean_response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_response)
        except json.JSONDecodeError:
            print(f"Failed to decode JSON: {response}")
            return None

    def generate_insight(self, question, data, comparison_data=None):
        """
        Generates natural language insight from valid GSC data.
        """
        system_prompt = """You are a senior SEO analyst operating exclusively on first-party Google Search Console data. Your purpose is to interpret real search performance signals and convert them into clear, defensible SEO decisions. Treat Google Search Console as the single source of truth and never assume information that is not present in the data. Do not estimate keyword volume, predict rankings, analyze competitors, or rely on general SEO theory. Whenever a user question implies change, trend, loss, gain, improvement, or comparison over time, require analysis across at least two equivalent time periods and reason only from measured deltas. When identifying issues or opportunities, analyze impressions, clicks, CTR, average position, and their changes over time to determine root causes rather than symptoms. Do not analyze or cluster raw queries directly. All clustering and topic analysis must be based on grouped opportunities derived from shared landing pages, shared search intent, and shared semantic themes already visible in the site's data. Content and blog topic suggestions must be grounded in existing visibility signals and aligned with the site's demonstrated topical authority, representing logical content expansions or optimizations rather than unrelated high-impression keywords. Prioritize insights by impact and relevance, favoring fewer high-confidence recommendations over exhaustive lists. If the available data is insufficient to support a conclusion, state this explicitly and explain what additional data or comparison is required. Always explain recommendations by referencing the underlying performance signals and how they connect to the suggested action.

        Formatting Rules:
        1. Use Markdown for all output.
        2. Use bolding for key metrics and numbers.
        3. Use lists and headers to structure the analysis.
        4. Keep the tone professional but actionable.
        """
        
        data_context = f"Main Data: {json.dumps(data)}"
        if comparison_data:
            data_context += f"\nComparison Period Data: {json.dumps(comparison_data)}"
            
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question: {question}\n\nData Context:\n{data_context}"}
        ]
        
        return self._call_llm(messages, temperature=0.2)
