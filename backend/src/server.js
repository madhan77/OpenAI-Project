import express from 'express';
import cors from 'cors';
import { ApolloServer } from 'apollo-server-express';
import http from 'http';

import { environment } from './config/environment.js';
import { typeDefs } from './graphql/schema.js';
import { resolvers } from './graphql/resolvers.js';
import { healthRouter } from './routes/health.js';

async function startServer() {
  const app = express();

  const corsOptions = environment.corsOrigins.length
    ? { origin: environment.corsOrigins }
    : {};
  app.use(cors(corsOptions));
  app.use(express.json());

  app.use('/health', healthRouter);

  const apolloServer = new ApolloServer({
    typeDefs,
    resolvers,
  });

  await apolloServer.start();
  apolloServer.applyMiddleware({ app, path: '/graphql' });

  const httpServer = http.createServer(app);
  const port = environment.port;
  httpServer.listen(port, () => {
    console.log(`Wellness Tracker API running on port ${port}`);
    console.log(`GraphQL endpoint available at /graphql`);
  });
}

startServer().catch((error) => {
  console.error('Failed to start server', error);
  process.exit(1);
});
