import React, {PropsWithChildren} from 'react';
import NavBar from './NavBar';

type PageContainerProps = {
    outerClassName?: string;
    innerClassName?: string;
}

const PageContainer = (props: PropsWithChildren<PageContainerProps>) => {
    const defaultOuterClasses = "bg-white/95 dark:bg-slate-900 dark:text-slate-400";
    const actualOuterClasses = props.outerClassName ? defaultOuterClasses + " " + props.outerClassName : defaultOuterClasses;

    const defaultInnerClasses = "container mx-auto p-2 flex flex-col overflow-auto";
    const actualInnerClasses = props.innerClassName ? defaultInnerClasses + " " + props.innerClassName : defaultInnerClasses;

    return (
        <div className={actualOuterClasses}>
            <NavBar />
            <div className={actualInnerClasses}>
                {props.children}
            </div>
        </div>
    );
}

export default PageContainer;
