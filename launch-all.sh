#!/bin/bash

# # Change to the backend directory and start the uvicorn server
# cd backend
# uvicorn rag:app --reload &

# # Change to the frontend directory
# cd ../casc-frontend

# # Install dependencies
# pnpm i

# # Start the development server
# pnpm run dev

#!/bin/bash

#UPDATED LAUNCH FILE TO INCORPORATE CHATBOT

# Change to the backend directory and start the uvicorn server
cd backend
uvicorn main:app --reload &

# Change to the frontend directory
cd ../casc-frontend

# Install dependencies
pnpm i

# Start the development server
pnpm run dev