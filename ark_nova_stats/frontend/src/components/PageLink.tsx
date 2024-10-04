import React, {PropsWithChildren} from 'react';
import { Link } from 'react-router-dom';

type PageLinkProps = {
    to: any;
    className?: string;
}

const PageLink = (props: PropsWithChildren<PageLinkProps>) => {
    const defaultClasses = "";
    const actualClasses = props.className ? defaultClasses + " " + props.className : defaultClasses;

    return (
        <span className={actualClasses}>
            <Link to={props.to}>
                {props.children}
            </Link>
        </span>
    );
}

export default PageLink;
