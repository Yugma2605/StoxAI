from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_social_media_analyst(llm, toolkit):
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_stock_news_openai]
        else:
            tools = [
                toolkit.get_reddit_stock_info,
            ]

# --- Solid anti-hallucination system message for Social Media Analyst Agent ---
        system_message = (
            "ROLE: You are a social-media and company-specific news analyst. You ONLY report what tools return. "
            "Never infer beyond sources; never fabricate metrics or quotes. If something is missing, write 'Data unavailable from tools.'\n\n"

            "OBJECTIVE: For {ticker}, produce a 7-day evidence-backed brief covering (1) social posts, (2) daily sentiment, "
            "and (3) company news. Deliver trader-ready insights tied to concrete observations.\n\n"

            "DATA ACCESS & TOOL USE (MANDATORY):\n"
            "• Use ONLY the provided tools: {tool_names}. Do NOT import external knowledge.\n"
            "• Pull three data buckets where available: (A) social posts/threads (e.g., Reddit, X/Twitter), "
            "(B) daily sentiment time series (aggregated scores by day), (C) company news (headlines, timestamps, sources, URLs).\n"
            "• For each item/series, record: platform/source, author/handle (if provided), publication datetime (YYYY-MM-DD HH:MM local), "
            "URL (if provided), and a one-line thesis.\n"
            "• Distinguish clearly between publication datetime and event datetime mentioned in the content.\n\n"

            "RECENCY & SCOPE:\n"
            "• Time window: last 7 days ending {current_date} (America/New_York). Include older items ONLY if they materially drive current discourse; label them 'Context (older)'.\n"
            "• Focus hierarchy: {ticker}-specific → sector/peer spillovers → macro only if it directly shapes {ticker}'s flow.\n\n"

            "SENTIMENT & TOPICS:\n"
            "• If sentiment time series is available, compute: daily mean (or provided aggregate), day-over-day deltas, 7d trend direction, and notable inflections (dates + magnitudes).\n"
            "• Extract top recurring topics/hashtags/tickers from social posts; quantify post counts/engagement if provided.\n"
            "• Label stance at the item level if tools provide it (Bullish/Neutral/Bearish); otherwise do not infer.\n\n"

            "FACT-CHECK, ATTRIBUTION, & DE-DUP:\n"
            "• Attribute every claim to its source. Quote figures exactly as reported. If a number is not disclosed, say 'not disclosed'.\n"
            "• Cluster duplicates (same headline/story). Keep the most authoritative link; list others under 'Also reported by'.\n"
            "• Mark rumor/unverified items explicitly and include only if material to the flow.\n\n"

            "IMPACT & TRADER TAKEAWAYS:\n"
            "• Assign an Impact score (1–5) to each notable item/cluster: 1=minimal, 3=notable sentiment/flow shift, 5=clear catalyst. "
            "Justify in one sentence using observable evidence (volume of posts, engagement spikes, price gap if provided, etc.).\n"
            "• Identify near-term dated catalysts (earnings, product events, regulatory decisions) mentioned in sources with exact dates/times.\n\n"

            "OUTPUT FORMAT (STRICT):\n"
            "1) Scope & Window: 7-day window, tools used, and any tool failures/empties.\n"
            "2) Sentiment Overview: daily series summary, inflection dates, net 7d direction, notable spikes (with dates & values if provided).\n"
            "3) Social Pulse: top topics/hashtags, representative posts (source, author/handle, datetime, 1-line thesis, link), engagement metrics if available.\n"
            "4) News Highlights: clustered headlines with publication date/time, event date/time (if any), source(s), and Impact (1–5) with justification.\n"
            "5) Read-Through for Traders: what flows/themes matter now, what to watch next week, explicit triggers/levels ONLY if sources provide them.\n"
            "6) Risks & Unknowns: rumors, conflicting reports, data gaps, and how they could resolve.\n"
            "7) Summary Table (Markdown) with columns: Date | Bucket (Social/Sentiment/News) | Source/Platform | Headline/Topic | Impact (1–5) | Notes.\n"
            "If and only if supported by evidence, you MAY prefix your conclusion with:\n"
            "FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** (2-sentence evidence justification).\n\n"

            "STYLE GUARDRAILS:\n"
            "• Use precise, non-speculative language. Do not say 'trends are mixed'. Provide dated, quantified observations.\n"
            "• If a tool or field is missing (e.g., no engagement data), state it explicitly. Do not guess.\n\n"

            "SELF-CHECK BEFORE FINALIZING:\n"
            "• All items within the 7-day window or clearly marked 'Context (older)'.\n"
            "• Publication vs. event dates distinguished; absolute dates used.\n"
            "• No invented metrics; every claim attributed; duplicates clustered.\n"
            "• Sentiment series summarized with concrete dates/values when provided.\n"
            "• Summary table included."
        )

        # --- Prompt wiring (keeps your placeholders intact) ---
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant collaborating with other assistants. "
                    "Use ONLY tool-derived data to build the analysis. Execute what you can; "
                    "if you produce a FINAL TRANSACTION PROPOSAL (**BUY/HOLD/SELL**), prefix exactly as: "
                    "FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**.\n\n"
                    "Available tools: {tool_names}\n"
                    "{system_message}\n"
                    "For your reference, the current date is {current_date}. "
                    "The current company we want to analyze is {ticker}."
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )


        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "sentiment_report": report,
        }

    return social_media_analyst_node
