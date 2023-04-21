import React from 'react';
import { useQuery, gql } from '@apollo/client';

export const TEST_QUERY = gql`
  query Test {
    test
  }
`;

const MainView = () => {
  const { loading, error, data } = useQuery(TEST_QUERY);

  if (loading) return <p>Loading...</p>;

  if (error) return <p>Error : {error.message}</p>;

  return (
    <div className="dark:bg-neutral-600 h-screen">
      <div className="container mx-auto dark:bg-neutral-600">
          <div>{data.test}</div>
      </div>
    </div>
  )
}

export default MainView;
