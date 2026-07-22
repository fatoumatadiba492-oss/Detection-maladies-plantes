"""
Authentification — hash des mots de passe (bcrypt) + JWT + décorateurs de rôle.
Modèle : Utilisateur (idUtilisateur, nom, prenom, email, motDePasse, role)
         role ∈ {"administrateur", "maraicher"}
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, g

JWT_SECRET     = os.getenv('JWT_SECRET', 'dev-secret-a-changer-en-production')
JWT_ALGORITHM  = 'HS256'
JWT_EXPIRES_H  = 24


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except (ValueError, AttributeError):
        return False


def generate_token(user: dict) -> str:
    """user doit contenir : idUtilisateur, email, role."""
    payload = {
        'idUtilisateur': user['idUtilisateur'],
        'email':         user['email'],
        'role':          user['role'],
        'exp':           datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRES_H),
        'iat':           datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str):
    """Retourne le payload décodé, ou None si le token est invalide/expiré."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


def _extract_token():
    header = request.headers.get('Authorization', '')
    if header.startswith('Bearer '):
        return header[7:].strip()
    return None


def get_current_user():
    """Décode le token si présent, sans lever d'erreur. Utilisé pour l'auth optionnelle."""
    token = _extract_token()
    if not token:
        return None
    return decode_token(token)


def login_required(f):
    """Exige un token JWT valide. Injecte l'utilisateur décodé dans flask.g.current_user."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({'error': 'Authentification requise'}), 401
        payload = decode_token(token)
        if payload is None:
            return jsonify({'error': 'Token invalide ou expiré'}), 401
        g.current_user = payload
        return f(*args, **kwargs)
    return wrapper


def role_required(*roles):
    """Exige un token JWT valide ET un rôle parmi ceux fournis."""
    def decorator(f):
        @wraps(f)
        @login_required
        def wrapper(*args, **kwargs):
            if g.current_user.get('role') not in roles:
                return jsonify({'error': 'Accès refusé — rôle insuffisant'}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator
