"""
Task 2.1: Stubbing and Mocking Tests for Payment Gateway Functions

This test module demonstrates comprehensive stubbing and mocking techniques for testing
the pay_late_fees() and refund_late_fee_payment() functions that depend on an external
PaymentGateway service.
"""

import pytest
from unittest.mock import Mock
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.library_service import (
    pay_late_fees, 
    refund_late_fee_payment,
    calculate_late_fee_for_book
)
from services.payment_service import PaymentGateway
from clearDB import clear_database

clear_database()

# pay_late_fees() Tests


def test_pay_late_fees_successful_payment(mocker):
    """Test successful payment"""
    mocker.patch(
        'services.library_service.calculate_late_fee_for_book',
        return_value={'fee_amount': 5.00, 'days_overdue': 3, 'status': 'Late fee calculated'}
    )
    mocker.patch(
        'services.library_service.get_book_by_id',
        return_value={'id': 1, 'title': 'Test Book', 'author': 'Author', 'isbn': '1234567890123', 'total_copies': 5, 'available_copies': 3}
    )
    
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_123456_1234567890", "Payment processed")
    
    success, message, _ = pay_late_fees("123456", 1, mock_gateway)
    
    assert success is True
    assert "Payment successful" in message
    mock_gateway.process_payment.assert_called_once()
    clear_database()


def test_pay_late_fees_payment_declined(mocker):
    """Test declined payment from gateway."""
    mocker.patch(
        'services.library_service.calculate_late_fee_for_book',
        return_value={'fee_amount': 10.00, 'days_overdue': 5, 'status': 'Late fee calculated'}
    )
    mocker.patch(
        'services.library_service.get_book_by_id',
        return_value={'id': 2, 'title': 'Book', 'author': 'Author', 'isbn': '9876543210987', 'total_copies': 2, 'available_copies': 1}
    )
    
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, "", "Insufficient funds")
    
    success, message, _ = pay_late_fees("234567", 2, mock_gateway)
    
    assert success is False
    mock_gateway.process_payment.assert_called_once()
    clear_database()


def test_pay_late_fees_invalid_patron_id_short(mocker):
    """Test short patron ID"""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message, _ = pay_late_fees("12345", 1, mock_gateway)
    
    assert success is False
    assert "Invalid patron ID" in message
    mock_gateway.process_payment.assert_not_called()
    clear_database()


def test_pay_late_fees_invalid_patron_id_long(mocker):
    """Test long patron ID"""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message, _ = pay_late_fees("1234567", 1, mock_gateway)
    
    assert success is False
    assert "Invalid patron ID" in message
    mock_gateway.process_payment.assert_not_called()
    clear_database()


def test_pay_late_fees_invalid_patron_id_not_num(mocker):
    """Test patron ID that has letters."""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message, _ = pay_late_fees("ABC123", 1, mock_gateway)
    
    assert success is False
    assert "Invalid patron ID" in message
    mock_gateway.process_payment.assert_not_called()
    clear_database()


def test_pay_late_fees_empty_patron_id(mocker):
    """Test empty patron ID."""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message, _ = pay_late_fees("", 1, mock_gateway)
    
    assert success is False
    mock_gateway.process_payment.assert_not_called()
    clear_database()


def test_pay_late_fees_none_patron_id(mocker):
    """Test None patron ID."""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message, _ = pay_late_fees(None, 1, mock_gateway)
    
    assert success is False
    mock_gateway.process_payment.assert_not_called()
    clear_database()


def test_pay_late_fees_zero_late_fees(mocker):
    """Test mock not called with no late fees."""
    mocker.patch(
        'services.library_service.calculate_late_fee_for_book',
        return_value={'fee_amount': 0.00, 'days_overdue': 0, 'status': 'No late fee'}
    )
    
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message, _ = pay_late_fees("123456", 1, mock_gateway)
    
    assert success is False
    assert "No late fees to pay" in message
    mock_gateway.process_payment.assert_not_called()
    clear_database()

