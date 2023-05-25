import React from 'react';
import { useMutation, gql } from '@apollo/client';
import PageContainer from '../components/PageContainer';

export const FITBIT_AUTH_MUTATION = gql`
    mutation AuthWithFitbit {
        authWithFitbit {
            url
        }
    }
`;

const AuthView = () => {
    const [startFitbitAuth, { data, loading, error, reset }] = useMutation(FITBIT_AUTH_MUTATION);

    let innerContent = <p></p>;
    if (loading) innerContent = <p>Loading...</p>;
    else if (error) innerContent = <p>Error: {error.message}</p>;
    else if (data === undefined) {
        startFitbitAuth();
    } else {
        window.location.replace(data.authWithFitbit.url);
    }
    return (
        <PageContainer>
            {innerContent}
        </PageContainer>
    )
}

export default AuthView;
