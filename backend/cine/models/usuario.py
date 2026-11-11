import hashlib
import hmac
import secrets
import uuid
from abc import ABC, abstractmethod


# Hash de contraseñas con scrypt (biblioteca estándar). Formato guardado:
# scrypt$n$r$p$sal_hex$hash_hex. Cada contraseña lleva su propia sal aleatoria.
_N, _R, _P = 2**14, 8, 1


def hash_password(password: str) -> str:
    sal = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=sal, n=_N, r=_R, p=_P, dklen=32)
    return f'scrypt${_N}${_R}${_P}${sal.hex()}${digest.hex()}'


def verify_password(password: str, guardado: str) -> bool:
    try:
        algoritmo, n, r, p, sal_hex, digest_hex = guardado.split('$')
        if algoritmo != 'scrypt':
            return False
        calculado = hashlib.scrypt(
            password.encode(), salt=bytes.fromhex(sal_hex),
            n=int(n), r=int(r), p=int(p), dklen=len(digest_hex) // 2,
        )
    except (ValueError, TypeError):
        return False
    # Comparación en tiempo constante para no dar pistas por tiempo de respuesta
    return hmac.compare_digest(calculado.hex(), digest_hex)


class Usuario(ABC):
    """Clase base abstracta: no se puede instanciar, cada subclase indica su rol."""

    def __init__(self, nombre: str, email: str) -> None:
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.email: str = email

    @property
    @abstractmethod
    def rol(self) -> str:
        """Rol del usuario: 'cliente' o 'admin'."""

    def __str__(self) -> str:
        return f'{self.nombre} <{self.email}> ({self.rol})'


class Cliente(Usuario):
    """Compra entradas como invitado; se identifica por su email."""

    @property
    def rol(self) -> str:
        return 'cliente'

    def __str__(self) -> str:
        return f'El email de {self.nombre} es : {self.email}'


class Administrador(Usuario):
    """Gestiona películas y sesiones tras iniciar sesión. Solo guarda el hash de la contraseña."""

    def __init__(self, nombre: str, email: str, password: str) -> None:
        super().__init__(nombre, email)
        self.password_hash: str = hash_password(password)

    @property
    def rol(self) -> str:
        return 'admin'

    def verificar_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)
