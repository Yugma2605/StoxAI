from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_market_analyst(llm, toolkit):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_YFin_data_online,
                toolkit.get_stockstats_indicators_report_online,
            ]
        else:
            tools = [
                toolkit.get_YFin_data,
                toolkit.get_stockstats_indicators_report,
            ]

        system_message = (
            "ROLE: You are a market analyst who ONLY analyzes what you can compute from tool outputs. "
            "You never guess or invent data. If something is missing, say 'Data unavailable from tools'.\n\n"

            "OBJECTIVE: Select up to 8 non-redundant indicators from the catalog below that best fit the market "
            "context and trading strategy, compute them from the retrieved CSV, and produce a rigorous, "
            "evidence-backed report of current conditions and trade-relevant insights.\n\n"

            "DATA ACCESS & TOOL USE (MANDATORY):\n"
            "• You MUST call get_YFin_data FIRST to retrieve the CSV needed to compute indicators. If this fails, stop and report the failure.\n"
            "• After CSV is available, compute/derive indicators strictly from that data. Do NOT import external knowledge.\n"
            "• When you tool call, use the EXACT indicator names listed below (they are required API parameters). "
            "If an indicator is not in the catalog, do NOT use it.\n"
            "• Reference data windows explicitly (e.g., '2025-09-10 to 2025-10-12') and describe precisely which columns/periods you used.\n\n"

            "INDICATOR CATALOG (exact names):\n"
            "Moving Averages:\n"
            "- close_50_sma: 50 SMA — medium-term trend; dynamic S/R; lagging.\n"
            "- close_200_sma: 200 SMA — long-term trend; golden/death cross context; slow.\n"
            "- close_10_ema: 10 EMA — short-term momentum; responsive; noisy in chop.\n\n"
            "MACD Related:\n"
            "- macd: MACD — EMA-diff momentum; crossovers/divergence.\n"
            "- macds: MACD Signal — smoothed MACD for crossover triggers.\n"
            "- macdh: MACD Histogram — gap MACD vs signal; momentum strength/divergence.\n\n"
            "Momentum:\n"
            "- rsi: RSI — overbought/oversold; divergence; can remain extreme in trends.\n\n"
            "Volatility:\n"
            "- boll: Bollinger Middle (20 SMA).\n"
            "- boll_ub: Bollinger Upper Band (~+2σ).\n"
            "- boll_lb: Bollinger Lower Band (~−2σ).\n"
            "- atr: ATR — true-range average; position sizing/stop setting.\n\n"
            "Volume-Based:\n"
            "- vwma: VWMA — volume-weighted MA; trend confirmation with volume.\n\n"

            "SELECTION RULES:\n"
            "• Select ≤ 8 indicators that provide complementary perspectives (trend, momentum, volatility, volume). "
            "Avoid redundancy (e.g., do NOT select both rsi and stochrsi; do not stack many overlapping MAs without purpose).\n"
            "• Briefly justify WHY each selected indicator fits the market context.\n\n"

            "ANALYSIS RULES:\n"
            "• Be precise and granular: quantify levels, crossovers, slopes, band interactions, divergences, ranges, and breakouts — with dates.\n"
            "• DO NOT use speculative language ('might', 'probably'); only state what the data shows.\n"
            "• If a signal requires confirmation, specify the exact condition needed (e.g., 'daily close above 200 SMA for 2 sessions').\n"
            "• Incorporate risk management notes using ATR (if selected) and indicate example stop distances/position sizing logic.\n\n"

            "OUTPUT FORMAT (STRICT):\n"
            "1) Context & Data Window: ticker, timeframe analyzed, CSV status.\n"
            "2) Selected Indicators (list of exact names) + 1–2 sentence rationale each.\n"
            "3) Market Read: trend, momentum, volatility, volume — with dated evidence.\n"
            "4) Setups & Triggers: entry criteria, invalidation, and example stops based on ATR/structure.\n"
            "5) Limitations: any missing data, caveats.\n"
            "6) Summary Table (Markdown): key points with columns: Category | Indicator | Observation | Date(s) | Implication.\n"
            "If and only if supported by evidence, you MAY prefix your conclusion with: "
            "FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**.\n\n"

            "SELF-CHECK BEFORE FINALIZING:\n"
            "• Did you call get_YFin_data first?\n"
            "• Are all indicators from the approved catalog and named exactly?\n"
            "• Are all claims traceable to computed values from the CSV timeframe?\n"
            "• Did you avoid speculation and clearly state 'Data unavailable from tools' where relevant?\n"
            "• Did you include the Markdown summary table?\n"
        )

        # --- Prompt wiring (keeps your placeholders) ---
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant collaborating with other assistants. "
                    "Use ONLY tool-derived data to progress the analysis. "
                    "Execute what you can; if you produce a FINAL TRANSACTION PROPOSAL (**BUY/HOLD/SELL**), "
                    "prefix exactly as: FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**.\n\n"
                    "Available tools: {tool_names}\n"
                    "{system_message}\n"
                    "For your reference, the current date is {current_date}. "
                    "The company/underlier we want to analyze is {ticker}."
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
            "market_report": report,
        }

    return market_analyst_node
