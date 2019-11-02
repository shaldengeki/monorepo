import React from 'react';
import _ from 'lodash';
import { useQuery } from '@apollo/react-hooks';
import gql from "graphql-tag";

import Table from './Table';

const GET_TRANSACTIONS = gql`
    query Transactions {
        transactions {
            formattedDate
            description
            amount
            category
        }
    }
`;

const TransactionList = () => {
    const { data, loading, error } = useQuery(GET_TRANSACTIONS);

    const loadingDisplay = <h1>Loading transactions...</h1>;
    const errorDisplay = <h1>Error loading transactions!</h1>;

    if (loading) return loadingDisplay;
    if (error) return errorDisplay;

    const formattedTransactions = _.map(data.transactions || [], (txn) => {
        return {
            formattedDate: txn.formattedDate,
            description: txn.description,
            category: txn.category,
            amount: `$${txn.amount / 100.0}`
        };
    });

    const cols = [
        'formattedDate',
        'description',
        'category',
        'amount'
    ];
    return (
        <Table cols={cols} rows={formattedTransactions} key='transactions' />
    );
}

export default TransactionList;