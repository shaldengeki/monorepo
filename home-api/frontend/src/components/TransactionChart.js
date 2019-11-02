import React from 'react';
import { useQuery } from '@apollo/react-hooks';
import gql from "graphql-tag";
import _ from 'lodash';
import createPlotlyComponent from 'react-plotlyjs';
import Plotly from 'plotly.js-basic-dist';

const PlotlyComponent = createPlotlyComponent(Plotly);

const GET_MONTHLY_SPEND = gql`
    query MonthlySpend {
        amountByMonth {
            formattedMonth
            amount
        }
    }
`;

const TransactionChart = () => {
    const { data, loading, error } = useQuery(GET_MONTHLY_SPEND);

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