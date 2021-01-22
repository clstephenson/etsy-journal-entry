#!/usr/bin/python3

import csv, sys, getopt

order_lines = 0
statement_lines = 0
home_state = "AZ"
deposits = 0.0
payments = 0.0
debits = {
    'listing_fees' : 0.00,
    'marketing_fees' : 0.00,
    'shipping_fees' : 0.00,
    'transaction_fees' : 0.00,
    'subscription_fees' : 0.00,
    'refunds' : 0.00,
    'processing_fees' : 0.00,
    'etsy_bank': 0.00
}
credits = {
    'sales_income' : 0.00,
    'shipping_income' : 0.00,
    'shipping_cost_credit' : 0.00,
    'sales_tax_payable' : 0.00
}
headings = {
    'shipping' : 'Shipping',
    'tax' : 'Sales Tax',
    'state' : 'Ship State',
    'type' : 'Type',
    'amount' : 'Amount',
    'fees' : 'Fees & Taxes',
    'net' : 'Net',
    'title' : 'Title'
}
credit_total = 0.00
debit_total = 0.00
output = ''

def main(argv):
    orders_file_path = ''
    statement_file_path = ''
    output_file = 'journal-entry-output.txt'
    global home_state
    global order_lines
    global statement_lines
    global output
    global deposits
    global payments
    global credit_total
    global debit_total

    try:
        opts, args = getopt.getopt(argv, "s:o:", ["statement=", "orders="])
        if len(opts) < 2:
            print('etsy-journal-entry.py -s <statement-file> -o <orders-file>')
            sys.exit()
    except getopt.GetoptError:
        print('etsy-journal-entry.py -s <statement-file> -o <orders-file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-s", "--statement"):
            statement_file_path = arg
        elif opt in ("-o", "--orders"):
            orders_file_path = arg

    order_lines = process_orders_file(orders_file_path, home_state)
    output, statement_lines = process_statement_file(statement_file_path)

    debit_total = sum(value for value in debits.values())
    credit_total = sum(value for value in credits.values())

    formatted_output = format_output(output)
    print(formatted_output)
    send_output_to_file(formatted_output, output_file)


def process_orders_file(file_path, home_state):
    with open(file_path, mode='r') as csv_file:
        order_lines = 0
        global headings

        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:

            if order_lines == 0:
                pass

            if row[headings['state']] == home_state:
                credits['sales_tax_payable'] += float(row[headings['tax']])

            credits['shipping_income'] += float(row[headings['shipping']])
            order_lines += 1
    return order_lines

def process_statement_file(file_path):
    with open(file_path, mode='r') as csv_file:
        output = ""
        statement_lines = 0
        global deposits
        global payments
        global headings
        gross_sales_income = 0.00
        refund_processing_fees = 0.00
        
        output += '\n'
        output += '\nPayments and Deposits'
        output += '\n========================================'

        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row[headings['net']] != '--':
                debits['etsy_bank'] += float(row[headings['net']].replace('$', ''))

            if row[headings['type']] == 'Listing':
                debits['listing_fees'] += abs(float(row[headings['net']].replace('$', '')))
            elif row[headings['type']] == 'Marketing':
                debits['marketing_fees'] += abs(float(row[headings['net']].replace('$', '')))
            elif row[headings['type']] == 'Shipping Label':
                debits['shipping_fees'] += abs(float(row[headings['net']].replace('$', '')))
            elif row[headings['type']] == 'Transaction':
                debits['transaction_fees'] += abs(float(row[headings['net']].replace('$', '')))
            elif row[headings['type']] == 'Subscription':
                debits['subscription_fees'] += abs(float(row[headings['net']].replace('$', '')))
            elif row[headings['type']] == 'Refund':
                debits['refunds'] += float(row[headings['net']].replace('$', '')) - float(row[headings['fees']].replace('$', ''))
                refund_processing_fees += float(row[headings['fees']].replace('$', ''))
            elif row[headings['type']] == 'Sale':
                debits['processing_fees'] += abs(float(row[headings['fees']].replace('$', '')))
                gross_sales_income += float(row[headings['net']].replace('$', '')) - float(row[headings['fees']].replace('$', ''))
            elif row[headings['type']] == 'Deposit':
                amount = float(row['Title'].split(' ')[0].replace('$', ''))
                output += f'\nDeposit from Etsy: {amount:.2f}'
                deposits += amount
            elif row[headings['type']] == 'Payment':
                amount = float(row[headings['net']].split(' ')[0].replace('$', ''))
                output += f'\nPayment to Etsy: {amount:.2f}'
                payments += amount
            
            statement_lines += 1

        # order processing fees is fees from sales plus refund processing fees
        debits['processing_fees'] += refund_processing_fees
        
        # sales income is net sales minus processing fees minus shipping and taxes from order
        credits['sales_income'] = gross_sales_income - credits['shipping_income'] - credits['sales_tax_payable']

        # subtract payments to etsy from etsy bank debit
        debits['etsy_bank'] -= payments

    return output, statement_lines

def format_output(output):
    global debit_total
    global credit_total
    output += '\n'
    output += f'\nTotal Deposits to Bank Account: ${deposits:.2f}'
    output += f'\nTotal Payments to Etsy: ${payments:.2f}'
    output += '\n'
    output += '\nDebits'
    output += '\n========================================'
    output += f'\nListing Fees: {debits["listing_fees"]:.2f}'
    output += f'\nMarketing Fees: {debits["marketing_fees"]:.2f}'
    output += f'\nShipping Fees: {debits["shipping_fees"]:.2f}'
    output += f'\nTransaction Fees: {debits["transaction_fees"]:.2f}'
    output += f'\nSubscription Fees: {debits["subscription_fees"]:.2f}'
    output += f'\nRefunds: {debits["refunds"]:.2f}'
    output += f'\nOrder Processing Fees: {debits["processing_fees"]:.2f}'
    output += f'\nEtsy Bank (Etsy Payable): {debits["etsy_bank"]:.2f}'
    output += '\n-----------------------------------------'
    output += f'\nTotal Debits = {debit_total:.2f}'
    output += '\n'
    output += '\n\tCredits'
    output += '\n\t========================================'
    output += f'\n\tSales Income: {credits["sales_income"]:.2f}'
    output += f'\n\tShipping Income: {credits["shipping_income"]:.2f}'
    output += f'\n\tSales Tax Payable: {credits["sales_tax_payable"]:.2f}'
    output += '\n\t-----------------------------------------'
    output += f'\n\tTotal Credits = {credit_total:.2f}'
    output += '\n'
    output += '\n'
    output += f'Processed {order_lines} order lines from.'
    output += f'\nProcessed {statement_lines} statement lines.'
    output += '\n'
    return output

def send_output_to_file(output, output_file):
    f = open(output_file, 'w')
    f.write(output)
    f.close


if __name__ == "__main__":
    main(sys.argv[1:])