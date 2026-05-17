FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# Set environment variables
ENV NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NODE_ENV=development

EXPOSE 3000

CMD ["npm", "run", "dev"]
