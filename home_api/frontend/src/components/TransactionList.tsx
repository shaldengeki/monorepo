import React from 'react';
import _ from 'lodash';
import { gql } from '@apollo/client/core';
import { useQuery, useMutation } from '@apollo/client/react/hooks';

import Table from './Table';

const GET_TRANSACTIONS = gql`
    query Transactions(
        $earliestDate: Int,
        $latestDate: Int,
        $minAmount: Int,
        $maxAmount: Int,
        $types: [String],
        $categories: [String],
        $accounts: [String]
    ) {
        transactions(
            earliestDate: $earliestDate,
            latestDate: $latestDate,
            minAmount: $minAmount,
            maxAmount: $maxAmount,
            types: $types,
            categories: $categories,
            accounts: $accounts
        ) {
            formattedDate
            description
            amount
            category
            type
            account
        }
    }
`;

const formatCurrency = (amt: number, type: string): string => {
    const dollarAmt = `$${amt / 100.0}`;
    return (type === 'debit') ? dollarAmt : '-' + dollarAmt;
}

type TransactionListProps = {
    earliestDate: number,
    latestDate: number,
    minAmount: number,
    maxAmount: number,
    types: string[],
    categories: string[],
    accounts: string[],
}

export type FormattedTransaction = {
    formattedDate: string,
    account: string,
    description: string,
    category: string,
    amount: string,
}

const TransactionList = ({earliestDate, latestDate, minAmount, maxAmount, types, categories, accounts}: TransactionListProps) => {
    const { data, loading, error } = useQuery(GET_TRANSACTIONS, {
        variables: {
            earliestDate,
            latestDate,
            minAmount,
            maxAmount,
            types,
            categories,
            accounts
        }
    });

    const loadingDisplay = <h1>Loading transactions...</h1>;
    const errorDisplay = <h1>Error loading transactions!</h1>;

    if (loading) return loadingDisplay;
    if (error) return errorDisplay;

    const formattedTransactions = _.map(data.transactions || [], (txn): FormattedTransaction => {
        return {
            formattedDate: txn.formattedDate,
            account: txn.account,
            description: txn.description,
            category: txn.category,
            amount: formatCurrency(txn.amount, txn.type),
        };
    });

    const cols = [
        'formattedDate',
        'account',
        'description',
        'category',
        'amount'
    ];
    return (
        <Table cols={cols} rows={formattedTransactions} key='transactions' />
    );
}

export default TransactionList;
