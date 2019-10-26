import React from 'react';
import { useQuery } from '@apollo/react-hooks';
import gql from "graphql-tag";

const GET_TRANSACTIONS = gql`
    {
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
    const { data, loading, error } = useQuery(GET_TRANSACTIONS);
    const loadingDisplay = <h1>Loading transactions...</h1>;
    const errorDisplay = <h1>Error loading transactions!</h1>;

    if (loading) return loadingDisplay;
    if (error) return errorDisplay;

    return (
        <table class="table-auto">
            <thead>
                <tr>
                    <th class="px-4 py-2">Date</th>
                    <th class="px-4 py-2">Description</th>
                    <th class="px-4 py-2">Category</th>
                    <th class="px-4 py-2">Amount</th>
                </tr>
            </thead>
            <tbody>
                {data.transactions &&
                    data.transactions.map(txn => renderTransaction(txn))}
            </tbody>
        </table>
    );
}

export default TransactionList;