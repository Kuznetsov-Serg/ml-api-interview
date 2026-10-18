# scripts/benchmark.py
"""
Универсальный бенчмарк для сравнения двух реализаций.

# Базовый запуск
poetry run python scripts/benchmark.py \
    --old data/input_ml/notebook_ml_1.py \
    --new data/output_ml/notebook_ml_1.py \
    --function engineer_features \
    --data data/customers.csv

# С несколькими прогонами для стабильности
poetry run python scripts/benchmark.py \
    --old data/input_ml/notebook_ml_1.py \
    --new data/output_ml/notebook_ml_1.py \
    --function engineer_features \
    --data data/customers.csv \
    --runs 5
"""

import argparse
import importlib.util
import sys
import time
import tracemalloc
from pathlib import Path

import pandas as pd


def load_module_from_path(path: str, module_name: str):
    """Динамически импортирует модуль по пути к файлу."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"Не удалось загрузить модуль: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def run_benchmark(func, df, name: str) -> tuple[float, float]:
    """Замеряет время и пиковую память."""
    print(f"\n🚀 Запуск: {name}")
    tracemalloc.start()
    start_time = time.perf_counter()

    func(df)

    end_time = time.perf_counter()
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    exec_time = end_time - start_time
    peak_memory_mb = peak / (1024 * 1024)

    print(f"   ⏱ Время выполнения: {exec_time:.4f} сек")
    print(f"   💾 Пиковая память:  {peak_memory_mb:.2f} MB")
    return exec_time, peak_memory_mb


def parse_args():
    parser = argparse.ArgumentParser(description="Сравнение двух реализаций функции")
    parser.add_argument(
        "--old", required=True, help="Путь к файлу со старой реализацией"
    )
    parser.add_argument("--new", required=True, help="Путь к файлу с новой реализацией")
    parser.add_argument(
        "--function",
        required=True,
        help="Имя функции для бенчмарка (должна быть в обоих файлах)",
    )
    parser.add_argument("--data", required=True, help="Путь к CSV с тестовыми данными")
    parser.add_argument(
        "--runs",
        type=int,
        default=3,
        help="Количество прогонов для усреднения (по умолчанию 3)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print(f"📊 Загрузка данных из {args.data}...")
    df = pd.read_csv(args.data)
    print(f"   Загружено {len(df)} записей.\n" + "=" * 60)

    # Динамический импорт модулей
    old_module = load_module_from_path(args.old, "old_impl")
    new_module = load_module_from_path(args.new, "new_impl")

    # Проверяем, что функция существует в обоих модулях
    func_name = args.function
    if not hasattr(old_module, func_name):
        raise AttributeError(f"Функция '{func_name}' не найдена в {args.old}")
    if not hasattr(new_module, func_name):
        raise AttributeError(f"Функция '{func_name}' не найдена в {args.new}")

    old_func = getattr(old_module, func_name)
    new_func = getattr(new_module, func_name)

    # Несколько прогонов для стабильности
    old_times, old_mems = [], []
    new_times, new_mems = [], []

    for i in range(args.runs):
        print(f"\n--- Прогон {i + 1}/{args.runs} ---")
        t_old, m_old = run_benchmark(old_func, df, f"OLD ({Path(args.old).name})")
        t_new, m_new = run_benchmark(new_func, df, f"NEW ({Path(args.new).name})")
        old_times.append(t_old)
        old_mems.append(m_old)
        new_times.append(t_new)
        new_mems.append(m_new)

    # Усредняем (берем медиану, чтобы выбросы не влияли)
    old_time = sorted(old_times)[len(old_times) // 2]
    old_mem = sorted(old_mems)[len(old_mems) // 2]
    new_time = sorted(new_times)[len(new_times) // 2]
    new_mem = sorted(new_mems)[len(new_mems) // 2]

    # Валидация идентичности результатов
    print("\n🔍 Проверка идентичности выходных данных...")
    old_result = old_func(df.copy())
    new_result = new_func(df.copy())

    try:
        pd.testing.assert_frame_equal(old_result, new_result, check_dtype=False)
        print("   ✅ Результаты идентичны!")
    except AssertionError as e:
        print("   ⚠️  Результаты РАЗЛИЧАЮТСЯ:")
        print(f"   {e}")

    print("\n" + "=" * 60)
    print("🏆 ИТОГОВЫЙ РЕЗУЛЬТАТ (медиана):")
    print(f"   OLD: {old_time:.4f} сек, {old_mem:.2f} MB")
    print(f"   NEW: {new_time:.4f} сек, {new_mem:.2f} MB")
    print(f"   ⚡ Ускорение:      {old_time / new_time:.1f}x быстрее")
    print(f"   📉 Экономия памяти: {old_mem / new_mem:.1f}x меньше")
    print("=" * 60)


if __name__ == "__main__":
    main()
