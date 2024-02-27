import React from 'react';
import fitbit from './fitbit.png';
import logo192 from './logo192.png';
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
        <div className="sticky top-0 z-40 w-full backdrop-blur flex-none lg:border-b lg:border-slate-900/10 lg:dark:border-slate-50/[0.06] bg-white/95 supports-backdrop-blur:bg-white/60 dark:bg-transparent">
            <div className="max-w-screen-2xl mx-auto">
                <div className="py-4 mx-4 lg:mx-0 lg:px-8 relative flex items-center gap-2 dark:text-slate-400">
                    <img className="flex-none h-6 inline" src={logo192} alt="Fitbit app icon" />
                    <div className="dark:hover:text-slate-300 hover:text-slate-500">
                        <Link to={'/challenges'}>
                            <p className="font-bold">Challenges</p>
                        </Link>
                    </div>
                    {
                        loading && <p>Loading...</p>
                    }
                    {
                        error && <p>Error loading login state</p>
                    }
                    {
                        data && data.currentUser === null &&
                        <Link to={'/auth'} className="ml-auto dark:hover:text-slate-300 hover:text-slate-500">
                            <img className="h-5 inline" src={fitbit} alt="Fitbit app icon" />
                            <span className="font-bold">Sign in with Fitbit</span>
                        </Link>
                    }
                    {
                        data && data.currentUser && <p className="ml-auto">{data.currentUser.displayName}</p>
                    }
                </div>
            </div>
        </div>
    );
};

export default NavBar;
