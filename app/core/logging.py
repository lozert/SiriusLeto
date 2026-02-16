import logging
from logging import Logger


def setup_logging(level: int = logging.INFO) -> None:
    """
    Базовая настройка логирования для приложения.
    Вызывается лениво при первом запросе логгера.
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


def get_logger(name: str) -> Logger:
    """
    Возвращает логгер с указанным именем.
    При первом вызове инициализирует базовую конфигурацию.
    """
    root = logging.getLogger()
    if not root.handlers:
        setup_logging()
    return logging.getLogger(name)

