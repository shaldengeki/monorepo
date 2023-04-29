import React, {PropsWithChildren} from 'react';

type FormButtonProps = {
    hook?: Function
    className?: string
}

const FormButton = (props: PropsWithChildren<FormButtonProps>) => {
    const baseClasses = "p-0.5 mx-0.5 rounded dark:text-slate-400"
    let actualClasses = baseClasses
    if (props.className) {
        actualClasses += props.className;
    }

    return (
        <button
            className={actualClasses}
            onClick={(e) => {
                e.preventDefault();
                props.hook && props.hook(e);
            }}
        >
            {props.children}
        </button>
    )
}

export default FormButton;

type CancelButtonProps = {
    hook?: Function
}

export const CancelButton = (props: PropsWithChildren<CancelButtonProps>) => {
    return (
        <FormButton hook={props.hook} className={"bg-teal-400 dark:bg-slate-600 dark:text-slate-400"}>
            {props.children}
        </FormButton>
    );
}

type SubmitButtonProps = {
    hook?: Function
}

export const SubmitButton = (props: PropsWithChildren<SubmitButtonProps>) => {
    return (
        <FormButton hook={props.hook} className={"bg-teal-400 dark:bg-pink-900 dark:text-slate-400"}>
            {props.children}
        </FormButton>
    );
}
