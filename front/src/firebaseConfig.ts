import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: "project-web-ai-3d052.firebaseapp.com",
  projectId: "project-web-ai-3d052",
  storageBucket: "project-web-ai-3d052.firebasestorage.app",
  messagingSenderId: "245388012694",
  appId: "1:245388012694:web:2993b2db20bab1070b26b7"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);