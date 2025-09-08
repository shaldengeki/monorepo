import { gql } from '@apollo/client/core';
import { useMutation } from '@apollo/client/react';

export const FITBIT_AUTH_MUTATION = gql`
    mutation AuthWithFitbit {
        authWithFitbit {
            url
        }
    }
`;

const AuthView = () => {
    const [startFitbitAuth, { data, loading, error }] = useMutation(FITBIT_AUTH_MUTATION);

    if (loading) return <p>Loading...</p>;
    else if (error) return <p>Error: {error.message}</p>;
    else if (data === undefined) {
        startFitbitAuth();
    } else {
        window.location.replace(data.authWithFitbit.url);
    }
}

export default AuthView;
