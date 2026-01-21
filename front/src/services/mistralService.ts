import { Mistral } from '@mistralai/mistralai'

const apiKey = import.meta.env.VITE_MISTRAL_API_KEY

if (!apiKey) {
  throw new Error('VITE_MISTRAL_API_KEY is not set in environment variables.')
}

const client = new Mistral({
  apiKey,
})

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export async function chatWithMistral(
  messages: ChatMessage[],
  model: string = 'mistral-large-latest'
): Promise<string> {
  try {
    const response = await client.chat.complete({
      model,
      messages,
    })

    return response.choices[0]?.message?.content || ''
  } catch (error) {
    console.error('Error communicating with Mistral AI:', error)
    throw error
  }
}

export async function chatWithContext(
  userQuery: string,
  contextDocuments: string[],
  conversationHistory: ChatMessage[] = [],
  model: string = 'mistral-large-latest'
): Promise<string> {
  // Build context from documents
  const context = contextDocuments.join('\n\n')
  
  const systemPrompt = `You are a helpful study assistant. Use the following documents to answer questions:

${context}

Be concise and helpful in your responses.`

  const messages: ChatMessage[] = [
    ...conversationHistory,
    { role: 'user', content: userQuery },
  ]

  try {
    const response = await client.chat.complete({
      model,
      messages,
      systemPrompt,
    })

    return response.choices[0]?.message?.content || ''
  } catch (error) {
    console.error('Error communicating with Mistral AI:', error)
    throw error
  }
}
