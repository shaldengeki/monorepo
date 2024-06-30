import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';
import { useParams } from 'react-router-dom';
import ExampleComponent from '../components/ExampleComponent';

export const EXAMPLE_QUERY = gql`
    query ExampleQuery($id: Int!) {
        foo {
            id
        }
    }
`;

type ExampleViewParams = {
    exampleId: string;
}

const ExampleView = () => {
    let { exampleId } = useParams<ExampleViewParams>();
    const id = parseInt(exampleId || "0", 10);

    const  {loading, error, data } = useQuery(
        EXAMPLE_QUERY,
        {variables: { id }},
    );
    return (
        <ExampleComponent />
    )
}

export default ExampleView;
