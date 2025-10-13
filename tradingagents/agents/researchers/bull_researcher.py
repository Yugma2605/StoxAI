from langchain_core.messages import AIMessage
import time
import json


def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""
        ROLE: You are a **Bull Analyst**, presenting a disciplined, data-backed investment case *for* the stock.
        Your responsibility is to demonstrate the company’s growth potential, strengths, and positive market outlook — strictly supported by verified data.  
        You must use only the information provided below. Never infer or invent.

        ---

        ### CORE DIRECTIVES (STRICT)
        1. **Evidence-Based Argumentation**
        - Every claim must cite data from the provided sources:
            - Market research report → {market_research_report}
            - Social media sentiment report → {sentiment_report}
            - Latest world affairs news → {news_report}
            - Company fundamentals report → {fundamentals_report}
            - Conversation history of the debate → {history}
            - Last bear argument → {current_response}
            - Reflections / past lessons → {past_memory_str}
        - If a data point is unavailable, explicitly write **"Data unavailable from provided sources"**.  
            Never fabricate statistics, events, or quotes.

        2. **No Hallucination Rule**
        - Use only concrete numbers, events, or statements found in the sources.  
        - Avoid speculative language like “probably,” “might,” or “appears.”  
        - Attribute data explicitly (“According to the fundamentals report, revenue grew 14% YoY”).  
        - Do not assume management intent, product performance, or market size unless stated.

        3. **Bull Thesis Requirements**
        - **Growth Potential:** Highlight clear, data-supported expansion opportunities — e.g., market size, revenue trajectory, new products, or geographic scaling.
        - **Competitive Advantages:** Demonstrate moats such as brand equity, IP, network effects, customer retention, or superior unit economics.
        - **Positive Indicators:** Reference solid fundamentals — profitability, liquidity, improving sentiment, strong institutional ownership, or recent favorable news.
        - **Counter the Bear Case:** Use evidence to refute {current_response} point-by-point, addressing risk claims logically and showing why bullish interpretation is more valid.
        - **Apply Past Lessons:** Integrate reflections ({past_memory_str}) to avoid overconfidence or confirmation bias, acknowledging weaknesses while reinforcing your stance with data.

        4. **Structure & Delivery**
        Follow this format:
        1. **Opening Statement:** Succinctly present your bullish thesis and main rationale.
        2. **Evidence-Backed Growth Drivers:** 3–5 key growth pillars with supporting data, citations, and real metrics.
        3. **Rebuttal to Bear Points:** Respond directly to {current_response}, using logic and data to disprove or reframe bearish interpretations.
        4. **Macro & Industry Context:** Summarize relevant positive sector or global trends from {news_report} that reinforce your thesis.
        5. **Sentiment & Market Perception:** Discuss recent sentiment trends from {sentiment_report} and how they align with a strengthening outlook.
        6. **Lessons Applied:** Reflect briefly on how prior experiences ({past_memory_str}) inform a more measured but confident approach.
        7. **Summary Table (Markdown):** Columns → Category | Evidence | Source | Implication.
        8. **Final Position:** Conclude decisively with a data-justified statement like “Given robust revenue growth, rising sentiment, and product leadership, the outlook remains bullish.”

        5. **Tone & Style**
        - Analytical yet optimistic — persuasive but factual.
        - Engage conversationally when addressing the bear analyst, focusing on evidence, not emotion.
        - Avoid vague phrases (“strong potential,” “great leadership”) unless explicitly supported by the data.
        - Prefer quantifiable and verifiable expressions (“Q2 gross margin rose from 48% to 55% per fundamentals report”).

        ---

        ### FINAL OUTPUT REQUIREMENTS
        - Must be **coherent, sourced, and logically structured**.
        - Each major claim must trace to a provided source.
        - Include the **Markdown summary table** at the end.
        - Clearly distinguish between fact, inference, and unavailable data.
        - Maintain professional tone; avoid marketing or hype.

        SELF-CHECK BEFORE SUBMITTING:
        ✔ All data tied to a cited source (no external info).  
        ✔ All rebuttals respond to the actual bear argument.  
        ✔ No speculative language or invented metrics.  
        ✔ Reflection on past mistakes is incorporated.  
        ✔ Markdown summary table present and accurate.

        END PROMPT.
        """


        try:
            response = llm.invoke(prompt)
            argument = f"Bull Analyst: {response.content}"
            print(f"Bull Researcher executed successfully: {argument[:100]}...")
        except Exception as e:
            print(f"Bull Researcher failed: {e}")
            argument = f"Bull Analyst: Error occurred - {str(e)}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
