
import React from 'react';
import ProfileCard, { ProfileData } from './ProfileCard';

interface ResponseListProps {
  profiles: ProfileData[];
  queryText?: string;
}

const ResponseList: React.FC<ResponseListProps> = ({ profiles, queryText }) => {
  return (
    <div className="space-y-4">
      {queryText && (
        <div className="text-sm text-gtgrey mb-4 animate-message-fade-in opacity-0">
          Showing results for: <span className="font-medium">{queryText}</span>
        </div>
      )}
      {profiles.length > 0 ? (
        profiles.map((profile) => (
          <ProfileCard 
            key={profile.id} 
            profile={profile} 
          />
        ))
      ) : (
        <div className="text-center py-6 text-gtgrey">
          No profiles found matching your query.
        </div>
      )}
    </div>
  );
};

export default ResponseList;
