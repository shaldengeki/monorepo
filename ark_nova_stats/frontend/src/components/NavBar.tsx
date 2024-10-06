import React from 'react';
import logo192 from './logo192.png';
import { Link } from 'react-router-dom';

type NavBarElementProps = {
    text: string;
    link?: string;
    className?: string;
}

const NavBarElement = (props: NavBarElementProps) => {
    const defaultClassName = "dark:hover:text-slate-300 hover:text-slate-500";
    const actualClassName = props.className ? defaultClassName + " " + props.className : defaultClassName;

    let innerContent = <p>{props.text}</p>
    if (props.link !== undefined) {
        innerContent = (<Link to={props.link}>
            <p>{props.text}</p>
        </Link>);
    }

    return (
        <div className={actualClassName}>
            {innerContent}
        </div>
    );
}

type NavBarProps = {
    className?: string;
}

const NavBar = (props: NavBarProps) => {
    return (
        <div className="sticky top-0 z-40 w-full backdrop-blur flex-none lg:border-b lg:border-slate-900/10 lg:dark:border-slate-50/[0.06] bg-white/95 supports-backdrop-blur:bg-white/60 dark:bg-transparent">
            <div className="max-w-screen-2xl mx-auto">
                <div className="py-4 mx-4 lg:mx-0 lg:px-8 relative flex items-center gap-2 dark:text-slate-400">
                    <img className="flex-none h-6 inline" src={logo192} alt="Fitbit app icon" />
                    <NavBarElement link={'/'} text={"Ark Nova Games Database"} className={"font-bold"} />
                    <NavBarElement link={'/emu_cup'} text={"Emu Cup"} />
                    <NavBarElement link={'/cards'} text={"Cards"} />
                </div>
            </div>
        </div>
    );
};

export default NavBar;
