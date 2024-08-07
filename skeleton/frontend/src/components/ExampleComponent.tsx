import React, {PropsWithChildren} from 'react';

type ExampleComponentProps = {
    className?: string;
}

const ExampleComponent = (props: PropsWithChildren<ExampleComponentProps>) => {
    const defaultClasses = "text-4xl font-bold pb-4 mb-4 border-b-2 border-slate-50 dark:border-neutral-600 dark:text-slate-200";
    const actualClasses = props.className ? defaultClasses + " " + props.className : defaultClasses;

    return (
        <div className={actualClasses}>
            {props.children}
            <p>Hello World!</p>
        </div>
    );
};

export default ExampleComponent;
