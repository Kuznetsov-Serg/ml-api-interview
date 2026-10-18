# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
# ---

# %% [raw]
# # notebook_ml.ipynb
# # Вариант 3: LLM/текстовая модель со streaming
# # Что оптимизировать:
# # - Lazy loading модели (один раз при старте)
# # - Batching запросов
# # - SSE для streaming ответов
# # - Кэширование результатов в Redis
# #
# from transformers import pipeline
#
# # ПЛОХО: модель загружается при каждом вызове
# def classify_text(text):
#     classifier = pipeline('sentiment-analysis', model='distilbert-base-uncased')
#     result = classifier(text)
#     return result
#
# # ПЛОХО: обработка по одному тексту
# texts = pd.read_csv('reviews.csv')['text'].tolist()
# results = []
# for text in texts:
#     results.append(classify_text(text))
