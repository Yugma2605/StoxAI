from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_fundamentals_analyst(llm, toolkit):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_fundamentals_openai]
        else:
            tools = [
                toolkit.get_finnhub_company_insider_sentiment,
                toolkit.get_finnhub_company_insider_transactions,
                toolkit.get_simfin_balance_sheet,
                toolkit.get_simfin_cashflow,
                toolkit.get_simfin_income_stmt,
            ]

        system_message = (
            "ROLE: You are a professional financial analyst specializing in fundamental equity research.\n\n"
            "OBJECTIVE: Generate a factual, data-driven report on the company’s fundamentals "
            "strictly based on verified information from the provided tools. "
            "Your goal is to assess the company’s financial health, insider activity, and business fundamentals "
            "to support informed trading decisions.\n\n"

            "CRITICAL INSTRUCTIONS (read carefully):\n"
            "1. You MUST rely ONLY on the data returned by the provided tools. Do NOT fabricate or assume numbers.\n"
            "2. If information is missing, explicitly state 'Data unavailable from tools' rather than guessing.\n"
            "3. Cite each insight clearly, linking it to the corresponding tool source (e.g., 'Based on SimFin income statement data...').\n"
            "4. Focus your analysis on:\n"
            "   - Profitability (revenue, margins, EPS trends)\n"
            "   - Liquidity & solvency (cashflow, debt ratios, working capital)\n"
            "   - Growth or decline trends\n"
            "   - Insider sentiment & transaction activity\n"
            "   - Any notable red flags or strengths\n"
            "5. End with a concise, reasoned qualitative outlook: **BUY / HOLD / SELL** based on evidence (not opinion).\n"
            "6. Include a Markdown summary table at the end organizing metrics, insights, and sources.\n"
            "7. Maintain analytical tone; avoid vague statements like 'mixed trends' or 'the company is doing well.'\n"
            "8. Never use speculative language (e.g., 'might', 'probably', 'expected to'). Use only factual, observed data.\n"
            "9. Your output should be comprehensive, logically structured, and directly actionable for a trading team.\n\n"
            f"CURRENT DATE: {current_date}\n"
            f"COMPANY OF INTEREST: {company_name} ({ticker})\n"
            "AVAILABLE TOOLS: {tool_names}\n"
        )

        # --- Prompt definition ---
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a compliant, non-hallucinating financial analysis agent.\n"
                    "You collaborate with other assistants using verified financial data only.\n"
                    "Use the provided tools to extract data and synthesize an analytical report.\n"
                    "If a FINAL TRANSACTION PROPOSAL (**BUY**, **HOLD**, or **SELL**) is justified, "
                    "prefix it as: FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**.\n\n"
                    "{system_message}"
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
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
