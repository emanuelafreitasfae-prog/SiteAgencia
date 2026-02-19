# Andre Dev - Agency Website PRD

## Original Problem Statement
Criar um site para uma agência de desenvolvimento de websites e aplicações para Android e iOS chamada "Andre Dev" com:
- Página principal com Hero, Serviços, Portfolio, Testemunhos, Contacto
- Área de cliente com login/registo
- **Área de administração** para gerir contactos, utilizadores, projetos e mensagens
- Estilo moderno e minimalista em tons de azul

## Architecture
- **Frontend**: React 19 + TailwindCSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Auth**: JWT-based authentication with role-based access (admin/client)

## User Personas
1. **Potential Client**: Visits landing page, views services/portfolio, submits contact form
2. **Registered Client**: Logs in, creates projects, sends messages, tracks project status
3. **Administrator**: Manages contacts, users, projects, responds to messages

## Core Requirements
- [x] Landing page with Hero, Services, Portfolio, Testimonials, Contact sections
- [x] User registration and login (JWT auth)
- [x] Client dashboard with stats overview
- [x] Project management (create, view projects)
- [x] Messaging system (send messages to agency)
- [x] Contact form for visitors
- [x] Responsive design (mobile + desktop)
- [x] **Admin setup page (/admin-setup)**
- [x] **Admin dashboard with statistics**
- [x] **Admin contact management (view/delete)**
- [x] **Admin user management (view/delete)**
- [x] **Admin project management (view/update status)**
- [x] **Admin message management (view/reply)**
- [x] **Role-based access control**

## What's Been Implemented (December 2024)
1. **Landing Page**: Complete with all sections, navigation, contact form
2. **Authentication**: Register, login, protected routes, role-based access
3. **Client Dashboard**: Stats cards, sidebar navigation, projects, messages
4. **Admin Panel**: Full admin functionality with:
   - Dashboard with statistics
   - Contact management
   - User management
   - Project status management
   - Message replies

## API Endpoints

### Public
- `POST /api/contact` - Submit contact form
- `GET /api/portfolio` - Get portfolio items

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Client (Protected)
- `POST/GET /api/projects` - Create/list projects
- `POST/GET /api/messages` - Create/list messages
- `GET /api/stats` - Get dashboard statistics

### Admin (Admin Only)
- `POST /api/admin/setup` - Create admin account (one-time)
- `GET /api/admin/check` - Check if admin exists
- `GET /api/admin/stats` - Get admin statistics
- `GET /api/admin/contacts` - List all contacts
- `DELETE /api/admin/contacts/{id}` - Delete contact
- `GET /api/admin/users` - List all users
- `DELETE /api/admin/users/{id}` - Delete user
- `GET /api/admin/projects` - List all projects
- `PUT /api/admin/projects/{id}/status` - Update project status
- `GET /api/admin/messages` - List all messages
- `PUT /api/admin/messages/{id}/reply` - Reply to message

## Prioritized Backlog

### P0 (Completed)
- [x] Landing page
- [x] Authentication system
- [x] Client Dashboard
- [x] Admin Panel

### P1 (Next)
- [ ] Email notifications on contact form
- [ ] Project file uploads
- [ ] Password reset functionality
- [ ] Admin can create client accounts

### P2 (Future)
- [ ] Invoice generation
- [ ] Payment integration (Stripe)
- [ ] Project timeline/milestones
- [ ] Real-time chat

## Next Tasks
1. Implement email notifications for contact form and message replies
2. Add project file upload functionality
3. Implement password reset
