from agents import Agent, Runner, function_tool

from vector_store import semantic_search


@function_tool
def search_fitness_knowledge(query: str) -> str:
    results = semantic_search(query, limit=5)

    if not results:
        return "В базе знаний не найдено информации по этому запросу."

    filtered = [item for item in results if item["score"] > 0.20]

    if not filtered:
        return "В базе знаний не найдено достаточно релевантной информации."

    parts = []

    for item in filtered:
        parts.append(
            f"Фрагмент ID: {item['id']}\n"
            f"Релевантность: {item['score']:.3f}\n"
            f"{item['text']}"
        )

    return "\n\n---\n\n".join(parts)


fitness_agent = Agent(
    name="FitnessKnowledgeAgent",
    model="gpt-5.4-mini",
    instructions=(
        "Ты AI-ассистент учебного сайта про фитнес, тренировки и спортивное питание. "
        "Всегда отвечай на русском языке. "
        "Всегда используй инструмент search_fitness_knowledge для поиска информации. "
        "Отвечай только на основе найденных фрагментов из базы знаний. "
        "Не выдумывай факты, дозировки, медицинские рекомендации и противопоказания. "
        "Если в базе знаний нет информации, прямо скажи: 'В базе знаний нет информации по этому вопросу'. "
        "Не ставь диагнозы и не давай медицинские назначения. "
        "Если вопрос связан с болезнями, травмами, беременностью, лекарствами или хроническими состояниями, "
        "посоветуй обратиться к врачу или квалифицированному специалисту. "
        "Формат ответа: короткий ответ, затем 2–4 практических пункта."
    ),
    tools=[search_fitness_knowledge],
)


async def ask_agent(question: str) -> str:
    result = await Runner.run(fitness_agent, question)
    return result.final_output