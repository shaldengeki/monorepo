import {PropsWithChildren} from 'react';

type PageContainerProps = {
    outerClassName?: string;
    innerClassName?: string;
    navbar: React.JSX.Element;
    titleComponent?: React.JSX.Element;
}

const PageContainer = (props: PropsWithChildren<PageContainerProps>) => {
    const defaultOuterClasses = "page-container bg-white/95 dark:bg-slate-900 dark:text-slate-400";
    const actualOuterClasses = props.outerClassName ? defaultOuterClasses + " " + props.outerClassName : defaultOuterClasses;

    const defaultInnerClasses = "container mx-auto p-2 flex flex-col overflow-auto";
    const actualInnerClasses = props.innerClassName ? defaultInnerClasses + " " + props.innerClassName : defaultInnerClasses;

    const contentClasses = "page-contents";

    return (
        <div className={actualOuterClasses}>
            {props.navbar}
            <div className={actualInnerClasses}>
                {props.titleComponent ? props.titleComponent: <></>}
                <div className={contentClasses}>
                    {props.children}
                </div>
            </div>
        </div>
    );
}

export default PageContainer;
