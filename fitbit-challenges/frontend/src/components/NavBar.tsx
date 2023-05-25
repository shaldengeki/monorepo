import React from 'react';
import fitbit from './fitbit.png';
import { Link } from 'react-router-dom';

type NavBarProps = {
    className?: string;
}

const NavBar = (props: NavBarProps) => {
    return (
        <div className="leading-6 w-full sticky border-b border-b-slate-50 py-4 px-1 bg-blue-200 dark:bg-slate-900 dark:text-slate-400">
            <div className="relative flex items-center">
                <Link to={'/auth'} className="ml-auto">
                    <img className="h-5 inline" src={fitbit} alt="Fitbit app icon" />
                    <span>Sign in with Fitbit</span>
                </Link>
            </div>
        </div>
    );
};

export default NavBar;
