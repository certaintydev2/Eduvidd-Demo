import json

from slack_notifier.main import handler

if __name__ == '__main__':
    # Signup
    # sqs_stuff = dict({
    #     "id": ["712441715"],
    #     "event": ["signup_success"],
    #     "payload[subscription][customer][email]": ["hannah@horvath.com"],
    #     "payload[subscription][customer][first_name]": ["Hannah"],
    #     "payload[subscription][customer][last_name]": ["Horvath"],
    #     "payload[subscription][customer][id]": ["34501447"],
    #     "payload[subscription][id]": ["33421031"],
    #     "payload[subscription][previous_state]": ["inactive"],
    #     "payload[subscription][state]": ["active"],
    #     "payload[site][subdomain]": ["professional-association-cc-dev"]
    # })

    # Subscription
    # sqs_stuff = dict({
    #     'id': '727243283',
    #     'event': ['subscription_state_change'],
    #     'payload[subscription][id]': ['28268158'],
    #     'payload[subscription][state]': ['active'],
    #     'payload[subscription][activated_at]': ['2019-05-17 10:00:00 -0400'],
    #     'payload[subscription][created_at]': ['2019-08-01 12:10:09 -0400'],
    #     'payload[subscription][updated_at]': ['2020-06-19 11:22:03 -0400'],
    #     'payload[subscription][balance_in_cents]': ['0'],
    #     'payload[subscription][current_period_ends_at]': ['2020-06-19 22:00:00 -0400'],
    #     'payload[subscription][next_assessment_at]': ['2020-06-19 11:07:52 -0400'],
    #     'payload[subscription][payment_collection_method]': ['automatic'],
    #     'payload[subscription][current_period_started_at]': ['2020-06-05 22:00:00 -0400'],
    #     'payload[subscription][previous_state]': ['past_due'],
    #     'payload[subscription][signup_payment_id]': ['0'],
    #     'payload[subscription][signup_revenue]': ['0.00'],
    #     'payload[subscription][total_revenue_in_cents]': ['36823'],
    #     'payload[subscription][product_price_in_cents]': ['1455'],
    #     'payload[subscription][product_version_number]': ['1'],
    #     'payload[subscription][payment_type]': ['bank_account'],
    #     'payload[subscription][referral_code]': ['xqd7vq'],
    #     'payload[subscription][product_price_point_id]': ['543664'],
    #     'payload[subscription][credit_balance_in_cents]': ['0'],
    #     'payload[subscription][prepayment_balance_in_cents]': ['0'],
    #     'payload[subscription][currency]': ['AUD'],
    #     'payload[subscription][customer][id]': ['29169569'],
    #     'payload[subscription][customer][first_name]': ['Amy'],
    #     'payload[subscription][customer][last_name]': ['Aberdein'],
    #     'payload[subscription][customer][email]': ['Amy_aberdein@hotmail.com'],
    #     'payload[subscription][customer][created_at]': ['2019-07-31 11:17:49 -0400'],
    #     'payload[subscription][customer][updated_at]': ['2019-10-29 23:26:19 -0400'],
    #     'payload[subscription][customer][address]': ['101 Ekibin Rd'],
    #     'payload[subscription][customer][address_2]': ['U1'],
    #     'payload[subscription][customer][city]': ['Annerley'],
    #     'payload[subscription][customer][state]': ['AU-QLD'],
    #     'payload[subscription][customer][zip]': ['4170'],
    #     'payload[subscription][customer][country]': ['AU'],
    #     'payload[subscription][customer][phone]': ['0475 625 005'],
    #     'payload[subscription][customer][verified]': ['false'],
    #     'payload[subscription][customer][portal_customer_created_at]': ['2019-10-29 23:26:19 -0400'],
    #     'payload[subscription][customer][tax_exempt]': ['false'],
    #     'payload[subscription][product][id]': ['4883106'],
    #     'payload[subscription][product][name]': [
    #         'Full-time Nurse/Midwife/Affiliate (Fortnightly) ABN 86 313 257 505'
    #     ],
    #     'payload[subscription][product][handle]': ['ftnfgc'],
    #     'payload[subscription][product][description]': [
    #         'Working over 48 hours per fortnight. (Billed fortnightly).'
    #     ],
    #     'payload[subscription][product][request_credit_card]': ['true'],
    #     'payload[subscription][product][expiration_interval_unit]': ['never'],
    #     'payload[subscription][product][created_at]': ['2019-05-07 13:58:26 -0400'],
    #     'payload[subscription][product][updated_at]': ['2020-06-15 18:54:56 -0400'],
    #     'payload[subscription][product][price_in_cents]': ['1455'],
    #     'payload[subscription][product][interval]': ['14'],
    #     'payload[subscription][product][interval_unit]': ['day'],
    #     'payload[subscription][product][trial_interval_unit]': ['month'],
    #     'payload[subscription][product][require_credit_card]': ['true'],
    #     'payload[subscription][product][taxable]': ['true'],
    #     'payload[subscription][product][tax_code]': ['D0000000'],
    #     'payload[subscription][product][initial_charge_after_trial]': ['false'],
    #     'payload[subscription][product][version_number]': ['1'],
    #     'payload[subscription][product][default_product_price_point_id]': ['602699'],
    #     'payload[subscription][product][request_billing_address]': ['true'],
    #     'payload[subscription][product][require_billing_address]': ['true'],
    #     'payload[subscription][product][require_shipping_address]': ['false'],
    #     'payload[subscription][product][product_price_point_id]': ['543664'],
    #     'payload[subscription][product][product_price_point_name]': [
    #         'Full-time Nurse/Midwife/Affiliate (Fortnightly)  ex GST'
    #     ],
    #     'payload[subscription][product][product_price_point_handle]':
    #         ['uuid:a3563b40-531f-0137-92c4-0a7da89f880c'],
    #     'payload[subscription][product][product_family][id]': ['1260579'],
    #     'payload[subscription][product][product_family][name]': ['NPAQ Billing Plans (Go Cardless)'],
    #     'payload[subscription][product][product_family][handle]': ['npaq-billing-plans-go-cardless'],
    #     'payload[subscription][product][public_signup_pages][id]': ['407239'],
    #     'payload[subscription][product][public_signup_pages][return_url]':
    #         ['https://www.npaq.com.au/almost'],
    #     'payload[subscription][product][public_signup_pages][return_params]': [
    #         'eml={customer_reference}'
    #     ],
    #     'payload[subscription][product][public_signup_pages][url]':
    #         ['https://professional-association-dd.chargifypay.com/subscribe/dnmmv4nmmpbn/ftnfgc'],
    #     'payload[subscription][bank_account][id]': ['19940246'],
    #     'payload[subscription][bank_account][first_name]': ['AMY'],
    #     'payload[subscription][bank_account][last_name]': ['ABERDEIN'],
    #     'payload[subscription][bank_account][customer_id]': ['29169569'],
    #     'payload[subscription][bank_account][current_vault]': ['gocardless'],
    #     'payload[subscription][bank_account][vault_token]': ['MD000JJT0VCQCT'],
    #     'payload[subscription][bank_account][billing_country]': ['AU'],
    #     'payload[subscription][bank_account][customer_vault_token]': ['CU000JR8RSMDAK'],
    #     'payload[subscription][bank_account][bank_name]': [
    #         'ING Bank (Australia) Limited (trading as ING)'
    #     ],
    #     'payload[subscription][bank_account][masked_bank_account_number]': ['XXXXXX87'],
    #     'payload[subscription][bank_account][bank_account_type]': ['checking'],
    #     'payload[subscription][bank_account][bank_account_holder_type]': ['personal'],
    #     'payload[subscription][bank_account][payment_type]': ['bank_account'],
    #     'payload[subscription][bank_account][verified]': ['true'],
    #     'payload[site][id]': ['63455'],
    #     'payload[site][subdomain]': ['professional-association-dd'],
    #     'payload[event_id]': ['1109440228']
    # })

    # Component
    sqs_stuff = dict({
        'id': '727538253',
        'event': ['component_allocation_change'],
        'payload[site][id]': ['70817'],
        'payload[site][subdomain]': ['professional-association-dd-dev'],
        'payload[component][id]': ['985092'],
        'payload[component][kind]': ['on_off_component'],
        'payload[component][name]': ['CPD Monthly'],
        'payload[component][unit_name]': ['on/off'],
        'payload[subscription][id]': ['33464518'],
        'payload[subscription][name]': ['James Brown'],
        'payload[subscription][state]': ['active'],
        'payload[subscription][product][id]': ['5234206'],
        'payload[subscription][product][product_price_point_id]': ['933995'],
        'payload[subscription][product][product_price_point_handle]':
            ['uuid:1461c9d0-7dbe-0137-7df5-02b7af0a7112'],
        'payload[subscription][product][name]': [
            'Full-time Nurse/Midwife/Affiliate (Monthly) 190701'
        ],
        'payload[subscription][product][interval]': ['1'],
        'payload[subscription][product][interval_unit]': ['month'],
        'payload[product][id]': ['5234206'],
        'payload[product][name]': ['Full-time Nurse/Midwife/Affiliate (Monthly) ABN 86 313 257 505'],
        'payload[product][interval]': ['1'],
        'payload[product][interval_unit]': ['month'],
        'payload[allocation][id]': ['577070715'],
        'payload[allocation][proration_upgrade_scheme]': ['prorate-attempt-capture'],
        'payload[allocation][proration_downgrade_scheme]': ['no-prorate'],
        'payload[transaction_exchange_rate][actual_rate]': ['1'],
        'payload[transaction_exchange_rate][reporting_rate]': ['1'],
        'payload[previous_allocation]': ['0'],
        'payload[new_allocation]': ['1'],
        'payload[timestamp]': ['2020-06-20T02:05:37Z'],
        'payload[price_point_id]': ['867444'],
        'payload[event_id]': ['1109805593']
    })

    # GO1
    # Signup
    # sqs_stuff = dict(
    #     {
    #         'kind': 'new',
    #         'first_name': 'Hannah',
    #         'last_name': 'Horvath',
    #         'email': 'hannah@horvath.com',
    #     }
    # )
    # Sub + Comp
    # sqs_stuff = dict(
    #     {
    #         'kind': 'update',
    #         'email': 'hannah@horvath.com',
    #         'state': True,
    #     }
    # )

    the_event = dict(
        Records=[dict(body=json.dumps(sqs_stuff))],
    )
    the_context = None
    resp = handler(the_event, the_context)
