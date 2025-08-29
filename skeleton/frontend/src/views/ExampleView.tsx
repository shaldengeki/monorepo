import React from 'react';
import ExampleComponent from '../components/ExampleComponent';
import PageContainer from '../../../../react_library/PageContainer';

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
