import React, {PropsWithChildren} from 'react';
import { Link } from 'react-router-dom';

type PageTitleProps = {
    className?: string;
    linkTo?: string;
}

const PageTitle = (props: PropsWithChildren<PageTitleProps>) => {
    const defaultClasses = "text-4xl font-bold pb-4 mb-4 border-b-2 border-slate-50 dark:border-neutral-600 dark:text-slate-200";
    const actualClasses = props.className ? defaultClasses + " " + props.className : defaultClasses;

    let innerContent = props.children
    if (props.linkTo !== undefined) {
        innerContent = <Link to={props.linkTo}>{innerContent}</Link>
    }

    return (
        <div className={actualClasses}>
            { innerContent }
        </div>
    );
};

export default PageTitle;
