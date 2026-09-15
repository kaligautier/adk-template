"""Calculator service - Business logic for mathematical operations."""

import logging
from enum import Enum

logger = logging.getLogger(__name__)


class Operation(str, Enum):
    """Supported mathematical operations."""

    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


class CalculatorClient:
    """Calculator client for mathematical operations."""

    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b

    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        return a - b

    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b

    def divide(self, a: float, b: float) -> float:
        """
        Divide a by b.

        Args:
            a: Numerator
            b: Denominator

        Returns:
            Result of division

        Raises:
            ValueError: If b is zero
        """
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        return a / b

    def calculate(self, operation: Operation, a: float, b: float) -> dict:
        """
        Perform mathematical calculation.

        This is the core business logic method.

        Args:
            operation: Operation to perform (Operation enum)
            a: First number
            b: Second number

        Returns:
            dict: Calculation result with operation details

        Raises:
            ValueError: If operation fails
        """
        logger.debug(f"Calculating: {operation.value}({a}, {b})")

        # Map operations to methods
        operations = {
            Operation.ADD: self.add,
            Operation.SUBTRACT: self.subtract,
            Operation.MULTIPLY: self.multiply,
            Operation.DIVIDE: self.divide,
        }

        # Execute operation
        try:
            result = operations[operation](a, b)
        except ValueError as e:
            # Re-raise with operation context
            raise ValueError(f"Operation '{operation}' failed: {str(e)}") from e

        return {
            "operation": operation.value,
            "a": a,
            "b": b,
            "result": result,
        }


# Singleton instance for convenience
calculator_client = CalculatorClient()
