import React, { useState, useRef, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import ResponseList from './ResponseList';
import { ProfileData } from './ProfileCard';
import { Send } from 'lucide-react';
import { sendChatMessage } from '@/api/chat';
import { useToast } from "@/components/ui/use-toast";

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
      profiles: []
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const newMessage: Message = {
      id: Date.now().toString(),
      type: 'query',
      text: input
    };
    
    setMessages(prev => [...prev, newMessage]);
    setIsLoading(true);
    
    try {
      const response = await sendChatMessage(input);
      
      const responseMessage: Message = {
        id: Date.now().toString(),
        type: 'response',
        text: response.text,
        profiles: response.profiles
      };
      
      setMessages(prev => [...prev, responseMessage]);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to get response from the chatbot. Please try again.",
        variant: "destructive",
      });
    } finally {
      setInput('');
      setIsLoading(false);
    }
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
