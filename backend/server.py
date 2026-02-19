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

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    email: str
    company: Optional[str] = None
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
    budget: Optional[str] = None

class ProjectResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    name: str
    description: str
    project_type: str
    status: str
    budget: Optional[str] = None
    created_at: str
    updated_at: str

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_type: Optional[str] = None
    status: Optional[str] = None
    budget: Optional[str] = None

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
