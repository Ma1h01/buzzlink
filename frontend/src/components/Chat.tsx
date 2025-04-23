import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import ProfileCard from './ProfileCard';

interface Profile {
  id: string;
  name: string;
  profile_pic?: string;
  headline?: string;
  summary?: string;
  linkedin_url?: string;
}

interface Message {
  type: 'user' | 'assistant';
  content: string;
  profiles?: Profile[];
}

interface ApiResponse {
  response: string;
  profiles: Profile[];
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = {
      type: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data: ApiResponse = await response.json();
      const parsedResponse = JSON.parse(data.response);
      
      const assistantMessage: Message = {
        type: 'assistant',
        content: [
          parsedResponse.summary,
          '',
          'Key Highlights:',
          ...parsedResponse.highlights.map(highlight => `• ${highlight}`),
          '',
          'Recommended Profiles:',
          ...parsedResponse.recommendations.map(rec => `• ${rec.name}: ${rec.relevance}`)
        ].join('\n'),
        profiles: data.profiles,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => [
        ...prev,
        {
          type: 'assistant',
          content: 'Sorry, there was an error processing your request.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-2xl mx-auto p-4">
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.type === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.type === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              {message.profiles && (
                <div className="mt-4 space-y-4">
                  {message.profiles.map((profile, profileIndex) => (
                    <ProfileCard
                      key={profileIndex}
                      name={profile.name}
                      image={profile.profile_pic || 'https://via.placeholder.com/150'}
                      summary={profile.summary || profile.headline || 'No summary available'}
                      linkedIn={profile.linkedin_url || '#'}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={isLoading}
        />
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send'}
        </Button>
      </form>
    </div>
  );
} 