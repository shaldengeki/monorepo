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

const renderTransaction = (txn) => {
    return (
        <tr>
            <td class="border px-4 py-2">{txn.formattedDate}</td>
            <td class="border px-4 py-2">{txn.description}</td>
            <td class="border px-4 py-2">{txn.category}</td>
            <td class="border px-4 py-2">${txn.amount / 100.0}</td>
        </tr>
    );
}

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

    return (
        <Table cols={cols} rows={data.transactions || []} renderRow={renderTransaction} />
    );
}

export default TransactionList;