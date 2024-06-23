import React from 'react';
import { useQuery } from '@apollo/react-hooks';
import gql from "graphql-tag";
import _ from 'lodash';
import createPlotlyComponent from 'react-plotlyjs';
import Plotly from 'plotly.js-basic-dist';

const PlotlyComponent = createPlotlyComponent(Plotly);

const GET_MONTHLY_SPEND = gql`
    query MonthlySpend(
        $earliestDate: Int,
        $latestDate: Int,
        $minAmount: Int,
        $maxAmount: Int,
        $types: [String],
        $categories: [String],
        $accounts: [String]
    ) {
        amountByMonth(
            earliestDate: $earliestDate,
            latestDate: $latestDate,
            minAmount: $minAmount,
            maxAmount: $maxAmount,
            types: $types,
            categories: $categories,
            accounts: $accounts
        ) {
            formattedMonth
            amount
        }
    }
`;

const TransactionChart = (props) => {
    const {
        earliestDate,
        latestDate,
        minAmount,
        maxAmount,
        types,
        categories,
        accounts
    } = props;

    const { data, loading, error } = useQuery(GET_MONTHLY_SPEND, {
        variables: {
            earliestDate,
            latestDate,
            minAmount,
            maxAmount,
            types,
            categories,
            accounts
        },
    });

    const loadingDisplay = <h1>Loading transactions...</h1>;
    const errorDisplay = <h1>Error loading transactions!</h1>;

    if (loading) return loadingDisplay;
    if (error) return errorDisplay;

    const graphData = [
        {
            x: _.map(data.amountByMonth, (a) => { return a.formattedMonth; }),
            y: _.map(data.amountByMonth, (a) => { return a.amount / 100.0; }),
            type: 'bar'
        }
    ];
    const layout = {

    };
    const config = {

    };
    return (
        <PlotlyComponent
            className="whatever"
            data={graphData}
            layout={layout}
            config={config}
        />
    );
}

export default TransactionChart;
