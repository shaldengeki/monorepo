import React from 'react';
import logo192 from './logo192.png';
import { Link } from 'react-router-dom';

type NavBarProps = {
    className?: string;
}

const NavBar = (props: NavBarProps) => {
    return (
        <div className="sticky top-0 z-40 w-full backdrop-blur flex-none lg:border-b lg:border-slate-900/10 lg:dark:border-slate-50/[0.06] bg-white/95 supports-backdrop-blur:bg-white/60 dark:bg-transparent">
            <div className="max-w-screen-2xl mx-auto">
                <div className="py-4 mx-4 lg:mx-0 lg:px-8 relative flex items-center gap-2 dark:text-slate-400">
                    <img className="flex-none h-6 inline" src={logo192} alt="Fitbit app icon" />
                    <div className="dark:hover:text-slate-300 hover:text-slate-500">
                        <Link to={'/'}>
                            <p className="font-bold">Ark Nova Games Database</p>
                        </Link>
                    </div>
                    <div className="dark:hover:text-slate-300 hover:text-slate-500">
                        <Link to={'/cards'}>
                            <p>Cards</p>
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default NavBar;
