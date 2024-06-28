import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';
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

type TransactionChartProps = {
    earliestDate: number,
    latestDate: number,
    minAmount: number,
    maxAmount: number,
    types: string[],
    categories: string[],
    accounts: string[],

}

const TransactionChart = ({
    earliestDate,
    latestDate,
    minAmount,
    maxAmount,
    types,
    categories,
    accounts
}: TransactionChartProps) => {
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
