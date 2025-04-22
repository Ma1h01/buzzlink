import { Linkedin } from 'lucide-react';

export interface ProfileData {
  id: string;
  name: string;
  pic: string;
  summary: string;
}

interface ProfileCardProps {
  profile: ProfileData;
}

export default function ProfileCard({ profile }: ProfileCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <div className="flex items-start space-x-4">
        <img
          src={profile.pic}
          alt={`${profile.name}'s profile`}
          className="w-16 h-16 rounded-full object-cover flex-shrink-0"
        />
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-lg">{profile.name}</h3>
            <a
              href={profile.id}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 hover:text-blue-600 flex-shrink-0"
              title="View LinkedIn Profile"
            >
              <Linkedin className="w-5 h-5" />
            </a>
          </div>
          <p className="text-gray-600 mt-2">{profile.summary}</p>
        </div>
      </div>
    </div>
  );
}
