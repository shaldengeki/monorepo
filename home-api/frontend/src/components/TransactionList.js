import React from 'react';
import { useQuery } from '@apollo/react-hooks';
import gql from "graphql-tag";
import _ from 'lodash';

import Table from './Table';

const GET_TRANSACTIONS = gql`
    query Transactions {
        transactions {
            date
            formattedDate
            description
            originalDescription
            amount
            type
            category
            account
        }
    }
`;

const TransactionList = () => {
    const cols = [
        'formattedDate',
        'description',
        'category',
        'amount'
    ];
    const { data, loading, error } = useQuery(GET_TRANSACTIONS);

    const loadingDisplay = <h1>Loading transactions...</h1>;
    const errorDisplay = <h1>Error loading transactions!</h1>;

    if (loading) return loadingDisplay;
    if (error) return errorDisplay;

    const transactions = _.map(data.transactions || [], (txn) => {
        return {
            formattedDate: txn.formattedDate,
            description: txn.description,
            category: txn.category,
            amount: `\$${txn.amount / 100.0}`
        };
    });

    return (
        <Table cols={cols} rows={transactions} />
    );
}

export default TransactionList;