def test_pay_late_fees_network_error(mocker):
    """Test exception handling when payment gateway encounters error."""
    mocker.patch(
        'services.library_service.calculate_late_fee_for_book',
        return_value={'fee_amount': 7.50, 'days_overdue': 4, 'status': 'Late fee calculated'}
    )
    mocker.patch(
        'services.library_service.get_book_by_id',
        return_value={'id': 3, 'title': 'Book', 'author': 'Author', 'isbn': '1111111111111', 'total_copies': 1, 'available_copies': 0}
    )
    
    mock_gateway = Mock(spec=PaymentGateway)

    success, message, _ = pay_late_fees("345678", 3, mock_gateway)
    assert success is False
    assert "Payment processing error" in message
    mock_gateway.process_payment.assert_called_once()
    clear_database()


# TEST: refund_late_fee_payment()

def test_refund_successful(mocker):
    """Test successful refund."""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund of $5.00 processed successfully")
    
    success, message = refund_late_fee_payment("txn_123456_1234567890", 5.00, mock_gateway)
    
    assert success is True
    assert "Refund" in message
    mock_gateway.refund_payment.assert_called_once_with("txn_123456_1234567890", 5.00)
    clear_database()


def test_refund_invalid_transaction_id_no_prefix(mocker):
    """Test of transaction ID withouttxn_"""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message = refund_late_fee_payment("iDid", 5.00, mock_gateway)
    
    assert success is False
    assert "Invalid transaction ID" in message
    mock_gateway.refund_payment.assert_not_called()
    clear_database()


def test_refund_invalid_transaction_id_empty(mocker):
    """Test of blank transaction ID."""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message = refund_late_fee_payment("", 5.00, mock_gateway)
    
    assert success is False
    assert "Invalid transaction ID" in message
    mock_gateway.refund_payment.assert_not_called()
    clear_database()


def test_refund_invalid_transaction_id_none(mocker):
    """Test of None transaction ID."""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message = refund_late_fee_payment(None, 5.00, mock_gateway)
    
    assert success is False
    assert "Invalid transaction ID" in message
    mock_gateway.refund_payment.assert_not_called()
    clear_database()


def test_refund_negative_amount(mocker):
    """Test of negative refund amount."""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message = refund_late_fee_payment("txn_123456_1234567890", -5.00, mock_gateway)
    
    assert success is False
    assert "greater than 0" in message
    mock_gateway.refund_payment.assert_not_called()
    clear_database()


def test_refund_zero_amount(mocker):
    """Test of zero refund amount."""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message = refund_late_fee_payment("txn_123456_1234567890", 0.00, mock_gateway)
    
    assert success is False
    assert "greater than 0" in message
    mock_gateway.refund_payment.assert_not_called()
    clear_database()


def test_refund_amount_exceeds_maximum(mocker):
    """Test refund amount exceeding $15.00 maximum."""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message = refund_late_fee_payment("txn_123456_1234567890", 15.01, mock_gateway)
    
    assert success is False
    assert "exceeds maximum" in message
    mock_gateway.refund_payment.assert_not_called()
    clear_database()

def test_refund_amount_at_maximum_boundary(mocker):
    """Test successful refund at exactly $15.00 maximum."""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund of $15.00 processed")
    
    success, message = refund_late_fee_payment("txn_123456_1234567890", 15.00, mock_gateway)
    
    assert success is True
    call_args = mock_gateway.refund_payment.call_args
    assert call_args[0][1] == 15.00
    clear_database()

def test_refund_gateway_exception(mocker):
    """Test exception handling when payment gateway encounters error during refund."""
    mock_gateway = Mock(spec=PaymentGateway)

    success, message = refund_late_fee_payment("txn_123456_1234567890", 5.00, mock_gateway)
    assert success is False
    assert "Refund processing error" in message 
    mock_gateway.refund_payment.assert_called_once_with("txn_123456_1234567890", 5.00)
    clear_database()

def test_refund_gateway_failure_message(mocker):
    """Test refund failure with specific gateway failure message."""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (False, "Gateway unavailable")

    success, message = refund_late_fee_payment("txn_123456_1234567890", 5.00, mock_gateway)

    assert success is False
    assert "Refund failed:" in message
    mock_gateway.refund_payment.assert_called_once_with("txn_123456_1234567890", 5.00)
    clear_database()