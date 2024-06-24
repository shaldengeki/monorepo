import { render } from '@testing-library/react';
import DatePicker from './DatePicker';
import React from 'react';

it('should render', async () => {
    render(
        <DatePicker start={1} end={2} onChangeStart={() => {}} onChangeEnd={() => {}} />
    );
});
