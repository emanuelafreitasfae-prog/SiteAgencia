# Andre Dev - Agency Website PRD

## Original Problem Statement
Criar um site para uma agência de desenvolvimento de websites e aplicações para Android e iOS chamada "Andre Dev" com:
- Página principal com Hero, Serviços, Portfolio, Testemunhos, Contacto
- Área de cliente com login/registo
- Estilo moderno e minimalista em tons de azul

## Architecture
- **Frontend**: React 19 + TailwindCSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Auth**: JWT-based authentication

## User Personas
1. **Potential Client**: Visits landing page, views services/portfolio, submits contact form
2. **Registered Client**: Logs in, creates projects, sends messages, tracks project status

## Core Requirements
- [x] Landing page with Hero, Services, Portfolio, Testimonials, Contact sections
- [x] User registration and login (JWT auth)
- [x] Client dashboard with stats overview
- [x] Project management (create, view projects)
- [x] Messaging system (send messages to agency)
- [x] Contact form for visitors
- [x] Responsive design (mobile + desktop)

## What's Been Implemented (December 2024)
1. **Landing Page**: Complete with all sections, navigation, contact form
2. **Authentication**: Register, login, protected routes
3. **Dashboard**: Stats cards, sidebar navigation
4. **Projects**: Create and list projects
5. **Messages**: Send and view messages
6. **Settings**: View account information

## API Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/contact` - Submit contact form (public)
- `GET /api/portfolio` - Get portfolio items (public)
- `POST/GET /api/projects` - Create/list projects
- `POST/GET /api/messages` - Create/list messages
- `GET /api/stats` - Get dashboard statistics

## Prioritized Backlog

### P0 (Completed)
- [x] Landing page
- [x] Authentication system
- [x] Dashboard
- [x] Projects management
- [x] Messaging

### P1 (Next)
- [ ] Email notifications on contact form
- [ ] Project file uploads
- [ ] Admin panel for agency
- [ ] Password reset functionality

### P2 (Future)
- [ ] Invoice generation
- [ ] Payment integration (Stripe)
- [ ] Project timeline/milestones
- [ ] Real-time chat

## Next Tasks
1. Implement email notifications for contact form submissions
2. Add admin panel for managing projects/contacts
3. Implement password reset functionality
