## usage:
```
etsy-journal-entry.py -s <statement-file> -o <orders-file>
```
*statement-file*: monthly statement CSV file downloaded from the Etsy store

*orders-file*: monthly orders CSV file downloaded from the Etsy store

## output:
A text file is created in the current working directory containing the debits and credits to be used for the monthly journal entry to account for Etsy income and expenses. The output will also be displayed to stdout if running in a terminal.

NOTE: the credit and debit categories are not all-inclusive. They only include information that is currently useful for my situation. The script would need to be updated to add other details.

### Sample:
```
Payments and Deposits
========================================
Payment to Etsy: 3.30

Total Deposits to Bank Account: $0.00
Total Payments to Etsy: $3.30

Debits
========================================
Listing Fees: 1.00
Marketing Fees: 0.00
Shipping Fees: 0.00
Transaction Fees: 1.51
Subscription Fees: 0.00
Refunds: 0.00
Order Processing Fees: 1.25
Etsy Bank (Etsy Payable): 26.37
-----------------------------------------
Total Debits = 30.13

	Credits
	========================================
	Sales Income: 30.13
	Shipping Income: 0.00
	Sales Tax Payable: 0.00
	-----------------------------------------
	Total Credits = 30.13

Processed 1 order lines from.
Processed 10 statement lines.
```