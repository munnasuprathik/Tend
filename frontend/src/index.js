import React from "react";
import ReactDOM from "react-dom/client";
import { ClerkProvider } from "@clerk/clerk-react";
import "@/index.css";
import App from "@/App";

const clerkPublishableKey =
  process.env.REACT_APP_CLERK_PUBLISHABLE_KEY ||
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ||
  "pk_test_Y29zbWljLWRhc3NpZS02My5jbGVyay5hY2NvdW50cy5kZXYk";

if (!clerkPublishableKey) {
  console.error(
    "Missing Clerk publishable key. Set REACT_APP_CLERK_PUBLISHABLE_KEY or NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.",
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <ClerkProvider publishableKey={clerkPublishableKey}>
      <App />
    </ClerkProvider>
  </React.StrictMode>,
);
