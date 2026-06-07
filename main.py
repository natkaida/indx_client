#!/usr/bin/env python3
"""
INDX.MONEY Trading Client - Точка входа
"""

from gui import IndxGUI


def main():
    """Запуск приложения"""
    app = IndxGUI()
    app.run()


if __name__ == "__main__":
    main()