import React from 'react';
import ExampleComponent from '../components/ExampleComponent';
import NavBar from '../../../../../react_library/NavBar';
import PageContainer from '../../../../../react_library/PageContainer';

type ExampleViewParams = {
    logo?: any,
}

const ExampleView = (props: ExampleViewParams) => {
    return (
        <PageContainer navbar={<NavBar logo={props.logo} title="Tic-Tac-Toe"/>}>
            <p>Page Container</p>
            <ExampleComponent />
        </PageContainer>
    )
}

export default ExampleView;
