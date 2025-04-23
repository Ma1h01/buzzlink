
import React from 'react';
import Header from '@/components/Header';
import ChatInterface from '@/components/ChatInterface';

const Index = () => {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      <main className="flex-1 container mx-auto mt-6 mb-6 max-w-4xl">
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden h-[calc(100vh-120px)]">
          <ChatInterface />
        </div>
      </main>
      <footer className="bg-gtnavy text-white py-4">
        <div className="container text-center text-sm">
          <p>© {new Date().getFullYear()} BuzzLink | Georgia Institute of Technology</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
