# qiskit-labs

Учебно-практический репозиторий по квантовым схемам, алгоритмам и QKD-направлению после завершения Coursera specialization *The Complete Quantum Computing Course for Beginners*.

## Цель

Показать практическое понимание Qiskit, базовых квантовых схем, алгоритмов и связи quantum computing с quantum security / QKD.

## Что реализовано

1. Single-qubit circuits and measurement
2. Bell state and entanglement
3. Quantum teleportation
4. Superdense coding
5. Deutsch–Jozsa algorithm
6. Bernstein–Vazirani algorithm
7. Grover search demo
8. Shor algorithm explained (factorization of 15)
9. BB84 QKD skeleton

Bell state показывает корреляцию между результатами измерения двух кубитов. Это важный строительный блок для квантовой информации, телепортации, superdense coding и entanglement-based QKD.

## Стек

Python, Qiskit, Qiskit Aer, NumPy, Matplotlib, Jupyter Notebook, pytest, pandas.

## Как запустить

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
pip install -e .
pytest -q
jupyter notebook
```

Откройте ноутбуки в `notebooks/` по порядку, начиная с `00_environment_check.ipynb`.

## Структура

```text
notebooks/   — лабораторные работы с пояснениями (RU)
src/         — переиспользуемые схемы и утилиты
tests/       — pytest
reports/     — краткие технические заметки
images/      — схемы и гистограммы
```

## Связь с QKD / Quantum Security

Этот репозиторий — переходный блок от quantum computing к quantum communications. Лаборатория `09_bb84_qkd_skeleton.ipynb` станет основой для отдельного проекта **bb84-qkd-simulator** (Eve, QBER, reconciliation, privacy amplification).

```text
Coursera specialization → Qiskit practice → BB84 skeleton → bb84-qkd-simulator → QKD + AES-GCM demo
```

## Сертификат специализации

<!-- TODO: вставьте URL вашего сертификата Coursera -->
[Сертификат специализации](https://example.com/your-certificate-link)

## Важно

Все материалы являются **учебными симуляциями** и не предназначены для production security.

## CI и разработка

- Установите dev-зависимости и pre-commit для автоматического удаления вывода ноутбуков и базовых проверок:

```bash
python -m pip install -r requirements-dev.txt
pre-commit install
nbstripout --install
```

- В репозитории включён GitHub Actions workflow `.github/workflows/ci.yml`, который запускает `pytest` на push/PR в ветку `main`.

- Для фиксации конкретных версий в своей среде используйте:

```bash
# после установки зависимостей
pip freeze > requirements.txt
```

## Ссылки
