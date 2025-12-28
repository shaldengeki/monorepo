import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
  },
});

// {
//   "bail": 1,
//   "verbose": true,
//   "testEnvironment": "jsdom",
//   "setupFilesAfterEnv": ["./setupTests.js"],
//   "moduleNameMapper": {
//     "\\.(jpg|ico|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$": "<rootDir>/mocks/fileMock.js",
//     "\\.(css|less)$": "<rootDir>/mocks/fileMock.js"
//   }
// }
