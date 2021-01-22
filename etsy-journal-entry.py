#!/usr/bin/python3

import csv, sys, getopt

order_lines = 0
statement_lines = 0
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
output = ''

def main(argv):
    orders_file_path = ''
    statement_file_path = ''
    output_file = 'journal-entry-output.txt'
    home_state = "AZ"
    global order_lines
    global statement_lines
    global output
    global deposits
    global payments

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

    print(format_output(output))
    send_output_to_file(output, output_file)
    f = open('journal-entry-output.txt', 'w')
    f.write(output)
    f.close


def process_orders_file(file_path, home_state):
    with open(file_path, mode='r') as csv_file:
        order_lines = 0
        col_shipping = "Shipping"
        col_tax = "Sales Tax"
        col_state = "Ship State"
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:

            if order_lines == 0:
                pass

            if row[col_state] == home_state:
                credits['sales_tax_payable'] += float(row[col_tax])

            credits['shipping_income'] += float(row[col_shipping])
            order_lines += 1
    return order_lines

def process_statement_file(file_path):
    with open(file_path, mode='r') as csv_file:
        output = ""
        statement_lines = 0
        global deposits
        global payments
        col_type = 'Type'
        col_amount = 'Amount'
        col_fees_taxes = 'Fees & Taxes'
        col_net = 'Net'
        gross_sales_income = 0.00
        refund_processing_fees = 0.00
        csv_reader = csv.DictReader(csv_file)

        output += '\n'
        output += '\nPayments and Deposits'
        output += '\n========================================'

        for row in csv_reader:
            if row[col_net] != '--':
                debits['etsy_bank'] += float(row[col_net].replace('$', ''))

            if row[col_type] == 'Listing':
                debits['listing_fees'] += float(row[col_net].replace('$', ''))
            elif row[col_type] == 'Marketing':
                debits['marketing_fees'] += float(row[col_net].replace('$', ''))
            elif row[col_type] == 'Shipping Label':
                debits['shipping_fees'] += float(row[col_net].replace('$', ''))
            elif row[col_type] == 'Transaction':
                debits['transaction_fees'] += float(row[col_net].replace('$', ''))
            elif row[col_type] == 'Subscription':
                debits['subscription_fees'] += float(row[col_net].replace('$', ''))
            elif row[col_type] == 'Refund':
                debits['refunds'] += float(row[col_net].replace('$', '')) - float(row[col_fees_taxes].replace('$', ''))
                refund_processing_fees += float(row[col_fees_taxes].replace('$', ''))
            elif row[col_type] == 'Sale':
                debits['processing_fees'] += float(row[col_fees_taxes].replace('$', ''))
                gross_sales_income += float(row[col_net].replace('$', '')) - float(row[col_fees_taxes].replace('$', ''))
            elif row[col_type] == 'Deposit':
                amount = float(row['Title'].split(' ')[0].replace('$', ''))
                output += f'\nDeposit from Etsy: {amount:.2f}'
                deposits += amount
            elif row[col_type] == 'Payment':
                amount = float(row[col_net].split(' ')[0].replace('$', ''))
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
    output += '\n'
    output += '\n\tCredits'
    output += '\n\t========================================'
    output += f'\n\tSales Income: {credits["sales_income"]:.2f}'
    output += f'\n\tShipping Income: {credits["shipping_income"]:.2f}'
    output += f'\n\tSales Tax Payable: {credits["sales_tax_payable"]:.2f}'
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