# Loan Underwriting AI - Frontend

React-based frontend for the Loan Underwriting AI application with Vite as the build tool.

## Features

### User Portal
- **Loan Application**: Submit new loan applications
- **Document Upload**: Upload PAN cards and salary slips
- **Application Tracking**: View status of submitted applications
- **Decision Results**: See loan approval/rejection decisions with reasoning

### Admin Portal
- **Dashboard**: Overview of applications statistics
- **Application Review**: Review and manage loan applications
- **Document Viewer**: View uploaded documents
- **Credit Assessment**: View credit scores and risk analysis
- **Agent Tracing**: See detailed workflow of AI agents
- **Decision Making**: Approve or reject applications with notes

## Technology Stack

- **React 18.2**: UI framework
- **React Router 6**: Client-side routing
- **Vite 5**: Build tool
- **Vanilla CSS**: Styling

## Installation

```bash
cd frontend
npm install
```

## Development

```bash
npm run dev
```

Opens at `http://localhost:3000`

## Build

```bash
npm run build
```

Generates optimized production build in `dist/` folder.

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── admin/          # Admin components
│   │   ├── shared/         # Shared components
│   │   └── user/           # User components
│   ├── pages/
│   │   ├── admin/          # Admin pages
│   │   └── user/           # User pages
│   ├── services/           # API services
│   ├── context/            # Auth context providers
│   ├── App.jsx            # Main app component with routing
│   ├── main.jsx           # Entry point
│   └── index.css          # Global styles
├── package.json
├── vite.config.js
└── .gitignore
```

## API Integration

Frontend communicates with backend at `http://localhost:8000/api`

### Authentication
- User login: POST `/auth/user/login`
- Admin login: POST `/auth/admin/login`
- Tokens stored in localStorage

### User Endpoints
- Submit application: POST `/user/applications`
- Get applications: GET `/user/applications`
- Upload documents: POST `/user/applications/{id}/upload`

### Admin Endpoints
- Get applications: GET `/admin/applications`
- Get application detail: GET `/admin/applications/{id}`
- Approve: POST `/admin/applications/{id}/approve`
- Reject: POST `/admin/applications/{id}/reject`
- Get trace: GET `/admin/applications/{id}/trace`
- Get credit report: GET `/admin/applications/{id}/credit-report`

## Environment Variables

Create `.env` file:
```
VITE_API_URL=http://localhost:8000/api
```

## Styling

Global styles in `src/index.css` with:
- CSS Grid for layouts
- Flexbox for components
- CSS Variables support (can be added)
- Responsive design
