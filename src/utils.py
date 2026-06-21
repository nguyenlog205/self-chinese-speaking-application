"""
Utility module for configuration management and logging.

This module provides:
- A configuration loader that merges YAML settings with environment variables.
- A logger factory with rotating file handlers and console output.

All functions are fully typed and documented.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from dotenv import load_dotenv


def load_config(config_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Load configuration from a YAML file and overlay environment variables.

    The function looks for a YAML file at the given path. If no path is provided,
    it defaults to `config/system.yml` relative to the project root (two levels
    above this module). Environment variables are loaded from `.env` if present,
    otherwise from `.env.example`. Variables prefixed with `TTS_` override the
    YAML settings using a flattened underscore notation, e.g. `TTS_SYSTEM_DEBUG`
    becomes `system.debug`.

    Args:
        config_path: Optional explicit path to the YAML configuration file.

    Returns:
        A dictionary containing the merged configuration.

    Raises:
        FileNotFoundError: If the specified YAML file does not exist.
        yaml.YAMLError: If the YAML file is malformed.
    """
    if config_path is None:
        base_dir = Path(__file__).resolve().parent.parent
        config_path = base_dir / "config" / "system.yml"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    # Load environment variables from .env or .env.example
    env_root = config_path.parent.parent
    env_file = env_root / ".env"
    if not env_file.exists():
        env_file = env_root / ".env.example"

    if env_file.exists():
        load_dotenv(dotenv_path=env_file)

    # Override config with environment variables having prefix "TTS_"
    for key, value in os.environ.items():
        if not key.startswith("TTS_"):
            continue
        # Remove prefix and convert to lowercase
        config_key = key[4:].lower()
        parts = config_key.split("_")
        target = config
        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]
        # Convert value to appropriate type (int, float, bool, or string)
        if value.isdigit():
            target[parts[-1]] = int(value)
        elif value.replace(".", "", 1).isdigit():
            target[parts[-1]] = float(value)
        elif value.lower() in ("true", "false"):
            target[parts[-1]] = value.lower() == "true"
        else:
            target[parts[-1]] = value

    return config


def create_logger(
    name: str = "tts_app",
    log_dir: Optional[Union[str, Path]] = None,
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    console_output: bool = True,
) -> logging.Logger:
    """
    Create a configured logger with both file and console handlers.

    The logger uses a rotating file handler to prevent unlimited disk usage.
    Log messages are formatted with timestamp, logger name, level, and message.

    Args:
        name: The name of the logger (also used as the log file name).
        log_dir: Directory where log files will be stored. Defaults to `logs/`
                 in the project root.
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        max_bytes: Maximum size in bytes for a single log file before rotation.
        backup_count: Number of rotated log files to keep.
        console_output: If True, also log to the console (stdout).

    Returns:
        A configured logging.Logger instance.

    Raises:
        ValueError: If the log_level string is invalid.
    """
    level = getattr(logging, log_level.upper(), None)
    if level is None:
        raise ValueError(f"Invalid log level: {log_level}")

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if the logger is already configured
    if logger.handlers:
        return logger

    # Determine log directory
    if log_dir is None:
        base_dir = Path(__file__).resolve().parent.parent
        log_dir = base_dir / "logs"
    else:
        log_dir = Path(log_dir)

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{name}.log"

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)  # Always log everything to file
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (optional)
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Console gets only INFO and above
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger