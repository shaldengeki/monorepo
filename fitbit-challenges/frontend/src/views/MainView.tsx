import React from 'react';
import { useQuery, gql } from '@apollo/client';

export const TEST_QUERY = gql`
  query Test {
    test
  }
`;

const MainView = () => {
  const { loading, error, data } = useQuery(TEST_QUERY);

  let innerContent = <p></p>;
  if (loading) innerContent = <p>Loading...</p>;
  else if (error) innerContent = <p>Error : {error.message}</p>;
  else {
    innerContent = <div>{data.test}</div>;
  }
  return (
    <div className="dark:bg-neutral-600 dark:text-slate-400 h-screen">
      <div className="container mx-auto dark:bg-neutral-600">
          {innerContent}
      </div>
    </div>
  )
}

export default MainView;
