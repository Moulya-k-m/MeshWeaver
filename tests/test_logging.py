
"""Tests for MeshWeaver logging."""

import logging
import unittest

from meshweaver.logging_config import setup_logging


class LoggingTests(unittest.TestCase):

    def test_logger_creation(self):
        logger = setup_logging()
        self.assertEqual(logger.name, "meshweaver")

    def test_logger_level(self):
        logger = setup_logging(logging.DEBUG)
        self.assertEqual(logger.level, logging.DEBUG)

    def test_handler_not_duplicated(self):
        logger = setup_logging()
        initial_count = len(logger.handlers)

        setup_logging()

        self.assertEqual(len(logger.handlers), initial_count)

    def test_broker_logger_hierarchy(self):
        logger = setup_logging(logging.INFO)
        broker_logger = logging.getLogger(
            "meshweaver.broker"
        )

        self.assertEqual(
            broker_logger.parent,
            logger,
        )
        self.assertTrue(
            broker_logger.isEnabledFor(logging.INFO)
        )


if __name__ == "__main__":
    unittest.main()
