import React from 'react';
import PageContainer from '../components/PageContainer';
import ExampleComponent from '../components/ExampleComponent';

type ExampleViewParams = {
    logo?: any,
}

const ExampleView = (props: ExampleViewParams) => {
    return (
        <PageContainer logo={props.logo}>
            <p>Page Container</p>
            <ExampleComponent />
        </PageContainer>
    )
}

export default ExampleView;
