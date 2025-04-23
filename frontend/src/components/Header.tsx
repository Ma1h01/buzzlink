
import React from 'react';
import { cn } from "@/lib/utils";

interface HeaderProps {
  className?: string;
}

const Header: React.FC<HeaderProps> = ({ className }) => {
  return (
    <header className={cn("w-full border-b border-gray-200 bg-white py-4", className)}>
      <div className="container flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-bold text-gtnavy"><span className="text-gtgold">Buzz</span>Link</h1>
        </div>
      </div>
    </header>
  );
};

export default Header;
