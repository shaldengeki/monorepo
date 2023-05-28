import React from 'react';
import fitbit from './fitbit.png';
import { Link } from 'react-router-dom';
import { useQuery, gql } from '@apollo/client';

export const FETCH_CURRENT_USER_QUERY = gql`
    query FetchCurrentUser {
          currentUser {
            fitbitUserId
            displayName
            createdAt
          }
      }
`;


type NavBarProps = {
    className?: string;
}

const NavBar = (props: NavBarProps) => {
    const { loading, error, data } = useQuery(
        FETCH_CURRENT_USER_QUERY,
    );

    return (
        <div className="leading-6 w-full sticky border-b border-b-slate-50 py-4 px-1 bg-blue-200 dark:bg-slate-900 dark:text-slate-400">
            <div className="relative flex items-center">
                {
                    loading && <p>Loading...</p>
                }
                {
                    error && <p>Error loading login state</p>
                }
                {
                    data && data.currentUser === null &&
                    <Link to={'/auth'} className="ml-auto">
                        <img className="h-5 inline" src={fitbit} alt="Fitbit app icon" />
                        <span>Sign in with Fitbit</span>
                    </Link>
                }
                {
                    data && data.currentUser && <p className="ml-auto">{data.currentUser.displayName}</p>
                }
            </div>
        </div>
    );
};

export default NavBar;
