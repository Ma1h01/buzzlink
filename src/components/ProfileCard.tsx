import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Linkedin } from "lucide-react";

export interface ProfileData {
  id: string;
  name: string;
  image: string;
  summary: string;
  linkedIn?: string;
}

interface ProfileCardProps {
  name: string;
  image: string;
  summary: string;
  linkedIn: string;
}

export default function ProfileCard({ name, image, summary, linkedIn }: ProfileCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 flex flex-col">
      <div className="flex items-center mb-4">
        <img
          src={image}
          alt={`${name}'s profile`}
          className="w-16 h-16 rounded-full object-cover mr-4"
        />
        <div>
          <h3 className="font-semibold text-lg">{name}</h3>
          <a
            href={linkedIn}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500 hover:text-blue-600 text-sm"
          >
            View LinkedIn Profile
          </a>
        </div>
      </div>
      <p className="text-gray-600 text-sm line-clamp-4">{summary}</p>
    </div>
  );
}
