# seed_minio.py
import io

from minio import Minio

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
)
# 7baa6f28-ac45-42db-b8a4-e00bf4ff2a24
# Create the projects bucket
if not client.bucket_exists("projects"):
    client.make_bucket("projects")

# Use one of your existing project IDs from PostgreSQL.
# Replace this with an actual project UUID from your DB.
PROJECT_ID = "7baa6f28-ac45-42db-b8a4-e00bf4ff2a24"


def upload(path: str, content: str):
    data = content.encode("utf-8")
    client.put_object(
        "projects",
        f"{PROJECT_ID}/{path}",
        io.BytesIO(data),
        length=len(data),
        content_type="text/plain",
    )
    print(f"  uploaded: {path}")


# Seed a small React project
upload(
    "package.json",
    """{
  "name": "devcollab-test",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}""",
)

upload(
    "src/App.tsx",
    """import React from 'react';
import { ProfileCard } from './components/ProfileCard';

function App() {
  return (
    <div className="app">
      <h1>DevCollab</h1>
      <ProfileCard name="Bishal" role="Developer" />
    </div>
  );
}

export default App;
""",
)

upload(
    "src/components/ProfileCard.tsx",
    """import React from 'react';

interface ProfileCardProps {
  name: string;
  role: string;
}

export function ProfileCard({ name, role }: ProfileCardProps) {
  return (
    <div className="profile-card">
      <h2>{name}</h2>
      <p>{role}</p>
      <button style={{ backgroundColor: 'blue', color: 'white' }}>
        View Profile
      </button>
    </div>
  );
}
""",
)

print("Done! Test project seeded.")
