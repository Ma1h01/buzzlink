import { ProfileData } from '@/components/ProfileCard';

interface Profile {
  id: string;
  name: string;
  profile_pic?: string;
  headline?: string;
  summary?: string;
  linkedin_url?: string;
}

interface ChatbotResponse {
  summary: string;
  highlights: string[];
  recommendations: Array<{
    name: string;
    relevance: string;
  }>;
}

interface ApiResponse {
  response: string;
  profiles: Profile[];
}

export async function sendChatMessage(message: string): Promise<{ text: string; profiles: Profile[] }> {
  try {
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data: ApiResponse = await response.json();
    const chatbotResponse: ChatbotResponse = JSON.parse(data.response);

    // Format the response text
    const formattedText = [
      chatbotResponse.summary,
      '',
      'Key Highlights:',
      ...chatbotResponse.highlights.map(highlight => `• ${highlight}`),
      '',
      'Recommended Profiles:',
      ...chatbotResponse.recommendations.map(rec => `• ${rec.name}: ${rec.relevance}`)
    ].join('\n');

    return {
      text: formattedText,
      profiles: data.profiles,
    };
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
} 