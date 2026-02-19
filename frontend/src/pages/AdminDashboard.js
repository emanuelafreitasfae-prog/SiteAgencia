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
} from '@/components/ui/dialog';
import { toast } from 'sonner';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { 
  Code2, 
  LayoutDashboard, 
  FolderKanban, 
  MessageSquare, 
  Users,
  Mail,
  LogOut,
  Menu,
  X,
  Shield,
  Clock,
  CheckCircle2,
  AlertCircle,
  Trash2,
  Send,
  FileEdit,
  Euro,
  Check,
  Reply
} from 'lucide-react';
import ContentEditor from './ContentEditor';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Admin Sidebar Component
const AdminSidebar = ({ open, setOpen }) => {
  const location = useLocation();
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
    toast.success('Sessão terminada');
  };

  const navItems = [
    { path: '/admin', icon: LayoutDashboard, label: 'Dashboard', exact: true },
    { path: '/admin/content', icon: FileEdit, label: 'Editar Site' },
    { path: '/admin/contacts', icon: Mail, label: 'Contactos' },
    { path: '/admin/users', icon: Users, label: 'Utilizadores' },
    { path: '/admin/projects', icon: FolderKanban, label: 'Projetos' },
    { path: '/admin/messages', icon: MessageSquare, label: 'Mensagens' },
  ];

  return (
    <>
      {open && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      <aside className={`
        fixed top-0 left-0 h-full w-64 bg-gradient-to-b from-secondary to-primary z-50
        transform transition-transform duration-200 ease-in-out
        ${open ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static
      `}>
        <div className="flex flex-col h-full">
          <div className="p-6 flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                <Code2 className="w-6 h-6 text-secondary" />
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

          <div className="px-6 py-4 border-t border-white/10">
            <div className="flex items-center gap-2 mb-1">
              <Shield className="w-4 h-4 text-white/80" />
              <span className="text-white/80 text-sm font-medium">Administrador</span>
            </div>
            <p className="text-white font-medium truncate">{user?.name}</p>
            <p className="text-white/60 text-sm truncate">{user?.email}</p>
          </div>

          <nav className="flex-1 px-4 py-6 space-y-2">
            {navItems.map((item) => {
              const isActive = item.exact 
                ? location.pathname === item.path
                : location.pathname.startsWith(item.path);
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                    ${isActive 
                      ? 'bg-white/20 text-white' 
                      : 'text-white/70 hover:bg-white/10 hover:text-white'
                    }
                  `}
                  data-testid={`admin-nav-${item.label.toLowerCase()}`}
                  onClick={() => setOpen(false)}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="p-4 border-t border-white/10">
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-4 py-3 rounded-lg w-full text-white/70 hover:bg-white/10 hover:text-white transition-colors"
              data-testid="admin-logout-btn"
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

// Admin Dashboard Overview
const AdminOverview = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const { getAuthHeaders } = useAuth();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API}/admin/stats`, {
          headers: getAuthHeaders()
        });
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching stats:', error);
        toast.error('Erro ao carregar estatísticas');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, [getAuthHeaders]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-secondary"></div>
      </div>
    );
  }

  const statCards = [
    { label: 'Utilizadores', value: stats?.total_users || 0, icon: Users, color: 'bg-blue-500' },
    { label: 'Contactos', value: stats?.total_contacts || 0, icon: Mail, color: 'bg-green-500' },
    { label: 'Projetos', value: stats?.total_projects || 0, icon: FolderKanban, color: 'bg-purple-500' },
    { label: 'Mensagens', value: stats?.total_messages || 0, icon: MessageSquare, color: 'bg-orange-500' },
  ];

  const projectStats = [
    { label: 'Pendentes', value: stats?.pending_projects || 0, icon: Clock, color: 'text-yellow-600' },
    { label: 'Em Progresso', value: stats?.in_progress_projects || 0, icon: AlertCircle, color: 'text-blue-600' },
    { label: 'Concluídos', value: stats?.completed_projects || 0, icon: CheckCircle2, color: 'text-green-600' },
  ];

  return (
    <div data-testid="admin-dashboard">
      <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-primary mb-4 sm:mb-6 md:mb-8">Painel de Administração</h1>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 md:gap-6 mb-4 sm:mb-6 md:mb-8">
        {statCards.map((stat, index) => (
          <div 
            key={index}
            className="bg-white border border-border p-3 sm:p-4 md:p-6 rounded-xl shadow-sm"
            data-testid={`admin-stat-${index}`}
          >
            <div className={`w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-12 ${stat.color} rounded-lg flex items-center justify-center mb-2 sm:mb-4`}>
              <stat.icon className="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6 text-white" />
            </div>
            <p className="text-xl sm:text-2xl md:text-3xl font-bold text-primary">{stat.value}</p>
            <p className="text-muted-foreground text-xs sm:text-sm truncate">{stat.label}</p>
          </div>
        ))}
      </div>

      <div className="bg-white border border-border p-4 sm:p-6 rounded-xl shadow-sm">
        <h2 className="text-base sm:text-lg font-semibold text-primary mb-3 sm:mb-4">Estado dos Projetos</h2>
        <div className="grid grid-cols-3 gap-2 sm:gap-4">
          {projectStats.map((stat, index) => (
            <div key={index} className="text-center p-2 sm:p-4 bg-muted rounded-lg">
              <stat.icon className={`w-5 h-5 sm:w-6 sm:h-6 md:w-8 md:h-8 mx-auto mb-1 sm:mb-2 ${stat.color}`} />
              <p className="text-lg sm:text-xl md:text-2xl font-bold text-primary">{stat.value}</p>
              <p className="text-xs sm:text-sm text-muted-foreground">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Contacts Management
const AdminContacts = () => {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const { getAuthHeaders } = useAuth();

  const fetchContacts = async () => {
    try {
      const response = await axios.get(`${API}/admin/contacts`, {
        headers: getAuthHeaders()
      });
      setContacts(response.data);
    } catch (error) {
      console.error('Error fetching contacts:', error);
      toast.error('Erro ao carregar contactos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContacts();
  }, []);

  const handleDelete = async (contactId) => {
    if (!window.confirm('Tem certeza que deseja eliminar este contacto?')) return;
    
    try {
      await axios.delete(`${API}/admin/contacts/${contactId}`, {
        headers: getAuthHeaders()
      });
      toast.success('Contacto eliminado');
      fetchContacts();
    } catch (error) {
      toast.error('Erro ao eliminar contacto');
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
    <div data-testid="admin-contacts-page">
      <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-primary mb-4 sm:mb-6 md:mb-8">Contactos</h1>
      
      {contacts.length === 0 ? (
        <div className="bg-white border border-border rounded-xl p-6 sm:p-8 md:p-12 text-center">
          <Mail className="w-10 h-10 sm:w-12 sm:h-12 text-muted-foreground mx-auto mb-3 sm:mb-4" />
          <h3 className="text-base sm:text-lg font-semibold text-primary mb-2">Sem contactos</h3>
          <p className="text-sm sm:text-base text-muted-foreground">Os contactos do formulário aparecerão aqui.</p>
        </div>
      ) : (
        <div className="space-y-3 sm:space-y-4">
          {contacts.map((contact) => (
            <div 
              key={contact.id}
              className="bg-white border border-border p-4 sm:p-6 rounded-xl shadow-sm"
              data-testid={`contact-${contact.id}`}
            >
              <div className="flex justify-between items-start gap-2 sm:gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 sm:gap-3 mb-1 sm:mb-2">
                    <h3 className="text-base sm:text-lg font-semibold text-primary truncate">{contact.name}</h3>
                    <span className="text-xs text-muted-foreground">
                      {new Date(contact.created_at).toLocaleDateString('pt-PT')}
                    </span>
                  </div>
                  <p className="text-xs sm:text-sm text-secondary mb-1 truncate">{contact.email}</p>
                  {contact.phone && (
                    <p className="text-xs sm:text-sm text-muted-foreground mb-2">{contact.phone}</p>
                  )}
                  <p className="text-sm sm:text-base text-foreground mt-2 sm:mt-3">{contact.message}</p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDelete(contact.id)}
                  className="text-destructive hover:text-destructive hover:bg-destructive/10 flex-shrink-0"
                  data-testid={`delete-contact-${contact.id}`}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Users Management
const AdminUsers = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const { getAuthHeaders } = useAuth();

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/admin/users`, {
        headers: getAuthHeaders()
      });
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
      toast.error('Erro ao carregar utilizadores');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleDelete = async (userId) => {
    if (!window.confirm('Tem certeza que deseja eliminar este utilizador? Todos os projetos e mensagens serão eliminados.')) return;
    
    try {
      await axios.delete(`${API}/admin/users/${userId}`, {
        headers: getAuthHeaders()
      });
      toast.success('Utilizador eliminado');
      fetchUsers();
    } catch (error) {
      toast.error('Erro ao eliminar utilizador');
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
    <div data-testid="admin-users-page">
      <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-primary mb-4 sm:mb-6 md:mb-8">Utilizadores</h1>
      
      {users.length === 0 ? (
        <div className="bg-white border border-border rounded-xl p-6 sm:p-8 md:p-12 text-center">
          <Users className="w-10 h-10 sm:w-12 sm:h-12 text-muted-foreground mx-auto mb-3 sm:mb-4" />
          <h3 className="text-base sm:text-lg font-semibold text-primary mb-2">Sem utilizadores</h3>
          <p className="text-sm sm:text-base text-muted-foreground">Os utilizadores registados aparecerão aqui.</p>
        </div>
      ) : (
        <>
          {/* Mobile Cards */}
          <div className="lg:hidden space-y-3">
            {users.map((user) => (
              <div key={user.id} className="bg-white border border-border p-4 rounded-xl" data-testid={`user-card-${user.id}`}>
                <div className="flex justify-between items-start mb-2">
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-primary truncate">{user.name}</p>
                    <p className="text-sm text-muted-foreground truncate">{user.email}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(user.id)}
                    className="text-destructive hover:text-destructive hover:bg-destructive/10 flex-shrink-0"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>{user.company || 'Sem empresa'}</span>
                  <span>{new Date(user.created_at).toLocaleDateString('pt-PT')}</span>
                </div>
              </div>
            ))}
          </div>
          
          {/* Desktop Table */}
          <div className="hidden lg:block bg-white border border-border rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-muted">
                  <tr>
                    <th className="text-left p-4 font-medium text-primary">Nome</th>
                    <th className="text-left p-4 font-medium text-primary">Email</th>
                    <th className="text-left p-4 font-medium text-primary">Empresa</th>
                    <th className="text-left p-4 font-medium text-primary">Data</th>
                    <th className="text-right p-4 font-medium text-primary">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className="border-t border-border" data-testid={`user-row-${user.id}`}>
                      <td className="p-4">{user.name}</td>
                      <td className="p-4 text-muted-foreground">{user.email}</td>
                      <td className="p-4 text-muted-foreground">{user.company || '-'}</td>
                      <td className="p-4 text-muted-foreground text-sm">
                        {new Date(user.created_at).toLocaleDateString('pt-PT')}
                      </td>
                      <td className="p-4 text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(user.id)}
                          className="text-destructive hover:text-destructive hover:bg-destructive/10"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

// Projects Management
const AdminProjects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const { getAuthHeaders } = useAuth();

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/admin/projects`, {
        headers: getAuthHeaders()
      });
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
      toast.error('Erro ao carregar projetos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleStatusChange = async (projectId, newStatus) => {
    try {
      await axios.put(`${API}/admin/projects/${projectId}/status?status=${newStatus}`, {}, {
        headers: getAuthHeaders()
      });
      toast.success('Estado atualizado');
      fetchProjects();
    } catch (error) {
      toast.error('Erro ao atualizar estado');
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-secondary"></div>
      </div>
    );
  }

  return (
    <div data-testid="admin-projects-page">
      <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-primary mb-4 sm:mb-6 md:mb-8">Projetos</h1>
      
      {projects.length === 0 ? (
        <div className="bg-white border border-border rounded-xl p-6 sm:p-8 md:p-12 text-center">
          <FolderKanban className="w-10 h-10 sm:w-12 sm:h-12 text-muted-foreground mx-auto mb-3 sm:mb-4" />
          <h3 className="text-base sm:text-lg font-semibold text-primary mb-2">Sem projetos</h3>
          <p className="text-sm sm:text-base text-muted-foreground">Os projetos dos clientes aparecerão aqui.</p>
        </div>
      ) : (
        <div className="space-y-3 sm:space-y-4">
          {projects.map((project) => {
            const statusBadge = getStatusBadge(project.status);
            return (
              <div 
                key={project.id}
                className="bg-white border border-border p-4 sm:p-6 rounded-xl shadow-sm"
                data-testid={`admin-project-${project.id}`}
              >
                <div className="flex flex-col gap-3 sm:gap-4">
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2 sm:gap-3 mb-1 sm:mb-2">
                      <h3 className="text-base sm:text-lg font-semibold text-primary">{project.name}</h3>
                      <span className={`text-xs px-2 py-0.5 sm:py-1 rounded-full ${statusBadge.class}`}>
                        {statusBadge.label}
                      </span>
                    </div>
                    <p className="text-muted-foreground text-xs sm:text-sm mb-2 sm:mb-3">{project.description}</p>
                    {project.user && (
                      <p className="text-xs sm:text-sm">
                        <span className="text-muted-foreground">Cliente: </span>
                        <span className="text-secondary">{project.user.name}</span>
                        <span className="text-muted-foreground hidden sm:inline"> ({project.user.email})</span>
                      </p>
                    )}
                  </div>
                  <div className="flex items-center">
                    <Select
                      value={project.status}
                      onValueChange={(value) => handleStatusChange(project.id, value)}
                    >
                      <SelectTrigger className="w-full sm:w-40" data-testid={`status-select-${project.id}`}>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pending">Pendente</SelectItem>
                        <SelectItem value="in_progress">Em Progresso</SelectItem>
                        <SelectItem value="completed">Concluído</SelectItem>
                      </SelectContent>
                    </Select>
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

// Messages Management
const AdminMessages = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [replyText, setReplyText] = useState('');
  const [replying, setReplying] = useState(false);
  const { getAuthHeaders } = useAuth();

  const fetchMessages = async () => {
    try {
      const response = await axios.get(`${API}/admin/messages`, {
        headers: getAuthHeaders()
      });
      setMessages(response.data);
    } catch (error) {
      console.error('Error fetching messages:', error);
      toast.error('Erro ao carregar mensagens');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMessages();
  }, []);

  const handleReply = async () => {
    if (!replyText.trim()) {
      toast.error('Escreva uma resposta');
      return;
    }

    setReplying(true);
    try {
      await axios.put(`${API}/admin/messages/${selectedMessage.id}/reply?reply=${encodeURIComponent(replyText)}`, {}, {
        headers: getAuthHeaders()
      });
      toast.success('Resposta enviada');
      setSelectedMessage(null);
      setReplyText('');
      fetchMessages();
    } catch (error) {
      toast.error('Erro ao enviar resposta');
    } finally {
      setReplying(false);
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
    <div data-testid="admin-messages-page">
      <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-primary mb-4 sm:mb-6 md:mb-8">Mensagens</h1>
      
      {messages.length === 0 ? (
        <div className="bg-white border border-border rounded-xl p-6 sm:p-8 md:p-12 text-center">
          <MessageSquare className="w-10 h-10 sm:w-12 sm:h-12 text-muted-foreground mx-auto mb-3 sm:mb-4" />
          <h3 className="text-base sm:text-lg font-semibold text-primary mb-2">Sem mensagens</h3>
          <p className="text-sm sm:text-base text-muted-foreground">As mensagens dos clientes aparecerão aqui.</p>
        </div>
      ) : (
        <div className="space-y-3 sm:space-y-4">
          {messages.map((message) => (
            <div 
              key={message.id}
              className={`bg-white border p-4 sm:p-6 rounded-xl shadow-sm ${!message.is_read ? 'border-secondary' : 'border-border'}`}
              data-testid={`admin-message-${message.id}`}
            >
              <div className="flex flex-col sm:flex-row justify-between items-start gap-2 sm:gap-4 mb-2 sm:mb-3">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                    <h3 className="font-semibold text-primary text-sm sm:text-base">{message.subject}</h3>
                    {!message.is_read && (
                      <span className="text-xs bg-secondary text-white px-2 py-0.5 rounded-full">Novo</span>
                    )}
                  </div>
                  {message.user && (
                    <p className="text-xs sm:text-sm text-muted-foreground mt-1 truncate">
                      De: {message.user.name} <span className="hidden sm:inline">({message.user.email})</span>
                    </p>
                  )}
                </div>
                <span className="text-xs text-muted-foreground whitespace-nowrap">
                  {new Date(message.created_at).toLocaleDateString('pt-PT')}
                </span>
              </div>
              <p className="text-sm sm:text-base text-foreground mb-3 sm:mb-4">{message.content}</p>
              
              {message.admin_reply ? (
                <div className="bg-muted p-3 sm:p-4 rounded-lg">
                  <p className="text-xs text-secondary font-medium mb-1">Sua resposta:</p>
                  <p className="text-xs sm:text-sm text-foreground">{message.admin_reply}</p>
                </div>
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedMessage(message)}
                  data-testid={`reply-btn-${message.id}`}
                  className="w-full sm:w-auto"
                >
                  <Send className="w-4 h-4 mr-2" />
                  Responder
                </Button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Reply Dialog */}
      <Dialog open={!!selectedMessage} onOpenChange={() => setSelectedMessage(null)}>
        <DialogContent aria-describedby="reply-description" className="max-w-[95vw] sm:max-w-lg mx-auto">
          <DialogHeader>
            <DialogTitle className="text-base sm:text-lg">Responder a: {selectedMessage?.subject}</DialogTitle>
            <p id="reply-description" className="text-xs sm:text-sm text-muted-foreground truncate">
              {selectedMessage?.user?.name} ({selectedMessage?.user?.email})
            </p>
          </DialogHeader>
          <div className="space-y-3 sm:space-y-4 mt-3 sm:mt-4">
            <div className="bg-muted p-3 rounded-lg text-xs sm:text-sm">
              <p className="text-muted-foreground mb-1">Mensagem original:</p>
              <p>{selectedMessage?.content}</p>
            </div>
            <Textarea
              value={replyText}
              onChange={(e) => setReplyText(e.target.value)}
              placeholder="Escreva a sua resposta..."
              rows={4}
              className="min-h-[100px]"
              data-testid="reply-textarea"
            />
            <Button 
              onClick={handleReply} 
              disabled={replying}
              className="w-full bg-secondary hover:bg-secondary/90"
              data-testid="send-reply-btn"
            >
              {replying ? 'A enviar...' : 'Enviar Resposta'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Main Admin Dashboard Layout
export default function AdminDashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, isAdmin } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user && !isAdmin()) {
      navigate('/dashboard');
    }
  }, [user, isAdmin, navigate]);

  return (
    <div className="min-h-screen bg-muted flex" data-testid="admin-panel">
      <AdminSidebar open={sidebarOpen} setOpen={setSidebarOpen} />
      
      <main className="flex-1 min-h-screen overflow-x-hidden">
        <header className="lg:hidden bg-white border-b border-border p-3 sm:p-4 flex items-center justify-between">
          <button 
            onClick={() => setSidebarOpen(true)}
            className="p-2"
            data-testid="admin-mobile-sidebar-btn"
          >
            <Menu className="w-5 h-5 sm:w-6 sm:h-6" />
          </button>
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 sm:w-5 sm:h-5 text-secondary" />
            <span className="font-sans font-bold text-base sm:text-lg text-primary">Admin</span>
          </div>
          <div className="w-9 sm:w-10"></div>
        </header>

        <div className="p-4 sm:p-6 lg:p-12">
          <Routes>
            <Route index element={<AdminOverview />} />
            <Route path="content" element={<ContentEditor />} />
            <Route path="contacts" element={<AdminContacts />} />
            <Route path="users" element={<AdminUsers />} />
            <Route path="projects" element={<AdminProjects />} />
            <Route path="messages" element={<AdminMessages />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}
