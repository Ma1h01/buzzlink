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
    <div className="bg-white rounded-lg shadow-md p-4 flex flex-col">
      <div className="flex items-center mb-4">
        <img
          src={profile.pic}
          alt={`${profile.name}'s profile`}
          className="w-16 h-16 rounded-full object-cover mr-4"
        />
        <div>
          <h3 className="font-semibold text-lg">{profile.name}</h3>
          <a
            href={profile.id}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500 hover:text-blue-600 text-sm"
          >
            View LinkedIn Profile
          </a>
        </div>
      </div>
      <p className="text-gray-600 text-sm line-clamp-4">{profile.summary}</p>
    </div>
  );
}
