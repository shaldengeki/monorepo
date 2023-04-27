import React, {PropsWithChildren} from 'react';

type PageContainerProps = {
    outerClassName?: string;
    innerClassName?: string;
}

const PageContainer = (props: PropsWithChildren<PageContainerProps>) => {
    const defaultOuterClasses = "dark:bg-neutral-600 dark:text-slate-400 h-screen";
    const actualOuterClasses = props.outerClassName ? defaultOuterClasses + " " + props.outerClassName : defaultOuterClasses;

    const defaultInnerClasses = "container mx-auto bg-blue-200 dark:bg-indigo-950 dark:text-slate-400 p-2 h-screen flex flex-col";
    const actualInnerClasses = props.innerClassName ? defaultInnerClasses + " " + props.innerClassName : defaultInnerClasses;

    return (
        <div className={actualOuterClasses}>
            <div className={actualInnerClasses}>
                {props.children}
            </div>
        </div>
    );
}

export default PageContainer;
