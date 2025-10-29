import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from 'react';
import {
  onIdTokenChanged,
  signInWithPopup,
  signOut as firebaseSignOut,
  type User,
} from 'firebase/auth';
import { apolloClient } from '../services/apolloClient.ts';
import { getFirebaseAuth, googleAuthProvider } from '../services/firebase.ts';

interface AuthContextValue {
  user: User | null;
  token: string | null;
  loading: boolean;
  initializationError: Error | null;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: PropsWithChildren): JSX.Element {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [initializationError, setInitializationError] = useState<Error | null>(null);

  useEffect(() => {
    let unsubscribe: (() => void) | undefined;
    async function initialize() {
      try {
        const auth = getFirebaseAuth();
        unsubscribe = onIdTokenChanged(auth, async (firebaseUser) => {
          setUser(firebaseUser);
          if (firebaseUser) {
            try {
              const idToken = await firebaseUser.getIdToken();
              setToken(idToken);
            } catch (tokenError) {
              console.warn('Unable to retrieve Firebase ID token', tokenError);
              setToken(null);
            }
          } else {
            setToken(null);
          }
          setLoading(false);
          try {
            await apolloClient.reFetchObservableQueries();
          } catch (refreshError) {
            console.warn('Failed to refresh GraphQL queries after auth change', refreshError);
          }
        });
      } catch (error) {
        const err = error instanceof Error ? error : new Error('Failed to initialise Firebase');
        setInitializationError(err);
        setLoading(false);
        console.error(err);
      }
    }

    void initialize();

    return () => {
      if (unsubscribe) {
        unsubscribe();
      }
    };
  }, []);

  const signInWithGoogle = useCallback(async () => {
    const auth = getFirebaseAuth();
    await signInWithPopup(auth, googleAuthProvider);
  }, []);

  const signOut = useCallback(async () => {
    const auth = getFirebaseAuth();
    await firebaseSignOut(auth);
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    token,
    loading,
    initializationError,
    signInWithGoogle,
    signOut,
  }), [user, token, loading, initializationError, signInWithGoogle, signOut]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
