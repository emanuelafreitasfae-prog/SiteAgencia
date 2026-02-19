from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'andre-dev-secret-key-2024')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Create the main app
app = FastAPI(title="Andre Dev API")

# Create router with /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== MODELS ====================

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    company: Optional[str] = None

class AdminCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    email: str
    company: Optional[str] = None
    role: str = "client"  # client, admin
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ProjectCreate(BaseModel):
    name: str
    description: str
    project_type: str  # web, android, ios, hybrid
    status: str = "pending"  # pending, in_progress, completed
    budget: str  # Now required

class ProjectResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    name: str
    description: str
    project_type: str
    status: str
    budget: str
    budget_status: str = "pending"  # pending, accepted, counter_proposal
    counter_proposal: Optional[str] = None
    admin_notes: Optional[str] = None
    created_at: str
    updated_at: str

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_type: Optional[str] = None
    status: Optional[str] = None
    budget: Optional[str] = None

class BudgetResponse(BaseModel):
    budget_status: str  # accepted, counter_proposal
    counter_proposal: Optional[str] = None
    admin_notes: Optional[str] = None

class MessageCreate(BaseModel):
    subject: str
    content: str

class MessageResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    subject: str
    content: str
    is_read: bool
    admin_reply: Optional[str] = None
    created_at: str

class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: str
    service_type: Optional[str] = None

class ContactResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    message: str
    service_type: Optional[str] = None
    created_at: str

class PortfolioItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: str
    description: str
    image_url: str
    category: str
    technologies: List[str]
    link: Optional[str] = None

# ==================== CMS MODELS ====================

class HeroContent(BaseModel):
    tagline: str = "Agência de Desenvolvimento"
    title: str = "Criamos o seu"
    highlight: str = "futuro digital"
    description: str = "Desenvolvemos websites e aplicações móveis que transformam ideias em experiências digitais extraordinárias. Android, iOS e Web."
    cta_text: str = "Começar Projeto"
    stats: List[dict] = []

class ServiceItem(BaseModel):
    id: Optional[str] = None
    icon: str = "Monitor"
    title: str
    description: str
    features: List[str]

class PortfolioItemCreate(BaseModel):
    title: str
    description: str
    image_url: str
    category: str
    technologies: List[str]
    link: Optional[str] = None

class TestimonialItem(BaseModel):
    id: Optional[str] = None
    name: str
    role: str
    image: str
    text: str

class ContactInfo(BaseModel):
    email: str = "contacto@andredev.pt"
    phone: str = "+351 912 345 678"
    location: str = "Lisboa, Portugal"

class SiteContent(BaseModel):
    hero: Optional[HeroContent] = None
    services: Optional[List[ServiceItem]] = None
    portfolio: Optional[List[PortfolioItemCreate]] = None
    testimonials: Optional[List[TestimonialItem]] = None
    contact_info: Optional[ContactInfo] = None


# ==================== HELPERS ====================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)
    user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Utilizador não encontrado")
    return user

async def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return current_user


# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já registado")
    
    # Create user
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "name": user_data.name,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "company": user_data.company,
        "role": "client",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    
    # Create token
    token = create_token(user_id)
    
    user_response = UserResponse(
        id=user_id,
        name=user_data.name,
        email=user_data.email,
        company=user_data.company,
        role="client",
        created_at=user_doc["created_at"]
    )
    
    return TokenResponse(access_token=token, user=user_response)

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    token = create_token(user["id"])
    
    user_response = UserResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        company=user.get("company"),
        role=user.get("role", "client"),
        created_at=user["created_at"]
    )
    
    return TokenResponse(access_token=token, user=user_response)

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        name=current_user["name"],
        email=current_user["email"],
        company=current_user.get("company"),
        role=current_user.get("role", "client"),
        created_at=current_user["created_at"]
    )

@api_router.put("/auth/profile")
async def update_profile(
    name: Optional[str] = None,
    company: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    update_data = {}
    if name:
        update_data["name"] = name
    if company is not None:
        update_data["company"] = company
    
    if update_data:
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": update_data}
        )
    
    updated_user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "password": 0})
    return updated_user


# ==================== PROJECT ROUTES ====================

