import React from 'react';
import PageContainer from '../components/PageContainer';
import ExampleComponent from '../components/ExampleComponent';

type ExampleViewParams = {
}

const ExampleView = () => {
    return (
        <PageContainer>
            <ExampleComponent>
                <p>Hello World!</p>
            </ExampleComponent>
        </PageContainer>
    )
}

export default ExampleView;
