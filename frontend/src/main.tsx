import React from 'react';
import ReactDOM from 'react-dom/client';
import { ApolloProvider } from '@apollo/client';
import App from './App.tsx';
import { apolloClient } from './services/apolloClient.ts';
import { AuthProvider } from './contexts/AuthContext.tsx';
import { initFirebaseApp } from './services/firebase.ts';
import './styles/global.css';

try {
  initFirebaseApp();
} catch (error) {
  console.error('Firebase failed to initialise. Update your .env configuration.', error);
}

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <AuthProvider>
      <ApolloProvider client={apolloClient}>
        <App />
      </ApolloProvider>
    </AuthProvider>
  </React.StrictMode>
);
