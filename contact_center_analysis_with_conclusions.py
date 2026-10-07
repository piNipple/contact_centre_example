"""
АНАЛИЗ ЭФФЕКТИВНОСТИ КОНТАКТ-ЦЕНТРА


Стек: Python, pandas, matplotlib.
Задача:
1. Проверить качество данных.
2. Рассчитать основные KPI.
3. Сравнить эффективность операторов, регионов и типов обращений.
4. Найти потенциальные зоны для дальнейшего исследования.
5. Сформировать аналитический вывод и рекомендации.

"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import textwrap


# 1. Загрузка и первичная проверка данных
df = pd.read_csv("contact_center_sample_data.csv")
df["date"] = pd.to_datetime(df["date"])

print("1. ПЕРВИЧНЫЙ АНАЛИЗ ДАННЫХ")
print(f"Количество обращений: {len(df):,}")
print(f"Период: {df['date'].min().date()} — {df['date'].max().date()}")
print(f"Количество операторов: {df['agent_id'].nunique()}")
print(f"Количество регионов: {df['region'].nunique()}")
print(f"Пропусков: {df.isna().sum().sum()}")
print(f"Дубликатов: {df.duplicated().sum()}")


# 2. Основные KPI
total_contacts = len(df)
avg_call_duration = df["call_duration_min"].mean()
avg_wait_time = df["wait_time_min"].mean()
resolution_rate = df["resolved"].mean() * 100
sales = df["sale"].sum()
conversion = df["sale"].mean() * 100
avg_rating = df["customer_rating"].mean()

print("2. ОСНОВНЫЕ KPI")


print(f"Количество обращений:       {total_contacts:,}")
print(f"Среднее время разговора:    {avg_call_duration:.2f} мин.")
print(f"Среднее время ожидания:     {avg_wait_time:.2f} мин.")
print(f"Доля решённых обращений:    {resolution_rate:.2f}%")
print(f"Количество продаж:          {sales}")
print(f"Конверсия в продажу:        {conversion:.2f}%")
print(f"Средняя оценка клиента:     {avg_rating:.2f} / 5")


# 3. Анализ по регионам
region_report = (
    df.groupby("region")
      .agg(
          contacts=("agent_id", "size"),
          avg_wait=("wait_time_min", "mean"),
          avg_duration=("call_duration_min", "mean"),
          resolution_rate=("resolved", "mean"),
          sales=("sale", "sum"),
          conversion=("sale", "mean"),
          avg_rating=("customer_rating", "mean"),
      )
      .reset_index()
)

region_report["resolution_rate"] *= 100
region_report["conversion"] *= 100

region_report = region_report.sort_values("conversion", ascending=False)

print("3. АНАЛИЗ ПО РЕГИОНАМ")

print(region_report.round(2).to_string(index=False))


# 4. Анализ по типу обращения

issue_report = (
    df.groupby("issue_type")
      .agg(
          contacts=("agent_id", "size"),
          avg_duration=("call_duration_min", "mean"),
          sales=("sale", "sum"),
          conversion=("sale", "mean"),
          resolution_rate=("resolved", "mean"),
      )
      .reset_index()
)

issue_report["conversion"] *= 100
issue_report["resolution_rate"] *= 100
issue_report = issue_report.sort_values("conversion", ascending=False)

print("4. АНАЛИЗ ПО ТИПАМ ОБРАЩЕНИЙ")
print(issue_report.round(2).to_string(index=False))


# 5. Анализ операторов

agent_report = (
    df.groupby("agent_id")
      .agg(
          contacts=("agent_id", "size"),
          avg_wait=("wait_time_min", "mean"),
          avg_duration=("call_duration_min", "mean"),
          sales=("sale", "sum"),
          conversion=("sale", "mean"),
          avg_rating=("customer_rating", "mean"),
      )
      .reset_index()
)

agent_report["conversion"] *= 100
agent_report = agent_report.sort_values("sales", ascending=False)

# Рейтинг по продажам и по конверсии
top_by_sales = agent_report.nlargest(5, "sales")
top_by_conversion = agent_report.nlargest(5, "conversion")

print("5. ЛУЧШИЕ ОПЕРАТОРЫ")
print("\nТоп-5 по абсолютному числу продаж:")
print(
    top_by_sales[
        ["agent_id", "contacts", "sales", "conversion", "avg_rating"]
    ].round(2).to_string(index=False)
)

print("\nТоп-5 по конверсии (минимум 30 обращений):")
top_by_conversion_30 = (
    agent_report[agent_report["contacts"] >= 30]
    .nlargest(5, "conversion")
)

print(
    top_by_conversion_30[
        ["agent_id", "contacts", "sales", "conversion", "avg_rating"]
    ].round(2).to_string(index=False)
)

# 6. Динамика по дням

daily_report = (
    df.groupby("date")
      .agg(
          contacts=("agent_id", "size"),
          sales=("sale", "sum"),
          conversion=("sale", "mean"),
          avg_wait=("wait_time_min", "mean"),
      )
      .reset_index()
)

daily_report["conversion"] *= 100

best_day = daily_report.loc[daily_report["conversion"].idxmax()]
worst_day = daily_report.loc[daily_report["conversion"].idxmin()]

print("6. ДИНАМИКА ПО ДНЯМ")
print(
    f"Лучший день по конверсии: {best_day['date'].date()} "
    f"({best_day['conversion']:.2f}%)"
)
print(
    f"Худший день по конверсии: {worst_day['date'].date()} "
    f"({worst_day['conversion']:.2f}%)"
)

# 7. Автоматический аналитический вывод

best_region = region_report.loc[region_report["conversion"].idxmax()]
worst_wait_region = region_report.loc[region_report["avg_wait"].idxmax()]
worst_resolution_region = region_report.loc[
    region_report["resolution_rate"].idxmin()
]

best_issue = issue_report.loc[issue_report["conversion"].idxmax()]
worst_issue = issue_report.loc[issue_report["conversion"].idxmin()]

# Для сравнения операторов используем минимум 30 обращений,
# чтобы не считать случайный высокий результат на маленькой выборке.
qualified_agents = agent_report[agent_report["contacts"] >= 30]

best_agent = qualified_agents.loc[qualified_agents["conversion"].idxmax()]
median_agent_conversion = qualified_agents["conversion"].median()

print("7. АНАЛИТИЧЕСКИЙ ВЫВОД")
conclusions = [
    (
        f"1. За анализируемый период обработано {total_contacts:,} обращений. "
        f"Среднее время разговора составило {avg_call_duration:.2f} мин., "
        f"а среднее ожидание — {avg_wait_time:.2f} мин."
    ),
    (
        f"2. Общая конверсия обращений в продажу составила {conversion:.2f}%, "
        f"доля решённых обращений — {resolution_rate:.2f}%, "
        f"средняя оценка клиентов — {avg_rating:.2f} из 5."
    ),
    (
        f"3. Лучший регион по конверсии — {best_region['region']}: "
        f"{best_region['conversion']:.2f}%. "
        f"Это направление можно использовать как объект для изучения лучших практик."
    ),
    (
        f"4. Наибольшее среднее время ожидания наблюдается в регионе "
        f"{worst_wait_region['region']} — {worst_wait_region['avg_wait']:.2f} мин. "
        f"Имеет смысл отдельно проверить нагрузку на операторов и распределение обращений."
    ),
    (
        f"5. Минимальная доля решённых обращений наблюдается в регионе "
        f"{worst_resolution_region['region']} — "
        f"{worst_resolution_region['resolution_rate']:.2f}%. "
        f"Стоит дополнительно исследовать причины незакрытых обращений."
    ),
    (
        f"6. Наиболее высокая конверсия наблюдается для типа обращения "
        f"«{best_issue['issue_type']}» — {best_issue['conversion']:.2f}%, "
        f"а самая низкая — для «{worst_issue['issue_type']}» "
        f"({worst_issue['conversion']:.2f}%). "
        f"Следующий шаг — проверить, насколько различие связано с составом клиентов "
        f"и спецификой обращений."
    ),
    (
        f"7. При оценке операторов важно учитывать не только количество продаж, "
        f"но и конверсию. Среди операторов с минимум 30 обращениями лучший результат "
        f"по конверсии показывает {best_agent['agent_id']} — "
        f"{best_agent['conversion']:.2f}% при {int(best_agent['contacts'])} обращениях. "
        f"Медианная конверсия в этой группе — {median_agent_conversion:.2f}%."
    ),
]

for conclusion in conclusions:
    print(textwrap.fill(conclusion, width=100))
    print()

# 8. Рекомендации
print("8. РЕКОМЕНДАЦИИ ПО ДАЛЬНЕЙШЕМУ АНАЛИЗУ")
recommendations = [
    "Проверить загрузку операторов по регионам и часам, особенно там, где выше время ожидания.",
    "Сравнить показатели новых и опытных операторов и изучить практики операторов с высокой конверсией.",
    "Разделить клиентов на сегменты и проверить, сохраняется ли разница в конверсии после сегментации.",
    "Проанализировать динамику KPI по дням и выявить возможные аномалии.",
    "Для продуктовых решений проверить статистическую значимость различий, прежде чем принимать решение.",
]

for i, recommendation in enumerate(recommendations, 1):
    print(f"{i}. {recommendation}")
# 9. Визуализации
fig, ax = plt.subplots(figsize=(10, 5))
region_report.sort_values("conversion").plot(
    x="region",
    y="conversion",
    kind="barh",
    ax=ax,
    legend=False,
)
ax.set_title("Конверсия в продажу по регионам")
ax.set_xlabel("Конверсия, %")
ax.set_ylabel("Регион")
plt.tight_layout()
plt.savefig('conversion_by_region.png', dpi=150, bbox_inches='tight')
plt.close()


fig, ax = plt.subplots(figsize=(10, 5))
issue_report.sort_values("conversion").plot(
    x="issue_type",
    y="conversion",
    kind="barh",
    ax=ax,
    legend=False,
)
ax.set_title("Конверсия в продажу по типам обращений")
ax.set_xlabel("Конверсия, %")
ax.set_ylabel("Тип обращения")
plt.tight_layout()
plt.savefig('conversion_by_issue_type.png', dpi=150, bbox_inches='tight')
plt.close()


fig, ax = plt.subplots(figsize=(11, 5))
daily_report.plot(
    x="date",
    y="contacts",
    kind="line",
    marker="o",
    ax=ax,
    legend=False,
)
ax.set_title("Количество обращений по дням")
ax.set_xlabel("Дата")
ax.set_ylabel("Количество обращений")
plt.tight_layout()
plt.savefig('contacts_by_day.png', dpi=150, bbox_inches='tight')
plt.close()
