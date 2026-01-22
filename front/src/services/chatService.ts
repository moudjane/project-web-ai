import { getFirestore, collection, addDoc, query, getDocs, orderBy, where, getDoc, doc, updateDoc } from "firebase/firestore"
import { auth } from "@/firebaseConfig"

const db = getFirestore()
const API_URL = "http://localhost:8000"

/**
 * Interroge le backend pour récupérer les segments de PDF pertinents
 */
export async function queryVectorStore(prompt: string): Promise<string> {
  const user = auth.currentUser
  if (!user) {
    throw new Error("User not authenticated")
  }

  try {
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: prompt,
        user_id: user.uid,
        k: 4 // Nombre de segments à récupérer
      })
    })

    if (!response.ok) {
      throw new Error("Failed to query vector store")
    }

    const data = await response.json()
    
    if (data.results_count === 0) {
      return ""
    }

    // On concatène les résultats pour créer le contexte
    return data.results
      .map((res) => `[Source: ${res.metadata.source}]: ${res.content}`)
      .join("\n\n")
  } catch (error) {
    console.error("Vector store query error:", error)
    return ""
  }
}

export async function savePrompt(chatId: string, prompt: string, role: "user" | "assistant" = "user"): Promise<string> {
  const user = auth.currentUser

  if (!user) {
    throw new Error("User not authenticated")
  }

  const docRef = await addDoc(collection(db, "chats", chatId, "messages"), {
    content: prompt,
    role,
    timestamp: new Date().toISOString(),
  })
  return docRef.id
}

export async function getChatHistory(chatId: string) {
  const messagesRef = collection(db, "chats", chatId, "messages")
  const q = query(messagesRef, orderBy("timestamp", "asc"))
  const snapshot = await getDocs(q)
  return snapshot.docs.map(doc => doc.data())
}

export async function createChat(title: string = "New Chat", subject: string = ""): Promise<string> {
  const user = auth.currentUser
  const userId = user ? user.uid : "anonymous"

  const docRef = await addDoc(collection(db, "chats"), {
    userId,
    title,
    subject,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  })
  return docRef.id
}

export async function getCurrentUserChats(): Promise<Array<{ id: string; title: string }>> {
  const user = auth.currentUser
  
  if (!user) {
    throw new Error("User not authenticated")
  }

  return getChatsByUserId(user.uid)
}

export async function getChatsByUserId(userId: string): Promise<Array<{ id: string; title: string }>> {
  const chatsRef = collection(db, "chats")
  const q = query(chatsRef, where("userId", "==", userId), orderBy("updatedAt", "desc"))
  const snapshot = await getDocs(q)
  
  return snapshot.docs.map(doc => ({
    id: doc.id,
    title: doc.data().title
  }))
}

export async function getChatById(chatId: string): Promise<{ id: string; title: string; userId: string; subject?: string; createdAt: string; updatedAt: string }> {
  const chatRef = doc(db, "chats", chatId)
  const snapshot = await getDoc(chatRef)
  
  if (!snapshot.exists()) {
    throw new Error("Chat not found")
  }
  
  return {
    id: snapshot.id,
    ...snapshot.data()
  } as { id: string; title: string; userId: string; subject?: string; createdAt: string; updatedAt: string }
}

export async function updateChatTitle(chatId: string, newTitle: string): Promise<void> {
  const chatRef = doc(db, "chats", chatId)
  
  await updateDoc(chatRef, {
    title: newTitle,
    updatedAt: new Date().toISOString(),
  })
}
