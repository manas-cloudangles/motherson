# Motherson UI

A modern React application built with Vite for creating and downloading app components.

## Features

- **Chat Page**: ChatGPT-like interface for interactive conversations
- **Elements Page**: Select common UI elements and preview them in real-time
- **Download Page**: Download HTML, CSS, and TypeScript files for your app

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
├── public/              # Static assets
├── src/
│   ├── pages/          # Page components
│   │   ├── ChatPage.jsx
│   │   ├── ElementsPage.jsx
│   │   └── DownloadPage.jsx
│   ├── App.jsx         # Main app component with routing
│   ├── App.css         # App styles
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles
├── index.html          # HTML template
├── vite.config.js      # Vite configuration
└── package.json        # Dependencies
```

## Theme

The application uses a custom color scheme:
- Primary Color: RGB(218, 32, 32)
- Background: White

## Technologies Used

- React 18
- React Router DOM
- Vite
- CSS3
