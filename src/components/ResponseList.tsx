import React from 'react';
import ProfileCard, { ProfileData } from './ProfileCard';

interface ResponseListProps {
  profiles: ProfileData[];
  queryText?: string;
}

const ResponseList: React.FC<ResponseListProps> = ({ profiles, queryText }) => {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {profiles.length > 0 ? (
          profiles.map((profile) => (
            <ProfileCard
              key={profile.id}
              profile={profile}
            />
          ))
        ) : (
          <div className="text-center py-6 text-gtgrey col-span-full">
            No profiles found matching your query.
          </div>
        )}
      </div>
    </div>
  );
};

export default ResponseList;
