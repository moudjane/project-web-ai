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
  model: string = 'mistral-large-latest',
): Promise<string> {
  try {
    const response = await client.chat.complete({
      model,
      messages,
    })

    const content = response.choices[0]?.message?.content
    return typeof content === 'string' ? content : ''
  } catch (error) {
    console.error('Error communicating with Mistral AI:', error)
    throw error
  }
}
