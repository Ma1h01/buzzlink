import React, { useState, useRef, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import ResponseList from './ResponseList';
import { ProfileData } from './ProfileCard';
import { Send } from 'lucide-react';

// Sample data for demo purposes - now matches the new data structure
const mockProfiles: ProfileData[] = [
  {
    id: '1',
    name: 'Sarah Johnson',
    image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330',
    summary: 'Software Engineer with experience in full-stack development and cloud computing. Currently working on AI/ML projects.',
    linkedIn: 'https://linkedin.com/'
  },
  {
    id: '2',
    name: 'David Chen',
    image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d',
    summary: 'Product Manager specializing in tech products. Experienced in agile methodologies and cross-functional team leadership.',
    linkedIn: 'https://linkedin.com/'
  },
  {
    id: '3',
    name: 'Maria Rodriguez',
    image: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80',
    summary: 'Research Scientist focusing on aerospace engineering. Leading innovative projects in spacecraft propulsion systems.',
    linkedIn: 'https://linkedin.com/'
  }
];

// Mock software engineering profiles
const softwareProfiles: ProfileData[] = [
  {
    id: '4',
    name: 'James Wilson',
    image: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=634&q=80',
    summary: 'Senior Software Engineer at Amazon.',
    linkedIn: 'https://linkedin.com/'
  },
  {
    id: '5',
    name: 'Emily Taylor',
    image: 'https://images.unsplash.com/photo-1554151228-14d9def656e4?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=634&q=80',
    summary: 'Frontend Developer at Twitter.',
    linkedIn: 'https://linkedin.com/'
  },
  {
    id: '6',
    name: 'Michael Chang',
    image: 'https://images.unsplash.com/photo-1552058544-f2b08422138a?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=634&q=80',
    summary: 'Full Stack Engineer at Facebook.',
    linkedIn: 'https://linkedin.com/'
  }
];

// Mock finance profiles
const financeProfiles: ProfileData[] = [
  {
    id: '7',
    name: 'Sophia Patel',
    image: 'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=634&q=80',
    summary: 'Investment Banking Analyst at Goldman Sachs.',
    linkedIn: 'https://linkedin.com/'
  },
  {
    id: '8',
    name: 'Robert Johnson',
    image: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=634&q=80',
    summary: 'Financial Analyst at JP Morgan Chase.',
    linkedIn: 'https://linkedin.com/'
  },
  {
    id: '9',
    name: 'Jennifer Lee',
    image: 'https://images.unsplash.com/photo-1491349174775-aaafddd81942?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=634&q=80',
    summary: 'Wealth Management Associate at Morgan Stanley.',
    linkedIn: 'https://linkedin.com/'
  }
];

interface Message {
  id: string;
  type: 'query' | 'response';
  text?: string;
  profiles?: ProfileData[];
}

const ChatInterface: React.FC = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      type: 'response',
      text: 'Welcome to BuzzLink! Ask me to help you find Georgia Tech alumni by field, location, or company. Try something like "Find alumni in software engineering" or "Show me GT graduates at Google".',
      profiles: mockProfiles
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const newMessage: Message = {
      id: Date.now().toString(),
      type: 'query',
      text: input
    };
    
    setMessages(prev => [...prev, newMessage]);
    setIsLoading(true);
    
    // Mock response based on user query
    setTimeout(() => {
      let responseProfiles: ProfileData[] = [];
      const query = input.toLowerCase();
      
      if (query.includes('software') || query.includes('engineer') || query.includes('developer') || query.includes('programming')) {
        responseProfiles = softwareProfiles;
      } else if (query.includes('finance') || query.includes('banking') || query.includes('investment')) {
        responseProfiles = financeProfiles;
      } else {
        responseProfiles = mockProfiles;
      }
      
      const responseMessage: Message = {
        id: Date.now().toString(),
        type: 'response',
        text: `Here are some alumni matching your query: "${input}"`,
        profiles: responseProfiles
      };
      
      setMessages(prev => [...prev, responseMessage]);
      setInput('');
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-80px)]">
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-6 mb-4">
          {messages.map((message) => (
            <div key={message.id} className={`${message.type === 'query' ? 'ml-auto max-w-[80%]' : 'mr-auto max-w-full'}`}>
              {message.type === 'query' ? (
                <div className="bg-gtnavy text-white p-3 rounded-lg animate-message-fade-in opacity-0">
                  {message.text}
                </div>
              ) : (
                <div className="space-y-3 animate-message-fade-in opacity-0">
                  {message.text && (
                    <div className="bg-white border border-gray-200 p-3 rounded-lg shadow-sm">
                      {message.text}
                    </div>
                  )}
                  {message.profiles && message.profiles.length > 0 && (
                    <ResponseList profiles={message.profiles} queryText={message.text} />
                  )}
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>
      
      <div className="border-t p-4 bg-white">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about GT alumni by field, company, or location..."
            className="flex-1"
            disabled={isLoading}
          />
          <Button type="submit" disabled={isLoading} className="bg-gtgold hover:bg-yellow-600">
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
