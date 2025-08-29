import React, {PropsWithChildren} from 'react';
import { Link } from 'react-router-dom';

type NavBarElementProps = {
    link?: string;
    text?: string;
    className?: string;
}

export const NavBarElement = (props: PropsWithChildren<NavBarElementProps>) => {
    const defaultClassName = "dark:hover:text-slate-300 hover:text-slate-500";
    const actualClassName = props.className ? defaultClassName + " " + props.className : defaultClassName;

    let innerContent = props.children;
    if (props.text !== undefined) {
        innerContent = <p>{props.text}</p>;
    }
    if (props.link !== undefined) {
        innerContent = (<Link to={props.link}>
            {innerContent}
        </Link>);
    }

    return (
        <div className={actualClassName}>
            {innerContent}
        </div>
    );
}

type NavBarProps = {
    logo?: any;
    title?: string;
    className?: string;
}

const NavBar = (props: PropsWithChildren<NavBarProps>) => {
    const titleElt = props.title ? <span>{props.title}</span> : <span></span>;
    const logoElt = props.logo ? (<NavBarElement link={'/'} className={"font-bold"}>
                            <img className="flex-none h-6 inline" src={props.logo} alt="App icon" />
                            {titleElt}
                        </NavBarElement>) : <></>;
    return (
        <div className="sticky top-0 z-40 w-full backdrop-blur flex-none lg:border-b lg:border-slate-900/10 lg:dark:border-slate-50/[0.06] bg-white/95 supports-backdrop-blur:bg-white/60 dark:bg-transparent">
            <div className="max-w-screen-2xl mx-auto">
                <div className="py-4 mx-4 lg:mx-0 lg:px-8 relative flex items-center gap-4 dark:text-slate-400">
                    <div className="py-4 mx-4 lg:mx-0 lg:pr-8 relative flex items-center gap-4 dark:text-slate-400">
                        {logoElt}
                        {props.children}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default NavBar;
