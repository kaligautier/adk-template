"""Unit tests for calculator service."""

import pytest

from app.services.calculator_service import CalculatorClient, Operation


class TestCalculatorClientAdd:
    """Tests for CalculatorClient.add method."""

    def should_return_sum_of_positive_numbers(self):
        """Test adding two positive numbers."""
        client = CalculatorClient()
        result = client.add(5, 3)
        assert result == 8

    def should_return_sum_of_negative_numbers(self):
        """Test adding two negative numbers."""
        client = CalculatorClient()
        result = client.add(-5, -3)
        assert result == -8

    def should_return_zero_when_adding_opposites(self):
        """Test adding opposite numbers."""
        client = CalculatorClient()
        result = client.add(5, -5)
        assert result == 0

    def should_handle_float_numbers(self):
        """Test adding float numbers."""
        client = CalculatorClient()
        result = client.add(2.5, 3.7)
        assert result == pytest.approx(6.2)


class TestCalculatorClientSubtract:
    """Tests for CalculatorClient.subtract method."""

    def should_return_difference_of_positive_numbers(self):
        """Test subtracting two positive numbers."""
        client = CalculatorClient()
        result = client.subtract(10, 3)
        assert result == 7

    def should_return_negative_when_second_larger(self):
        """Test subtracting larger number from smaller."""
        client = CalculatorClient()
        result = client.subtract(3, 10)
        assert result == -7

    def should_handle_negative_numbers(self):
        """Test subtracting negative numbers."""
        client = CalculatorClient()
        result = client.subtract(5, -3)
        assert result == 8


class TestCalculatorClientMultiply:
    """Tests for CalculatorClient.multiply method."""

    def should_return_product_of_positive_numbers(self):
        """Test multiplying two positive numbers."""
        client = CalculatorClient()
        result = client.multiply(5, 3)
        assert result == 15

    def should_return_zero_when_multiplying_by_zero(self):
        """Test multiplying by zero."""
        client = CalculatorClient()
        result = client.multiply(5, 0)
        assert result == 0

    def should_return_negative_when_multiplying_opposite_signs(self):
        """Test multiplying positive and negative numbers."""
        client = CalculatorClient()
        result = client.multiply(5, -3)
        assert result == -15

    def should_handle_float_numbers(self):
        """Test multiplying float numbers."""
        client = CalculatorClient()
        result = client.multiply(2.5, 4)
        assert result == pytest.approx(10.0)


class TestCalculatorClientDivide:
    """Tests for CalculatorClient.divide method."""

    def should_return_quotient_of_positive_numbers(self):
        """Test dividing two positive numbers."""
        client = CalculatorClient()
        result = client.divide(10, 2)
        assert result == 5

    def should_return_float_for_non_divisible_numbers(self):
        """Test division resulting in float."""
        client = CalculatorClient()
        result = client.divide(10, 3)
        assert result == pytest.approx(3.333333333)

    def should_raise_error_when_dividing_by_zero(self):
        """Test dividing by zero raises ValueError."""
        client = CalculatorClient()
        with pytest.raises(ValueError, match="Division by zero is not allowed"):
            client.divide(10, 0)

    def should_handle_negative_division(self):
        """Test dividing with negative numbers."""
        client = CalculatorClient()
        result = client.divide(-10, 2)
        assert result == -5


class TestCalculatorClientCalculate:
    """Tests for CalculatorClient.calculate method."""

    def should_perform_addition_operation(self):
        """Test calculate with ADD operation."""
        client = CalculatorClient()
        result = client.calculate(Operation.ADD, 5, 3)

        assert result["operation"] == "add"
        assert result["a"] == 5
        assert result["b"] == 3
        assert result["result"] == 8

    def should_perform_subtraction_operation(self):
        """Test calculate with SUBTRACT operation."""
        client = CalculatorClient()
        result = client.calculate(Operation.SUBTRACT, 10, 3)

        assert result["operation"] == "subtract"
        assert result["result"] == 7

    def should_perform_multiplication_operation(self):
        """Test calculate with MULTIPLY operation."""
        client = CalculatorClient()
        result = client.calculate(Operation.MULTIPLY, 5, 3)

        assert result["operation"] == "multiply"
        assert result["result"] == 15

    def should_perform_division_operation(self):
        """Test calculate with DIVIDE operation."""
        client = CalculatorClient()
        result = client.calculate(Operation.DIVIDE, 10, 2)

        assert result["operation"] == "divide"
        assert result["result"] == 5

    def should_raise_error_with_context_on_division_by_zero(self):
        """Test calculate wraps division by zero error with context."""
        client = CalculatorClient()
        with pytest.raises(ValueError, match="Operation 'Operation.DIVIDE' failed"):
            client.calculate(Operation.DIVIDE, 10, 0)

    def should_include_all_parameters_in_result(self):
        """Test calculate result contains all operation details."""
        client = CalculatorClient()
        result = client.calculate(Operation.ADD, 7.5, 2.5)

        assert "operation" in result
        assert "a" in result
        assert "b" in result
        assert "result" in result
        assert len(result) == 4


class TestOperation:
    """Tests for Operation enum."""

    def should_have_add_operation(self):
        """Test ADD operation exists and has correct value."""
        assert Operation.ADD.value == "add"

    def should_have_subtract_operation(self):
        """Test SUBTRACT operation exists and has correct value."""
        assert Operation.SUBTRACT.value == "subtract"

    def should_have_multiply_operation(self):
        """Test MULTIPLY operation exists and has correct value."""
        assert Operation.MULTIPLY.value == "multiply"

    def should_have_divide_operation(self):
        """Test DIVIDE operation exists and has correct value."""
        assert Operation.DIVIDE.value == "divide"

    def should_allow_string_conversion(self):
        """Test Operation can be created from string."""
        op = Operation("add")
        assert op == Operation.ADD
