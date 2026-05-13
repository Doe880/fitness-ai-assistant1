from agents import Agent, Runner, function_tool

from vector_store import semantic_search


LAST_SOURCES: list[dict] = []


TRAINING_CATEGORIES = {
    "тренировки",
    "восстановление",
}

NUTRITION_CATEGORIES = {
    "питание",
    "спортпит",
}


def format_results_for_agent(results: list[dict]) -> str:
    if not results:
        return "В базе знаний не найдено достаточно релевантной информации."

    parts = []

    for item in results:
        metadata = item.get("metadata", {})

        title = item.get("title") or metadata.get("title", "Без названия")
        category = item.get("category") or metadata.get("category", "без категории")
        item_type = metadata.get("type", "")
        level = ", ".join(metadata.get("level", [])) if isinstance(metadata.get("level"), list) else metadata.get("level", "")
        equipment = ", ".join(metadata.get("equipment", [])) if isinstance(metadata.get("equipment"), list) else metadata.get("equipment", "")
        muscle_groups = ", ".join(metadata.get("muscle_groups", [])) if isinstance(metadata.get("muscle_groups"), list) else metadata.get("muscle_groups", "")

        parts.append(
            f"Источник ID: {item.get('id')}\n"
            f"Тема: {title}\n"
            f"Категория: {category}\n"
            f"Тип: {item_type}\n"
            f"Уровень: {level}\n"
            f"Оборудование: {equipment}\n"
            f"Группы мышц: {muscle_groups}\n"
            f"Релевантность: {item.get('score', 0):.3f}\n"
            f"{item.get('text', '')}"
        )

    return "\n\n---\n\n".join(parts)


def save_sources(results: list[dict]) -> None:
    global LAST_SOURCES

    LAST_SOURCES = [
        {
            "id": item.get("id"),
            "title": item.get("title", "Без названия"),
            "category": item.get("category", "без категории"),
            "score": round(item.get("score", 0), 3),
        }
        for item in results
    ]


def is_category(item: dict, allowed_categories: set[str]) -> bool:
    metadata = item.get("metadata", {})
    category = item.get("category") or metadata.get("category")

    return category in allowed_categories


@function_tool
def search_training_knowledge(query: str) -> str:
    global LAST_SOURCES

    results = semantic_search(query, limit=8)

    filtered = [
        item for item in results
        if item.get("score", 0) > 0.20
        and is_category(item, TRAINING_CATEGORIES)
    ]

    save_sources(filtered)

    return format_results_for_agent(filtered)


@function_tool
def search_nutrition_knowledge(query: str) -> str:
    global LAST_SOURCES

    results = semantic_search(query, limit=8)

    filtered = [
        item for item in results
        if item.get("score", 0) > 0.20
        and is_category(item, NUTRITION_CATEGORIES)
    ]

    save_sources(filtered)

    return format_results_for_agent(filtered)


@function_tool
def search_program_knowledge(query: str) -> str:
    """
    Ищет информацию для составления тренировочных программ:
    частота тренировок, новичок, всё тело, части тела, восстановление.
    """
    global LAST_SOURCES

    expanded_query = (
        query
        + " программа на неделю тренировка новичок всё тело частота тренировок "
        + "грудь спина ноги плечи руки пресс восстановление день отдыха легкая активность "
        + "дом зал оборудование уровень"
    )

    results = semantic_search(expanded_query, limit=10)

    filtered = [
        item for item in results
        if item.get("score", 0) > 0.18
        and is_category(item, TRAINING_CATEGORIES)
    ]

    save_sources(filtered)

    return format_results_for_agent(filtered)


training_agent = Agent(
    name="TrainingAgent",
    model="gpt-5.4-mini",
    instructions=(
        "Ты специалист по тренировкам. "
        "Отвечай на русском языке. "
        "Всегда используй search_training_knowledge. "
        "Отвечай только на основе найденной базы знаний. "
        "Не давай медицинские рекомендации. "
        "Если речь о боли, травмах или болезни — посоветуй обратиться к специалисту. "
        "Если в базе знаний нет информации, так и скажи. "
        "Формат: короткий вывод, затем 2–4 практических пункта."
    ),
    tools=[search_training_knowledge],
)


nutrition_agent = Agent(
    name="NutritionAgent",
    model="gpt-5.4-mini",
    instructions=(
        "Ты специалист по спортивному питанию. "
        "Отвечай на русском языке. "
        "Всегда используй search_nutrition_knowledge. "
        "Отвечай только на основе найденной базы знаний. "
        "Не назначай дозировки, лечение или медицинские схемы. "
        "Если речь о заболеваниях, лекарствах, беременности или хронических состояниях — "
        "посоветуй обратиться к врачу или квалифицированному специалисту. "
        "Если в базе знаний нет информации, так и скажи. "
        "Формат: короткий вывод, затем 2–4 практических пункта."
    ),
    tools=[search_nutrition_knowledge],
)


program_agent = Agent(
    name="ProgramAgent",
    model="gpt-5.4-mini",
    instructions=(
        "Ты специалист по составлению простых тренировочных программ. "
        "Отвечай на русском языке. "
        "Всегда используй search_program_knowledge перед составлением программы. "
        "Составляй программы только на основе базы знаний. "
        "Не используй сложные медицинские или реабилитационные рекомендации. "
        "Не назначай опасные нагрузки. "
        "Если пользователь новичок, предлагай 2–3 тренировки в неделю. "
        "Если пользователь просит программу на неделю, сделай план по дням. "
        "Обязательно добавляй дни отдыха или лёгкой активности. "
        "Если в базе знаний нет информации, так и скажи. "
        "Формат ответа:\n"
        "1. Краткое пояснение\n"
        "2. Программа по дням\n"
        "3. Важные правила безопасности и восстановления"
    ),
    tools=[search_program_knowledge],
)


main_agent = Agent(
    name="MainFitnessAgent",
    model="gpt-5.4-mini",
    instructions=(
        "Ты главный AI-ассистент сайта про фитнес. "
        "Определи тип запроса пользователя. "
        "Если пользователь просит готовую программу, план на неделю, расписание тренировок, "
        "план для новичка или тренировочный сплит — передай задачу ProgramAgent. "
        "Если вопрос про упражнения, мышцы, части тела, зал, домашние тренировки или восстановление — "
        "передай задачу TrainingAgent. "
        "Если вопрос про еду, белок, углеводы, протеин, креатин, калории или спортпит — "
        "передай задачу NutritionAgent. "
        "Отвечай на русском языке. "
        "Не выдумывай факты."
    ),
    handoffs=[training_agent, nutrition_agent, program_agent],
)


def build_prompt(question: str, history: list[dict] | None = None) -> str:
    history = history or []

    history_text = ""

    for item in history[-6:]:
        role = item.get("role", "user")
        content = item.get("content", "")

        if role == "user":
            history_text += f"Пользователь: {content}\n"
        elif role == "assistant":
            history_text += f"Ассистент: {content}\n"

    return (
        "История диалога:\n"
        f"{history_text}\n"
        "Новый вопрос пользователя:\n"
        f"{question}"
    )


async def ask_agent(
    question: str,
    history: list[dict] | None = None
) -> tuple[str, list[dict]]:
    global LAST_SOURCES

    LAST_SOURCES = []

    prompt = build_prompt(question, history)

    result = await Runner.run(main_agent, prompt)

    return result.final_output, LAST_SOURCES