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
  result: Array<{
    id: string;
    name: string;
    pic?: string;
    summary?: string;
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
    console.log('Raw API Response:', data);
    const chatbotResponse: ChatbotResponse = JSON.parse(data.response);
    console.log('Parsed Chatbot Response:', chatbotResponse);

    // Format the response text with just a simple header
    const formattedText = [
      `Here are the results:`,
      ''
    ].join('\n');

    // Convert the result array into Profile objects
    const profiles = chatbotResponse.result.map(profile => ({
      id: profile.id,
      name: profile.name,
      pic: profile.pic || '',  // Add fallback for missing profile pics
      summary: profile.summary || ''  // Add fallback for missing summaries
    }));

    return {
      text: formattedText,
      profiles: profiles,
    };
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
} 