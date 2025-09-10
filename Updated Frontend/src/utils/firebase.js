import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut, createUserWithEmailAndPassword, signInWithEmailAndPassword } from 'firebase/auth';
import { getFirestore, doc, getDoc, setDoc, updateDoc, collection, addDoc, query, orderBy, onSnapshot } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "AIzaSyDH0QJx9ru7nM-wCSx-e1qG3ZB3bVxPVzA",
  authDomain: "neerniti-app.firebaseapp.com",
  projectId: "neerniti-app",
  storageBucket: "neerniti-app.firebasestorage.app",
  messagingSenderId: "213008718130",
  appId: "1:213008718130:web:e67cbff848535169629f2b",
  measurementId: "G-WYP252GMMX"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const googleProvider = new GoogleAuthProvider();

// Function to handle Google Sign-In
const signInWithGoogle = async () => {
  try {
    const res = await signInWithPopup(auth, googleProvider);
    const user = res.user;
    const userDocRef = doc(db, "users", user.uid);
    const userDocSnap = await getDoc(userDocRef);

    if (!userDocSnap.exists()) {
      await setDoc(userDocRef, {
        uid: user.uid,
        name: user.displayName,
        email: user.email,
        role: null,
        createdAt: new Date(),
      });
    }
    return user;
  } catch (err) {
    console.error(err);
    throw new Error(err.message);
  }
};

// Function for email/password sign-in/up
const signInWithEmail = async (email, password) => {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;
    
    await setDoc(doc(db, "users", user.uid), {
      uid: user.uid,
      name: email.split('@')[0],
      email: user.email,
      role: null,
      createdAt: new Date(),
    });

    return user;

  } catch (error) {
    if (error.code === 'auth/email-already-in-use') {
      try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        return userCredential.user;
      } catch (err) {
        throw new Error(err.message);
      }
    } else {
      throw new Error(error.message);
    }
  }
};

// Function to update user data in Firestore
const updateUserRole = async (uid, newRole) => {
  try {
    const userDocRef = doc(db, "users", uid);
    await updateDoc(userDocRef, {
      role: newRole
    });
  } catch (err) {
    console.error("Error updating user role:", err);
    throw new Error("Failed to update user role.");
  }
};

// --- THIS FUNCTION WAS LIKELY MISSING ---
// Function to handle user sign-out
const logout = () => {
  signOut(auth);
};

// Function to save a chat message
const saveMessage = async (userId, message) => {
  try {
    const chatCollectionRef = collection(db, "chats", userId, "messages");
    await addDoc(chatCollectionRef, {
      ...message,
      timestamp: new Date()
    });
  } catch (error) {
    console.error("Error saving message: ", error);
  }
};

// Function to get chat messages in real-time
const getMessages = (userId, callback) => {
  const chatCollectionRef = collection(db, "chats", userId, "messages");
  const q = query(chatCollectionRef, orderBy("timestamp", "asc"));

  return onSnapshot(q, (querySnapshot) => {
    const messages = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    callback(messages);
  });
};

// --- AND THIS EXPORT LIST NEEDS TO INCLUDE IT ---
export {
  auth,
  db,
  signInWithGoogle,
  signInWithEmail,
  updateUserRole,
  logout,
  saveMessage,
  getMessages
};