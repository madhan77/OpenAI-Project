import { ApolloClient, HttpLink, InMemoryCache } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { getFirebaseAuth } from './firebase.ts';

const httpLink = new HttpLink({
  uri: import.meta.env.VITE_GRAPHQL_URL ?? 'http://localhost:4000/graphql'
});

const authLink = setContext(async (_, { headers }) => {
  try {
    const auth = getFirebaseAuth();
    const currentUser = auth.currentUser;
    const token = currentUser ? await currentUser.getIdToken() : null;

    return {
      headers: {
        ...headers,
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    };
  } catch (error) {
    console.warn('Unable to attach Firebase auth header', error);
    return { headers };
  }
});

export const apolloClient = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          dailyInsights: {
            merge: false
          },
          weeklyProgress: {
            merge: false
          }
        }
      }
    }
  })
});