@api_router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_user)
):
    project_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    project_doc = {
        "id": project_id,
        "user_id": current_user["id"],
        "name": project_data.name,
        "description": project_data.description,
        "project_type": project_data.project_type,
        "status": project_data.status,
        "budget": project_data.budget,
        "created_at": now,
        "updated_at": now
    }
    
    await db.projects.insert_one(project_doc)
    
    return ProjectResponse(**{k: v for k, v in project_doc.items() if k != "_id"})

@api_router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(current_user: dict = Depends(get_current_user)):
    projects = await db.projects.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).to_list(100)
    return projects

@api_router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, current_user: dict = Depends(get_current_user)):
    project = await db.projects.find_one(
        {"id": project_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return project

@api_router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: dict = Depends(get_current_user)
):
    project = await db.projects.find_one(
        {"id": project_id, "user_id": current_user["id"]}
    )
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    update_data = {k: v for k, v in project_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.projects.update_one(
        {"id": project_id},
        {"$set": update_data}
    )
    
    updated = await db.projects.find_one({"id": project_id}, {"_id": 0})
    return updated

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.projects.delete_one(
        {"id": project_id, "user_id": current_user["id"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return {"message": "Projeto eliminado com sucesso"}


# ==================== MESSAGE ROUTES ====================

@api_router.post("/messages", response_model=MessageResponse)
async def create_message(
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    message_id = str(uuid.uuid4())
    
    message_doc = {
        "id": message_id,
        "user_id": current_user["id"],
        "subject": message_data.subject,
        "content": message_data.content,
        "is_read": False,
        "admin_reply": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.messages.insert_one(message_doc)
    
    return MessageResponse(**{k: v for k, v in message_doc.items() if k != "_id"})

@api_router.get("/messages", response_model=List[MessageResponse])
async def get_messages(current_user: dict = Depends(get_current_user)):
    messages = await db.messages.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return messages


# ==================== CONTACT ROUTES (PUBLIC) ====================

@api_router.post("/contact", response_model=ContactResponse)
async def submit_contact(contact_data: ContactCreate):
    contact_id = str(uuid.uuid4())
    
    contact_doc = {
        "id": contact_id,
        "name": contact_data.name,
        "email": contact_data.email,
        "phone": contact_data.phone,
        "message": contact_data.message,
        "service_type": contact_data.service_type,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.contacts.insert_one(contact_doc)
    
    return ContactResponse(**{k: v for k, v in contact_doc.items() if k != "_id"})


# ==================== PORTFOLIO ROUTES (PUBLIC) ====================

@api_router.get("/portfolio", response_model=List[PortfolioItem])
async def get_portfolio():
    # Return sample portfolio items
    portfolio_items = [
        {
            "id": "1",
            "title": "E-Commerce Platform",
            "description": "Plataforma completa de e-commerce com pagamentos integrados",
            "image_url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600",
            "category": "web",
            "technologies": ["React", "Node.js", "MongoDB", "Stripe"],
            "link": None
        },
        {
            "id": "2",
            "title": "App de Fitness",
            "description": "Aplicação móvel para tracking de exercícios e nutrição",
            "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600",
            "category": "mobile",
            "technologies": ["React Native", "Firebase", "HealthKit"],
            "link": None
        },
        {
            "id": "3",
            "title": "Sistema de Gestão",
            "description": "Dashboard completo para gestão empresarial",
            "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600",
            "category": "web",
            "technologies": ["Vue.js", "Python", "PostgreSQL"],
            "link": None
        },
        {
            "id": "4",
            "title": "App de Delivery",
            "description": "Aplicação de entregas com tracking em tempo real",
            "image_url": "https://images.unsplash.com/photo-1526367790999-0150786686a2?w=600",
            "category": "mobile",
            "technologies": ["Flutter", "Google Maps", "Node.js"],
            "link": None
        }
    ]
    return portfolio_items


# ==================== STATS ROUTES ====================

@api_router.get("/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    total_projects = await db.projects.count_documents({"user_id": current_user["id"]})
    pending = await db.projects.count_documents({"user_id": current_user["id"], "status": "pending"})
    in_progress = await db.projects.count_documents({"user_id": current_user["id"], "status": "in_progress"})
    completed = await db.projects.count_documents({"user_id": current_user["id"], "status": "completed"})
    unread_messages = await db.messages.count_documents({"user_id": current_user["id"], "is_read": False})
    
    return {
        "total_projects": total_projects,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "unread_messages": unread_messages
    }


# ==================== ROOT ROUTE ====================

@api_router.get("/")
async def root():
    return {"message": "Andre Dev API - Bem-vindo!"}


# ==================== ADMIN ROUTES ====================

@api_router.post("/admin/setup", response_model=TokenResponse)
async def setup_admin(admin_data: AdminCreate):
    """Create initial admin account (only works if no admin exists)"""
    existing_admin = await db.users.find_one({"role": "admin"})
    if existing_admin:
        raise HTTPException(status_code=400, detail="Já existe um administrador")
    
    admin_id = str(uuid.uuid4())
    admin_doc = {
        "id": admin_id,
        "name": admin_data.name,
        "email": admin_data.email,
        "password": hash_password(admin_data.password),
        "company": None,
        "role": "admin",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(admin_doc)
    token = create_token(admin_id)
    
    user_response = UserResponse(
        id=admin_id,
        name=admin_data.name,
        email=admin_data.email,
        company=None,
        role="admin",
        created_at=admin_doc["created_at"]
    )
    
    return TokenResponse(access_token=token, user=user_response)

@api_router.get("/admin/check")
async def check_admin_exists():
    """Check if admin account exists"""
    existing_admin = await db.users.find_one({"role": "admin"}, {"_id": 0, "password": 0})
    return {"admin_exists": existing_admin is not None}

@api_router.get("/admin/contacts")
async def get_all_contacts(admin: dict = Depends(get_admin_user)):
    """Get all contact form submissions"""
    contacts = await db.contacts.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return contacts

@api_router.delete("/admin/contacts/{contact_id}")
async def delete_contact(contact_id: str, admin: dict = Depends(get_admin_user)):
    """Delete a contact submission"""
    result = await db.contacts.delete_one({"id": contact_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contacto não encontrado")
    return {"message": "Contacto eliminado"}

@api_router.get("/admin/users")
async def get_all_users(admin: dict = Depends(get_admin_user)):
    """Get all registered users"""
    users = await db.users.find({"role": "client"}, {"_id": 0, "password": 0}).sort("created_at", -1).to_list(100)
    return users

@api_router.delete("/admin/users/{user_id}")
async def delete_user(user_id: str, admin: dict = Depends(get_admin_user)):
    """Delete a user and their projects/messages"""
    user = await db.users.find_one({"id": user_id, "role": "client"})
    if not user:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado")
    
    await db.users.delete_one({"id": user_id})
    await db.projects.delete_many({"user_id": user_id})
    await db.messages.delete_many({"user_id": user_id})
    
    return {"message": "Utilizador eliminado"}

@api_router.get("/admin/projects")
async def get_all_projects(admin: dict = Depends(get_admin_user)):
    """Get all projects from all users"""
    projects = await db.projects.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    # Add user info to each project
    for project in projects:
        user = await db.users.find_one({"id": project["user_id"]}, {"_id": 0, "password": 0})
        project["user"] = {"name": user["name"], "email": user["email"]} if user else None
    return projects

@api_router.put("/admin/projects/{project_id}/status")
async def update_project_status(
    project_id: str,
    status: str,
    admin: dict = Depends(get_admin_user)
):
    """Update project status"""
    if status not in ["pending", "in_progress", "completed"]:
        raise HTTPException(status_code=400, detail="Estado inválido")
    
    result = await db.projects.update_one(
        {"id": project_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    return {"message": "Estado atualizado"}

@api_router.get("/admin/messages")
async def get_all_messages(admin: dict = Depends(get_admin_user)):
    """Get all messages from all users"""
    messages = await db.messages.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    # Add user info
    for message in messages:
        user = await db.users.find_one({"id": message["user_id"]}, {"_id": 0, "password": 0})
        message["user"] = {"name": user["name"], "email": user["email"]} if user else None
    return messages

@api_router.put("/admin/messages/{message_id}/reply")
async def reply_to_message(
    message_id: str,
    reply: str,
    admin: dict = Depends(get_admin_user)
):
    """Reply to a user message"""
    result = await db.messages.update_one(
        {"id": message_id},
        {"$set": {"admin_reply": reply, "is_read": True}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    
    return {"message": "Resposta enviada"}

@api_router.get("/admin/stats")
async def get_admin_stats(admin: dict = Depends(get_admin_user)):
    """Get overall statistics"""
    total_users = await db.users.count_documents({"role": "client"})
    total_contacts = await db.contacts.count_documents({})
    total_projects = await db.projects.count_documents({})
    pending_projects = await db.projects.count_documents({"status": "pending"})
    in_progress_projects = await db.projects.count_documents({"status": "in_progress"})
    completed_projects = await db.projects.count_documents({"status": "completed"})
    total_messages = await db.messages.count_documents({})
    unread_messages = await db.messages.count_documents({"is_read": False})
    
    return {
        "total_users": total_users,
        "total_contacts": total_contacts,
        "total_projects": total_projects,
        "pending_projects": pending_projects,
        "in_progress_projects": in_progress_projects,
        "completed_projects": completed_projects,
        "total_messages": total_messages,
        "unread_messages": unread_messages
    }


# ==================== CMS ROUTES ====================

# Default content for the site
DEFAULT_HERO = {
    "tagline": "Agência de Desenvolvimento",
    "title": "Criamos o seu",
    "highlight": "futuro digital",
    "description": "Desenvolvemos websites e aplicações móveis que transformam ideias em experiências digitais extraordinárias. Android, iOS e Web.",
    "cta_text": "Começar Projeto",
    "stats": [
        {"value": "50+", "label": "Projetos Entregues"},
        {"value": "100%", "label": "Clientes Satisfeitos"},
        {"value": "5+", "label": "Anos de Experiência"}
    ]
}

DEFAULT_SERVICES = [
    {
        "id": "1",
        "icon": "Monitor",
        "title": "Desenvolvimento Web",
        "description": "Websites modernos, responsivos e otimizados para SEO. Desde landing pages a plataformas complexas.",
        "features": ["React & Vue.js", "E-commerce", "Dashboards", "APIs RESTful"]
    },
    {
        "id": "2",
        "icon": "Smartphone",
        "title": "Aplicações Android",
        "description": "Apps nativas e híbridas para Android com performance excepcional e design intuitivo.",
        "features": ["Kotlin & Java", "Material Design", "Play Store", "Firebase"]
    },
    {
        "id": "3",
        "icon": "Code2",
        "title": "Aplicações iOS",
        "description": "Desenvolvimento de apps para iPhone e iPad com a qualidade que a Apple exige.",
        "features": ["Swift & SwiftUI", "Human Interface", "App Store", "Core Data"]
    },
    {
        "id": "4",
        "icon": "Rocket",
        "title": "Soluções Completas",
        "description": "Do conceito ao lançamento, acompanhamos todo o processo de desenvolvimento do seu projeto.",
        "features": ["UX/UI Design", "Backend", "DevOps", "Manutenção"]
    }
]

DEFAULT_PORTFOLIO = [
    {
        "id": "1",
        "title": "E-Commerce Platform",
        "description": "Plataforma completa de e-commerce com pagamentos integrados",
        "image_url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600",
        "category": "Web",
        "technologies": ["React", "Node.js", "MongoDB"],
        "link": None
    },
    {
        "id": "2",
        "title": "App de Fitness",
        "description": "Aplicação móvel para tracking de exercícios e nutrição",
        "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600",
        "category": "Mobile",
        "technologies": ["React Native", "Firebase"],
        "link": None
    },
    {
        "id": "3",
        "title": "Sistema de Gestão",
        "description": "Dashboard completo para gestão empresarial",
        "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600",
        "category": "Web",
        "technologies": ["Vue.js", "Python"],
        "link": None
    },
    {
        "id": "4",
        "title": "App de Delivery",
        "description": "Aplicação de entregas com tracking em tempo real",
        "image_url": "https://images.unsplash.com/photo-1526367790999-0150786686a2?w=600",
        "category": "Mobile",
        "technologies": ["Flutter", "Node.js"],
        "link": None
    }
]

DEFAULT_TESTIMONIALS = [
    {
        "id": "1",
        "name": "Maria Santos",
        "role": "CEO, TechStart",
        "image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200",
        "text": "A Andre Dev transformou completamente a nossa presença digital. O website que desenvolveram superou todas as expectativas."
    },
    {
        "id": "2",
        "name": "João Ferreira",
        "role": "Fundador, AppSolutions",
        "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200",
        "text": "Profissionalismo e qualidade excecional. A app que criaram para nós tem recebido feedback incrível dos utilizadores."
    }
]

DEFAULT_CONTACT_INFO = {
    "email": "contacto@andredev.pt",
    "phone": "+351 912 345 678",
    "location": "Lisboa, Portugal"
}

@api_router.get("/content")
async def get_site_content():
    """Get all site content (public)"""
    content = await db.site_content.find_one({"type": "main"}, {"_id": 0})
    
    if not content:
        return {
            "hero": DEFAULT_HERO,
            "services": DEFAULT_SERVICES,
            "portfolio": DEFAULT_PORTFOLIO,
            "testimonials": DEFAULT_TESTIMONIALS,
            "contact_info": DEFAULT_CONTACT_INFO
        }
    
    return {
        "hero": content.get("hero", DEFAULT_HERO),
        "services": content.get("services", DEFAULT_SERVICES),
        "portfolio": content.get("portfolio", DEFAULT_PORTFOLIO),
        "testimonials": content.get("testimonials", DEFAULT_TESTIMONIALS),
        "contact_info": content.get("contact_info", DEFAULT_CONTACT_INFO)
    }

@api_router.get("/admin/content")
async def get_admin_content(admin: dict = Depends(get_admin_user)):
    """Get site content for editing"""
    content = await db.site_content.find_one({"type": "main"}, {"_id": 0})
    
    if not content:
        return {
            "hero": DEFAULT_HERO,
            "services": DEFAULT_SERVICES,
            "portfolio": DEFAULT_PORTFOLIO,
            "testimonials": DEFAULT_TESTIMONIALS,
            "contact_info": DEFAULT_CONTACT_INFO
        }
    
    return {
        "hero": content.get("hero", DEFAULT_HERO),
        "services": content.get("services", DEFAULT_SERVICES),
        "portfolio": content.get("portfolio", DEFAULT_PORTFOLIO),
        "testimonials": content.get("testimonials", DEFAULT_TESTIMONIALS),
        "contact_info": content.get("contact_info", DEFAULT_CONTACT_INFO)
    }

@api_router.put("/admin/content/hero")
async def update_hero(hero: HeroContent, admin: dict = Depends(get_admin_user)):
    """Update hero section"""
    await db.site_content.update_one(
        {"type": "main"},
        {"$set": {"hero": hero.model_dump(), "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "Hero atualizado com sucesso"}

@api_router.put("/admin/content/services")
async def update_services(services: List[ServiceItem], admin: dict = Depends(get_admin_user)):
    """Update services section"""
    services_data = []
    for i, service in enumerate(services):
        s = service.model_dump()
        if not s.get("id"):
            s["id"] = str(i + 1)
        services_data.append(s)
    
    await db.site_content.update_one(
        {"type": "main"},
        {"$set": {"services": services_data, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "Serviços atualizados com sucesso"}

@api_router.put("/admin/content/portfolio")
async def update_portfolio(portfolio: List[PortfolioItemCreate], admin: dict = Depends(get_admin_user)):
    """Update portfolio section"""
    portfolio_data = []
    for i, item in enumerate(portfolio):
        p = item.model_dump()
        p["id"] = str(i + 1)
        portfolio_data.append(p)
    
    await db.site_content.update_one(
        {"type": "main"},
        {"$set": {"portfolio": portfolio_data, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "Portfolio atualizado com sucesso"}

@api_router.put("/admin/content/testimonials")
async def update_testimonials(testimonials: List[TestimonialItem], admin: dict = Depends(get_admin_user)):
    """Update testimonials section"""
    testimonials_data = []
    for i, item in enumerate(testimonials):
        t = item.model_dump()
        if not t.get("id"):
            t["id"] = str(i + 1)
        testimonials_data.append(t)
    
    await db.site_content.update_one(
        {"type": "main"},
        {"$set": {"testimonials": testimonials_data, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "Testemunhos atualizados com sucesso"}

@api_router.put("/admin/content/contact-info")
async def update_contact_info(contact_info: ContactInfo, admin: dict = Depends(get_admin_user)):
    """Update contact info"""
    await db.site_content.update_one(
        {"type": "main"},
        {"$set": {"contact_info": contact_info.model_dump(), "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "Informação de contacto atualizada com sucesso"}


# Include the router
app.include_router(api_router)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
