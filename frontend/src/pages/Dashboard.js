import { useState, useEffect } from 'react';
import { Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { toast } from 'sonner';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { 
  Code2, 
  LayoutDashboard, 
  FolderKanban, 
  MessageSquare, 
  Settings, 
  LogOut,
  Plus,
  Clock,
  CheckCircle2,
  AlertCircle,
  Menu,
  X,
  Send,
  Euro
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Sidebar Component
const Sidebar = ({ open, setOpen }) => {
  const location = useLocation();
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
    toast.success('Sessão terminada');
  };

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/dashboard/projects', icon: FolderKanban, label: 'Projetos' },
    { path: '/dashboard/messages', icon: MessageSquare, label: 'Mensagens' },
    { path: '/dashboard/settings', icon: Settings, label: 'Definições' },
  ];

  return (
    <>
      {/* Mobile Overlay */}
      {open && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 h-full w-64 bg-primary z-50
        transform transition-transform duration-200 ease-in-out
        ${open ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-6 flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                <Code2 className="w-6 h-6 text-primary" />
              </div>
              <span className="font-sans font-bold text-xl text-white">Andre Dev</span>
            </Link>
            <button 
              className="lg:hidden text-white"
              onClick={() => setOpen(false)}
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* User Info */}
          <div className="px-6 py-4 border-t border-white/10">
            <p className="text-white font-medium truncate">{user?.name}</p>
            <p className="text-white/60 text-sm truncate">{user?.email}</p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path || 
                (item.path !== '/dashboard' && location.pathname.startsWith(item.path));
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                    ${isActive 
                      ? 'bg-white/10 text-white' 
                      : 'text-white/60 hover:bg-white/5 hover:text-white'
                    }
                  `}
                  data-testid={`nav-${item.label.toLowerCase()}`}
                  onClick={() => setOpen(false)}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Logout */}
          <div className="p-4 border-t border-white/10">
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-4 py-3 rounded-lg w-full text-white/60 hover:bg-white/5 hover:text-white transition-colors"
              data-testid="logout-btn"
            >
              <LogOut className="w-5 h-5" />
              <span className="font-medium">Terminar sessão</span>
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};

// Dashboard Overview
const DashboardOverview = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const { getAuthHeaders } = useAuth();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API}/stats`, {
          headers: getAuthHeaders()
        });
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [getAuthHeaders]);

  const statCards = [
    { label: 'Total de Projetos', value: stats?.total_projects || 0, icon: FolderKanban, color: 'bg-secondary' },
    { label: 'Pendentes', value: stats?.pending || 0, icon: Clock, color: 'bg-yellow-500' },
    { label: 'Em Progresso', value: stats?.in_progress || 0, icon: AlertCircle, color: 'bg-blue-500' },
    { label: 'Concluídos', value: stats?.completed || 0, icon: CheckCircle2, color: 'bg-green-500' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-secondary"></div>
      </div>
    );
  }

  return (
    <div data-testid="dashboard-overview">
      <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-primary mb-4 sm:mb-6 md:mb-8">Dashboard</h1>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 md:gap-6 mb-4 sm:mb-6 md:mb-8">
        {statCards.map((stat, index) => (
          <div 
            key={index}
            className="bg-white border border-border p-3 sm:p-4 md:p-6 rounded-xl shadow-sm"
            data-testid={`stat-card-${index}`}
          >
            <div className="flex items-center justify-between mb-2 sm:mb-4">
              <div className={`w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-12 ${stat.color} rounded-lg flex items-center justify-center`}>
                <stat.icon className="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6 text-white" />
              </div>
            </div>
            <p className="text-xl sm:text-2xl md:text-3xl font-bold text-primary">{stat.value}</p>
            <p className="text-muted-foreground text-xs sm:text-sm truncate">{stat.label}</p>
          </div>
        ))}
      </div>

      <div className="bg-white border border-border p-4 sm:p-6 rounded-xl shadow-sm">
        <h2 className="text-base sm:text-lg font-semibold text-primary mb-3 sm:mb-4">Ações Rápidas</h2>
        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
          <Link to="/dashboard/projects" className="w-full sm:w-auto">
            <Button className="bg-secondary hover:bg-secondary/90 w-full sm:w-auto">
              <Plus className="w-4 h-4 mr-2" />
              Novo Projeto
            </Button>
          </Link>
          <Link to="/dashboard/messages" className="w-full sm:w-auto">
            <Button variant="outline" className="w-full sm:w-auto">
              <MessageSquare className="w-4 h-4 mr-2" />
              Enviar Mensagem
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

// Projects Page
const ProjectsPage = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    project_type: 'web',
    budget: ''
  });
  const { getAuthHeaders } = useAuth();

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`, {
        headers: getAuthHeaders()
      });
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateProject = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/projects`, newProject, {
        headers: getAuthHeaders()
      });
      toast.success('Projeto criado com sucesso!');
      setDialogOpen(false);
      setNewProject({ name: '', description: '', project_type: 'web', budget: '' });
      fetchProjects();
    } catch (error) {
      toast.error('Erro ao criar projeto');
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: { label: 'Pendente', class: 'bg-yellow-100 text-yellow-700' },
      in_progress: { label: 'Em Progresso', class: 'bg-blue-100 text-blue-700' },
      completed: { label: 'Concluído', class: 'bg-green-100 text-green-700' }
    };
    return badges[status] || badges.pending;
  };

  const getBudgetStatusBadge = (budgetStatus) => {
    const badges = {
      pending: { label: 'Orçamento Pendente', class: 'bg-orange-100 text-orange-700' },
      accepted: { label: 'Orçamento Aceite', class: 'bg-green-100 text-green-700' },
      counter_proposal: { label: 'Contraproposta', class: 'bg-purple-100 text-purple-700' }
    };
    return badges[budgetStatus] || badges.pending;
  };

  const getTypeBadge = (type) => {
    const types = {
      web: 'Website',
      android: 'Android',
      ios: 'iOS',
      hybrid: 'Híbrido'
    };
    return types[type] || type;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-secondary"></div>
      </div>
    );
  }

  return (
    <div data-testid="projects-page">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-4 mb-4 sm:mb-6 md:mb-8">
        <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-primary">Projetos</h1>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-secondary hover:bg-secondary/90 w-full sm:w-auto" data-testid="new-project-btn">
              <Plus className="w-4 h-4 mr-2" />
              Novo Projeto
            </Button>
          </DialogTrigger>
          <DialogContent aria-describedby="new-project-description" className="max-w-[95vw] sm:max-w-lg mx-auto">
            <DialogHeader>
              <DialogTitle>Criar Novo Projeto</DialogTitle>
              <p id="new-project-description" className="text-sm text-muted-foreground">
                Preencha os dados do seu novo projeto
              </p>
            </DialogHeader>
            <form onSubmit={handleCreateProject} className="space-y-4 mt-4">
              <div>
                <label className="block text-sm font-medium mb-2">Nome do Projeto</label>
                <Input 
                  value={newProject.name}
                  onChange={(e) => setNewProject({...newProject, name: e.target.value})}
                  placeholder="Ex: Website E-commerce"
                  required
                  data-testid="project-name-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Tipo</label>
                <Select 
                  value={newProject.project_type}
                  onValueChange={(value) => setNewProject({...newProject, project_type: value})}
                >
                  <SelectTrigger data-testid="project-type-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="web">Website</SelectItem>
                    <SelectItem value="android">Aplicação Android</SelectItem>
                    <SelectItem value="ios">Aplicação iOS</SelectItem>
                    <SelectItem value="hybrid">Aplicação Híbrida</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Descrição</label>
                <Textarea 
                  value={newProject.description}
                  onChange={(e) => setNewProject({...newProject, description: e.target.value})}
                  placeholder="Descreva o seu projeto..."
                  rows={3}
                  required
                  data-testid="project-description-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Orçamento Proposto *</label>
                <Input 
                  value={newProject.budget}
                  onChange={(e) => setNewProject({...newProject, budget: e.target.value})}
                  placeholder="Ex: 5000€"
                  required
                  data-testid="project-budget-input"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  O orçamento será analisado pelo administrador
                </p>
              </div>
              <Button type="submit" className="w-full bg-primary" data-testid="create-project-btn">
                Criar Projeto
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {projects.length === 0 ? (
        <div className="bg-white border border-border rounded-xl p-6 sm:p-8 md:p-12 text-center">
          <FolderKanban className="w-10 h-10 sm:w-12 sm:h-12 text-muted-foreground mx-auto mb-3 sm:mb-4" />
          <h3 className="text-base sm:text-lg font-semibold text-primary mb-2">Sem projetos</h3>
          <p className="text-sm sm:text-base text-muted-foreground mb-4">Crie o seu primeiro projeto para começar.</p>
        </div>
      ) : (
        <div className="grid gap-3 sm:gap-4">
          {projects.map((project) => {
            const statusBadge = getStatusBadge(project.status);
            const budgetBadge = getBudgetStatusBadge(project.budget_status);
            return (
              <div 
                key={project.id}
                className="bg-white border border-border p-4 sm:p-6 rounded-xl shadow-sm hover:border-secondary/50 transition-colors"
                data-testid={`project-card-${project.id}`}
              >
                <div className="flex flex-col gap-3 sm:gap-4">
                  <div>
                    <div className="flex flex-wrap items-center gap-2 sm:gap-3 mb-2">
                      <h3 className="text-base sm:text-lg font-semibold text-primary">{project.name}</h3>
                      <span className={`text-xs px-2 py-0.5 sm:py-1 rounded-full ${statusBadge.class}`}>
                        {statusBadge.label}
                      </span>
                    </div>
                    <p className="text-muted-foreground text-xs sm:text-sm mb-2 sm:mb-3">{project.description}</p>
                    <div className="flex flex-wrap gap-1.5 sm:gap-2 mb-3">
                      <span className="text-xs bg-muted px-2 py-1 rounded text-muted-foreground">
                        {getTypeBadge(project.project_type)}
                      </span>
                    </div>
                    
                    {/* Budget Section */}
                    <div className="bg-muted/50 rounded-lg p-3 sm:p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Euro className="w-4 h-4 text-secondary" />
                        <span className="text-sm font-medium text-primary">Orçamento</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ml-auto ${budgetBadge.class}`}>
                          {budgetBadge.label}
                        </span>
                      </div>
                      <div className="space-y-1">
                        <p className="text-sm">
                          <span className="text-muted-foreground">Proposto: </span>
                          <span className="font-medium text-primary">{project.budget}</span>
                        </p>
                        {project.budget_status === 'counter_proposal' && project.counter_proposal && (
                          <p className="text-sm">
                            <span className="text-muted-foreground">Contraproposta: </span>
                            <span className="font-medium text-purple-700">{project.counter_proposal}</span>
                          </p>
                        )}
                        {project.admin_notes && (
                          <p className="text-xs text-muted-foreground mt-2 italic">
                            Nota: {project.admin_notes}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="text-xs sm:text-sm text-muted-foreground">
                    Criado em {new Date(project.created_at).toLocaleDateString('pt-PT')}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

// Messages Page
const MessagesPage = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newMessage, setNewMessage] = useState({ subject: '', content: '' });
  const [sending, setSending] = useState(false);
  const { getAuthHeaders } = useAuth();

  const fetchMessages = async () => {
    try {
      const response = await axios.get(`${API}/messages`, {
        headers: getAuthHeaders()
      });
      setMessages(response.data);
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMessages();
  }, []);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    setSending(true);
    try {
      await axios.post(`${API}/messages`, newMessage, {
        headers: getAuthHeaders()
      });
      toast.success('Mensagem enviada com sucesso!');
      setNewMessage({ subject: '', content: '' });
      fetchMessages();
    } catch (error) {
      toast.error('Erro ao enviar mensagem');
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-secondary"></div>
      </div>
    );
  }

  return (
    <div data-testid="messages-page">
      <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-primary mb-4 sm:mb-6 md:mb-8">Mensagens</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 md:gap-8">
        {/* New Message Form */}
        <div className="bg-white border border-border p-4 sm:p-6 rounded-xl shadow-sm">
          <h2 className="text-base sm:text-lg font-semibold text-primary mb-3 sm:mb-4">Nova Mensagem</h2>
          <form onSubmit={handleSendMessage} className="space-y-3 sm:space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Assunto</label>
              <Input 
                value={newMessage.subject}
                onChange={(e) => setNewMessage({...newMessage, subject: e.target.value})}
                placeholder="Assunto da mensagem"
                required
                data-testid="message-subject-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Mensagem</label>
              <Textarea 
                value={newMessage.content}
                onChange={(e) => setNewMessage({...newMessage, content: e.target.value})}
                placeholder="Escreva a sua mensagem..."
                rows={4}
                required
                className="min-h-[100px] sm:min-h-[120px]"
                data-testid="message-content-input"
              />
            </div>
            <Button 
              type="submit" 
              disabled={sending}
              className="w-full bg-secondary hover:bg-secondary/90"
              data-testid="send-message-btn"
            >
              <Send className="w-4 h-4 mr-2" />
              {sending ? 'A enviar...' : 'Enviar Mensagem'}
            </Button>
          </form>
        </div>

        {/* Messages List */}
        <div className="space-y-3 sm:space-y-4">
          <h2 className="text-base sm:text-lg font-semibold text-primary">Histórico</h2>
          {messages.length === 0 ? (
            <div className="bg-white border border-border rounded-xl p-6 sm:p-8 text-center">
              <MessageSquare className="w-8 h-8 sm:w-10 sm:h-10 text-muted-foreground mx-auto mb-2 sm:mb-3" />
              <p className="text-sm sm:text-base text-muted-foreground">Sem mensagens</p>
            </div>
          ) : (
            messages.map((message) => (
              <div 
                key={message.id}
                className="bg-white border border-border p-3 sm:p-4 rounded-xl shadow-sm"
                data-testid={`message-${message.id}`}
              >
                <div className="flex items-start justify-between gap-2 sm:gap-4 mb-2">
                  <h3 className="font-medium text-primary text-sm sm:text-base">{message.subject}</h3>
                  <span className="text-xs text-muted-foreground whitespace-nowrap">
                    {new Date(message.created_at).toLocaleDateString('pt-PT')}
                  </span>
                </div>
                <p className="text-xs sm:text-sm text-muted-foreground">{message.content}</p>
                {message.admin_reply && (
                  <div className="mt-2 sm:mt-3 pt-2 sm:pt-3 border-t border-border">
                    <p className="text-xs text-secondary font-medium mb-1">Resposta:</p>
                    <p className="text-xs sm:text-sm text-foreground">{message.admin_reply}</p>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

// Settings Page
const SettingsPage = () => {
  const { user } = useAuth();

  return (
    <div data-testid="settings-page">
      <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-primary mb-4 sm:mb-6 md:mb-8">Definições</h1>

      <div className="bg-white border border-border p-4 sm:p-6 rounded-xl shadow-sm max-w-lg">
        <h2 className="text-base sm:text-lg font-semibold text-primary mb-4 sm:mb-6">Informações da Conta</h2>
        
        <div className="space-y-3 sm:space-y-4">
          <div>
            <label className="block text-xs sm:text-sm font-medium text-muted-foreground mb-1">Nome</label>
            <p className="text-sm sm:text-base text-foreground">{user?.name}</p>
          </div>
          <div>
            <label className="block text-xs sm:text-sm font-medium text-muted-foreground mb-1">Email</label>
            <p className="text-sm sm:text-base text-foreground break-all">{user?.email}</p>
          </div>
          {user?.company && (
            <div>
              <label className="block text-xs sm:text-sm font-medium text-muted-foreground mb-1">Empresa</label>
              <p className="text-sm sm:text-base text-foreground">{user?.company}</p>
            </div>
          )}
          <div>
            <label className="block text-xs sm:text-sm font-medium text-muted-foreground mb-1">Membro desde</label>
            <p className="text-sm sm:text-base text-foreground">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString('pt-PT') : '-'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main Dashboard Layout
export default function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-muted flex" data-testid="dashboard">
      <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />
      
      <main className="flex-1 min-h-screen overflow-x-hidden">
        {/* Mobile Header */}
        <header className="lg:hidden bg-white border-b border-border p-3 sm:p-4 flex items-center justify-between">
          <button 
            onClick={() => setSidebarOpen(true)}
            className="p-2"
            data-testid="mobile-sidebar-btn"
          >
            <Menu className="w-5 h-5 sm:w-6 sm:h-6" />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 sm:w-8 sm:h-8 bg-primary rounded-lg flex items-center justify-center">
              <Code2 className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            </div>
            <span className="font-sans font-bold text-base sm:text-lg text-primary">Andre Dev</span>
          </div>
          <div className="w-9 sm:w-10"></div>
        </header>

        {/* Content */}
        <div className="p-4 sm:p-6 lg:p-12">
          <Routes>
            <Route index element={<DashboardOverview />} />
            <Route path="projects" element={<ProjectsPage />} />
            <Route path="messages" element={<MessagesPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}
