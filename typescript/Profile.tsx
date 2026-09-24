import React, { useEffect, useState } from "react";

type ProfileProps = {
  userId: string;
};

export function Profile({ userId }: ProfileProps) {
  const [bio, setBio] = useState<string>("");

  useEffect(() => {
    fetch(`/api/users/${encodeURIComponent(userId)}`)
      .then((r) => r.json())
      .then((data: { bio: string }) => setBio(data.bio));
  }, [userId]);

  return <div className="bio" dangerouslySetInnerHTML={{ __html: bio }} />;
}

export function LoginRedirect() {
  const next = new URLSearchParams(window.location.search).get("next") ?? "/";
  window.location.href = next;
  return <p>Redirecting…</p>;
}
