
# Ananya Kollipara
# 20397133
# Group 2

### 2. Project Implementation Status Report

| Function Name                 | Implementation Status | What is Missing                                  |

|-------------------------------|-----------------------|--------------------------------------------------|

| add_book_to_catalog           | Partial               | ISBN does not stop/restrict accepting special characters and letters within an input; Total Copies value does not handle numbers over integer limits well from user input by notifying the user that the 'Database error occurred while adding the book', should instead put a number cap; Total Copies value input box allows user to type decimal values, whole number with '.0', math operations  and 'e' |

| borrow_book_by_patron         | Partial               | get_book_by_id is not implemented; Pateron with valid ID (6-digit format) is able to borrow more than the max of 5 books, the program allows to borrow a max of 6 books before notifying the user with 'You have reached the maximum borrowing limit of 5 books.' in a UI prompt at the 7th request to borrow a book |

| return_book_by_patron         | Partial               | Functionality is currently under development still as given from the notice UI prompt. Unable to return the book when 'Process Return' button is clicked. |

| calculate_late_fee_for_book   | Partial               | Functionality is currently under development as it is still on TODO. Needs to calculate late fees for overdue books based on: Books due 14 days after borrowing, $0.50/day for first 7 days overdue; $1.00/day for each additional day after 7 days; Maximum cap of $15.00 per book; Returns JSON response with fee amount and days overdue.|

| search_books_in_catalog       | Partial               | Functionality is currently under development as it is still on TODO and is not implemented still as given from the notice UI prompt. Needs support provided for the provided search functionality: Title search: Partial matching, case-insensitive, not more that 100 characters, not less than equal to 0 characters; Author search: Partial matching, case-insensitive, not more that 100 characters, not less than equal to 0 characters; ISBN search: Exact matching, ISBN should take only exactly 13 numbers, should not take special characters or letters in the input; Return results in the same format as the main catalog; Needs to use API endpoint '/late_fee/<patron_id>/<int:book_id>'. |

| get_patron_status_report      | Partial               | Functionality is currently under development as it is still on TODO. Needs the system to display patron status for a particular patron that includes the following: Currently borrowed books with due dates; Total late fees owed; Number of books currently borrowed; Borrowing history which should contain book tile, author name, and ISBN value which should only be exactly 13 numbers, not take special characters or letters; no specific space or API endpoint to display the patron Status report |

### 3. Writing Unit Test
Note: uses python clearDB.py to reset the database

R1_test.py
| test_add_book_valid_input_all_fields | Test adding a book with valid input. |
| test_add_book_invalid_isbn_too_short | Test adding a book with ISBN too short. |
| test_add_book_invalid_duplicate_isbn | Test adding a book with an isbn value that also exists in the catalog |
| test_add_book_invalid_isbn_uses_special_characters | Test adding a book with ISBN containing special characters |
| test_add_book_invalid_isbn_uses_letters | Test adding a book with ISBN containing letters |


R2_test.py
|test_valid_book_id_positive | Test adding a book with a positive book ID is generated |
| test_available_copies_are_less_than_equal_to_total_copies_valid | Test adding a book with available copies less than or equal to total copies |
| test_valid_borrow_button_for_available_books | Test borrowing a book when there are available copies |
| test_invalid_borrow_button_for_unavailable_books | Test borrowing a book when there are no available copies |


R3_test.py
| test_valid_six_digit_card | Test accepting a valid six digit card number |
| test_invalid_six_digit_card_short_len | Test rejecting an invalid six digit card number that is less than 6 digits |
| test_invalid_book_borrowing_over_5_max_of_same_card | Test borrowing a book over 5 books max limit |
| test_valid_borrow_book_decreases_available_copies | Test borrowing a book decreases available copies |

R4_test.py
| test_valid_book_borrowed_by_patron_is_returned | Test returning a book that was borrowed by the patron |
| test_valid_is_book_in_patron_borrow_record | Test verifys that the book was borrowed by a patron and in their record |
| test_records_return_date_is_valid | Test that the return date is recorded when a book is returned |
| test_return_book_by_patron_accepts_parameters_valid | Test that return_book_by_patron accepts patron ID and book ID as parameters |


R5_test.py
| test_that_book_is_overdue_valid | Test verifies that a book is overdue |
| test_that_book_is_overdue_invalid | Test Case Summary |
| test_set_due_date_default_14_days_later | Test that when first borrowing a book, the due date is 14 days later |
| test_overdue_bill_cap | Test that the late fee does not exceed the maximum cap of $15.00 |


R6_test.py
| test_valid_search_isbn | Test to find book with exact match isbn |
| test_valid_search_title_partial | Test to find book with partial match title |
| test_valid_search_author_partial | Test to find book with partial match author |
| test_valid_search_no_results_author | Test to find book from unmatching author with no results |


R7_test.py
| total_late_fees_owed_exists | total late fees owed by a patron exists |
| test_stored_currently_borrowed_books_with_due_dates_valid | stored currently borrowed books with due dates is true |
| test_number_of_books_currently_borrowed | number of books currently borrowed |
| test_shows_borrowing_history | shows borrowing history/history stored|






