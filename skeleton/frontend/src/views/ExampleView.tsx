import React from 'react';
import PageContainer from '../components/PageContainer';
import ExampleComponent from '../components/ExampleComponent';

type ExampleViewParams = {
}

const ExampleView = () => {
    return (
        <PageContainer>
            <p>Page Container</p>
            <ExampleComponent />
        </PageContainer>
    )
}

export default ExampleView;
