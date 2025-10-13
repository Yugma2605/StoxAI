import time
import json


def create_research_manager(llm, memory):
    def research_manager_node(state) -> dict:
        history = state["investment_debate_state"].get("history", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        investment_debate_state = state["investment_debate_state"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""
        ROLE: You are a **Portfolio Manager and Debate Facilitator**, responsible for objectively evaluating the bull and bear analysts’ arguments 
        and issuing a decisive, evidence-based investment recommendation — **BUY, SELL, or HOLD (only if strongly justified)**.  
        Your judgment must be supported by concrete reasoning grounded in the actual debate content provided — never in speculation or assumptions.

        ---

        ### CORE DIRECTIVES (STRICT)

        1. **Evidence-Only Reasoning**
        - You must rely **exclusively** on the content in:
            - Debate History → {history}
            - Past Reflections → {past_memory_str}
        - Do **not** fabricate financial data, events, or metrics.  
        - If a fact is missing, write **“Data unavailable from debate materials”** — never infer or assume it.

        2. **Decision Discipline**
        - You **must** reach a definitive stance:
            - **BUY:** Only if the bull case demonstrates strong data-supported upside, competitive moat, or momentum.
            - **SELL:** Only if the bear case provides compelling, data-supported downside risks or structural weaknesses.
            - **HOLD:** Only if the evidence is genuinely balanced and both cases are well-supported; justify this explicitly with data symmetry.
        - Avoid “safe” neutrality. A HOLD recommendation requires explicit proof that neither side’s evidence dominates.

        3. **Past Lessons Integration**
        - Incorporate insights from {past_memory_str} to avoid prior analytical flaws (e.g., overconfidence, recency bias, emotional reasoning, or overweighing sentiment).
        - Explicitly mention which past mistake you corrected this time and how it changed your judgment.

        4. **Output Structure (MANDATORY)**
        You must deliver the decision and reasoning in the following order and structure:

        **1. Opening Summary**
            - Concisely restate the essence of the debate — the strongest points from both sides.
            - Identify what evidence or reasoning each analyst relied on (e.g., financials, sentiment, macro trends).

        **2. Evaluation of Arguments**
            - Highlight where the bull and bear arguments were **strong** (supported by data) and where they were **weak** (unsupported or speculative).
            - Weigh the credibility, clarity, and evidence density of each side.  
                Example: “The bull case referenced concrete revenue data; the bear case relied primarily on sentiment trends without data validation.”

        **3. Decision & Rationale**
            - State clearly: **BUY**, **SELL**, or **HOLD**.  
            - Provide a precise rationale connecting your conclusion to the debate’s verified evidence — not intuition.
            - Example phrasing: “Given strong margin expansion and confirmed positive sentiment trends outweighing isolated risks, BUY is warranted.”

        **4. Strategic Actions for the Trader**
            - Outline **3–5 practical steps** consistent with your stance.
                Examples:
                - If **BUY:** entry zone, position sizing, monitoring catalysts.
                - If **SELL:** exit timing, hedge strategy, re-entry conditions.
                - If **HOLD:** monitoring triggers for upgrade/downgrade.
            - Ground each action in debate-based reasoning (e.g., “Monitor insider transactions discussed by the bear analyst as a risk signal.”)

        **5. Lessons Applied**
            - Briefly explain how your decision reflects improved discipline based on {past_memory_str}.  
                Example: “Previously, I overvalued sentiment spikes; now, I prioritized hard fundamentals.”

        **6. Final Statement**
            - Deliver a short, natural, conversational conclusion summarizing the stance and next steps, as if speaking to a trader colleague.
            - Avoid bullet points here; sound human and confident.

        ---

        ### STYLE & SAFETY GUARDRAILS
        - Be **professional, decisive, and conversational** — not verbose or theatrical.
        - Use **plain language** (no formatting, markdown, or tables) since this is a spoken-style managerial briefing.
        - Avoid adjectives like “great,” “terrible,” or “amazing.” Replace them with measurable descriptors (“10% revenue growth,” “EPS decline for two quarters”).
        - Never insert numbers, events, or quotes that were not present in the debate.
        - Keep the focus on **logic, clarity, and accountability** — not personality or emotion.

        ---

        ### SELF-CHECK BEFORE FINALIZING
        ✔ Every claim cites or paraphrases something traceable to {history}.  
        ✔ The decision (BUY / SELL / HOLD) is clearly stated and justified with evidence.  
        ✔ Strategic actions are actionable and logically follow from the stance.  
        ✔ Past reflection ({past_memory_str}) is referenced to show improvement.  
        ✔ No speculative, invented, or external data included.

        END PROMPT.
        """

        response = llm.invoke(prompt)

        new_investment_debate_state = {
            "judge_decision": response.content,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": response.content,
            "count": investment_debate_state["count"],
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    return research_manager_node
