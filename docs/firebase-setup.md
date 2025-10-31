# Firebase setup guide

Follow these steps to connect the Single Issue Management prototype to **your** Firebase project. The process does not require
any production data—the application continues to consume local mock data, but authentication is delegated to your Google
identity provider instance.

## 1. Create or select a Firebase project

1. Navigate to [https://console.firebase.google.com](https://console.firebase.google.com) and sign in with your Google account.
2. Create a new project (or reuse an existing one) that will host authentication for the prototype.
3. Once the project is created, click the **Web** (</>) icon to register a new web app. You can name the app anything you like; hosting is optional.

## 2. Enable Google sign-in

1. Inside your Firebase project, open **Build → Authentication → Sign-in method**.
2. Enable the **Google** provider and supply a support email when prompted.
3. Save the changes. No other providers are required for the mock-data prototype.

## 3. Collect the web app credentials

1. Still within the Firebase console, locate the **SDK setup and configuration** card for your web app.
2. Copy the configuration object fields (`apiKey`, `authDomain`, `projectId`, `appId`, and optionally `measurementId` and
   `storageBucket` if you plan to use them later).

## 4. Provide credentials to the frontend

1. In the repository, copy `frontend/.env.example` to `frontend/.env.local`:

   ```bash
   cp frontend/.env.example frontend/.env.local
   ```

2. Paste the values from the Firebase console into `.env.local`, replacing each placeholder:

   ```env
   VITE_FIREBASE_API_KEY=your-api-key
   VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your-project-id
   VITE_FIREBASE_APP_ID=your-app-id
   ```

3. (Optional) If you captured additional fields such as `storageBucket` or `measurementId`, you can add them to the `.env.local`
   file using the `VITE_FIREBASE_` prefix. The frontend will pick them up automatically as long as you pass them into the
   Firebase configuration object.

## 5. Start the development server

Run the Vite development server to verify sign-in is working:

```bash
cd frontend
npm install
npm run dev
```

Visit [http://localhost:5173/login](http://localhost:5173/login) and authenticate with Google. Upon successful login, you will
be redirected to the dashboard populated with mock incident data.

## 6. Share access with collaborators

Each collaborator must be granted access to your Firebase project. Add their Google accounts under **Project settings → Users and
permissions**, and then share the `/login` URL. They will be prompted to sign in with the same Google identity provider and will
land on the mock dashboard once authenticated.

---

With these steps complete, the prototype uses your Firebase account purely for authentication while continuing to rely on
mock operational data for the dashboard content.
