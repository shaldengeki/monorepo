import React, { Fragment } from 'react';
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
        <p>{txn.formattedDate}: {txn.description} - {txn.category} (${txn.amount / 100.0})</p>
    )
}

const TransactionList = () => {
    const { data, loading, error } = useQuery(GET_TRANSACTIONS);
    const loadingDisplay = <h1>Loading transactions...</h1>;
    const errorDisplay = <h1>Error loading transactions!</h1>;

    if (loading) return loadingDisplay;
    if (error) return errorDisplay;

    return (
        <Fragment>
          {data.transactions &&
            data.transactions.map(txn => renderTransaction(txn))}
        </Fragment>
    );
}

export default TransactionList;