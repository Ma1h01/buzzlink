
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
  profile: ProfileData;
}

const ProfileCard: React.FC<ProfileCardProps> = ({ profile }) => {
  return (
    <Card className="overflow-hidden border border-gray-200 animate-message-fade-in opacity-0" style={{ animationDelay: '0.1s' }}>
      <CardContent className="p-0">
        <div className="flex flex-col sm:flex-row">
          <div className="w-full sm:w-32 h-32 bg-gtlightgrey">
            <img 
              src={profile.image} 
              alt={profile.name} 
              className="w-full h-full object-cover"
            />
          </div>
          <div className="p-4 flex-1">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-bold text-lg text-gtnavy">{profile.name}</h3>
                <p className="text-sm text-gtgrey mt-2">{profile.summary}</p>
              </div>
              {profile.linkedIn && (
                <Button variant="outline" size="sm" className="bg-blue-500 hover:bg-blue-600 text-white border-0">
                  <Linkedin className="h-4 w-4 mr-1" /> Connect
                </Button>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ProfileCard;
