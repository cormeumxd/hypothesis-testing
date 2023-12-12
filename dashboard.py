import pandas as pd
import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

np.random.seed(112)
st.set_option('deprecation.showPyplotGlobalUse', False)

alpha = 0.05

def load_data(file_path):
    data = pd.read_csv(file_path, quotechar="'", encoding="windows-1251")
    column_mapping = {'"Количество больничных дней': 'work_days', '""Возраст""': 'age', '""Пол"""': 'gender'}
    data = (
        data.rename(columns=column_mapping)
        .assign(
            work_days=lambda x: x['work_days'].str.replace('"', '').astype(int),
            gender=lambda x: x['gender'].str.replace('"', '')
        )
    )
    return data

def check_hypothesis_chi2(data, group_column, threshold):
    crosstab_return = pd.crosstab(group_column, data.work_days > threshold, margins=True)
    crosstab = pd.crosstab(group_column, data.work_days > threshold)
    stats, p_value, _, _ = chi2_contingency(crosstab)
    return stats, p_value, crosstab_return

def check_gender_dependency(data, work_days_threshold, threshold, alpha):
    st.header("Проверим наличие зависимостей")

    # Hypothesis 1
    st.markdown('''
        Прежде всего хочется проверить, есть ли связь между кол-вом пропусков по больничному и пола/возраста.
        Для этого создадим таблицу частот пропусков от пола/возраста. Сформулируем гипотезу $H_0$ - кол-во пропусков не зависит от пола.
        Проверим гипотезу критерием согласия Пирсона
    ''')

    st.subheader('Зависимость пропусков от пола')

    # Visualization of distributions
    plt.figure(figsize=(10, 6))
    sns.histplot(data=data, x='work_days', hue='gender', kde=True, bins=20)
    plt.title("Распределение пропусков по болезни между мужчинами и женщинами")
    st.pyplot()

    # Statistical test
    stats, p_value, crosstab = check_hypothesis_chi2(data, data.gender, threshold)
    display_results("gender", work_days_threshold, stats, p_value, crosstab, alpha)

def check_age_dependency(data, work_days_threshold, age_threshold, threshold, alpha):
    st.subheader('Зависимость пропусков от возраста')

    plt.figure(figsize=(10, 6))
    sns.histplot(data=data, x='work_days', hue=data['age'] > age_threshold, kde=True, bins=20)
    plt.title(f"Распределение пропусков по болезни между группами возраста (>{age_threshold} лет)")
    st.pyplot()

    data[f'age>{age_threshold}'] = data.age > age_threshold
    stats, p_value, crosstab = check_hypothesis_chi2(data, data[f'age>{age_threshold}'], threshold)
    display_results(f"age>{age_threshold}", work_days_threshold, stats, p_value, crosstab, alpha)

def display_results(column_name, work_days_threshold, stats, p_value, crosstab, alpha):
    st.write(f"Таблица частот для work_days > {work_days_threshold}:")
    st.write(crosstab)
    st.write(f'pvalue < {alpha}' if p_value < alpha else f'pvalue > {alpha}')
    st.write(f"Результат: {'' if p_value < alpha else 'Нет '}значимой разницы для уровня значимости {alpha}. "
             f"Количество пропусков {'зависит' if p_value < alpha else 'не зависит'} от {column_name}")
    st.write(f"Значение статистики: {stats:.2f}, p-значение: {p_value:.3f}")

def main():
    # Dashboard title
    st.title("Анализ пропусков по болезни")

    # Load data
    file_path = st.file_uploader("Загрузите файл CSV", type=["csv"])
    if file_path is not None:
        data = load_data(file_path)

        # Parameters
        age_threshold = st.slider("Выберите возрастной порог:", min_value=data.age.min(), max_value=data.age.max(), value=35)
        work_days_threshold = st.slider("Выберите порог по рабочим дням:", min_value=data.work_days.min(), max_value=data.work_days.max(), value=2)

        # Check hypotheses
        check_gender_dependency(data, work_days_threshold, work_days_threshold, alpha)
        check_age_dependency(data, work_days_threshold, age_threshold, work_days_threshold, alpha)

# Run the main function
if __name__ == "__main__":
    main()
