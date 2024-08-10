import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';
import { Link, useParams } from 'react-router-dom';

import PageContainer from '../components/PageContainer';
import PageTitle from "../components/PageTitle";
import UserInfoBox from '../components/UserInfoBox';
import GameLogsTable from '../components/GameLogsTable';
import User from '../types/User';

export const USER_VIEW_QUERY = gql`
    query FetchUser($name: String!) {
        user(name: $name) {
            bgaId
            name
            avatar
            recentGameLogs {
                bgaTableId
                users {
                    name
                }
            }
            numGameLogs
        }
    }
`;



type UserViewParams = {
    name: string,
}

const UserView = () => {
    let { name } = useParams<UserViewParams>();
    const { loading, error, data } = useQuery(
        USER_VIEW_QUERY,
        {variables: {name}},
    );


    let innerContent = <p></p>;
    if (loading) innerContent = <p>Loading...</p>;
    else if (error) innerContent = <p>Error: {error.message}</p>;
    else {
        var user: User = data.user;
        innerContent = (
            <div>
                <PageTitle><Link to={`/user/${user.name}`} >User: {user.name}</Link></PageTitle>
                <div className={"py-2"}>
                    <UserInfoBox user={user} />
                </div>
                <div className={"py-2"}>
                    <h2 className={"text-xl"}>Recent game logs:</h2>
                    <GameLogsTable gameLogs={user.recentGameLogs} />
                </div>
            </div>
        );
    }

    return (
        <PageContainer>
            {innerContent}
        </PageContainer>
    )
}

export default UserView;
